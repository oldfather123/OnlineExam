from django.core.paginator import Paginator
from django.utils import timezone
from rest_framework.views import APIView

from src.apps.Paper.models import Paper
from src.apps.Score.models import Score
from src.utils.response_utils import ResponseCode, api_response

from .models import Exam
from .serializers import ExamEnterRequestSerializer, ExamSerializer


def attach_paper_titles(rows):
    paper_ids = [item["paper_id"] for item in rows]
    paper_map = {paper.id: paper for paper in Paper.objects.filter(id__in=paper_ids)}
    for item in rows:
        paper = paper_map.get(item["paper_id"])
        item["paper_title"] = paper.title if paper else ""
    return rows


class ExamBaseView(APIView):
    def post(self, request):
        paper_id = request.data.get("paper_id")
        if not Paper.objects.filter(id=paper_id, is_published=True).exists():
            return api_response(ResponseCode.BAD_REQUEST, "考试关联试卷不存在或未发布")

        serializer = ExamSerializer(data=request.data)
        if not serializer.is_valid():
            return api_response(ResponseCode.BAD_REQUEST, "创建失败", serializer.errors)
        if serializer.validated_data["start_time"] >= serializer.validated_data["end_time"]:
            return api_response(ResponseCode.BAD_REQUEST, "考试开始时间必须早于结束时间")
        serializer.save()
        return api_response(ResponseCode.SUCCESS, "创建成功", serializer.data)

    def delete(self, _, **kwargs):
        exam = Exam.objects.filter(id=kwargs.get("id"), is_deleted=False).first()
        if exam is None:
            return api_response(ResponseCode.NOT_FOUND, "考试不存在")
        exam.is_deleted = True
        exam.is_published = False
        exam.updated_at = timezone.now()
        exam.save(update_fields=["is_deleted", "is_published", "updated_at"])
        return api_response(ResponseCode.SUCCESS, "删除成功")

    def put(self, request, **kwargs):
        exam = Exam.objects.filter(id=kwargs.get("id"), is_deleted=False).first()
        if exam is None:
            return api_response(ResponseCode.NOT_FOUND, "考试不存在")

        payload = request.data.copy()
        for key in ["id", "created_at", "updated_at", "is_deleted"]:
            payload.pop(key, None)

        paper_id = payload.get("paper_id", exam.paper_id)
        if not Paper.objects.filter(id=paper_id, is_published=True).exists():
            return api_response(ResponseCode.BAD_REQUEST, "考试关联试卷不存在或未发布")

        serializer = ExamSerializer(exam, data=payload, partial=True)
        if not serializer.is_valid():
            return api_response(ResponseCode.BAD_REQUEST, "编辑失败", serializer.errors)
        start_time = serializer.validated_data.get("start_time", exam.start_time)
        end_time = serializer.validated_data.get("end_time", exam.end_time)
        if start_time >= end_time:
            return api_response(ResponseCode.BAD_REQUEST, "考试开始时间必须早于结束时间")
        serializer.save()
        return api_response(ResponseCode.SUCCESS, "编辑成功", serializer.data)

    def get(self, request, **kwargs):
        exam_id = kwargs.get("id")
        if exam_id:
            exam = Exam.objects.filter(id=exam_id, is_deleted=False).first()
            if exam is None:
                return api_response(ResponseCode.NOT_FOUND, "考试不存在")
            data = ExamSerializer(exam).data
            return api_response(ResponseCode.SUCCESS, "查询考试详情成功", attach_paper_titles([data])[0])

        queryset = Exam.objects.filter(is_deleted=False).order_by("-created_at")
        title = request.query_params.get("title")
        published = request.query_params.get("is_published")
        if title:
            queryset = queryset.filter(title__icontains=title)
        if published in ["true", "false"]:
            queryset = queryset.filter(is_published=(published == "true"))

        page = max(int(request.query_params.get("currentPage", 1)), 1)
        page_size = max(int(request.query_params.get("pageSize", 50)), 1)
        paginator = Paginator(queryset, page_size)
        page_obj = paginator.get_page(page)
        rows = attach_paper_titles(ExamSerializer(page_obj.object_list, many=True).data)
        return api_response(ResponseCode.SUCCESS, "查询成功", {"total": paginator.count, "data": rows})


class ExamPublishView(APIView):
    def post(self, _, **kwargs):
        exam = Exam.objects.filter(id=kwargs.get("id"), is_deleted=False).first()
        if exam is None:
            return api_response(ResponseCode.NOT_FOUND, "考试不存在")
        if not Paper.objects.filter(id=exam.paper_id, is_published=True).exists():
            return api_response(ResponseCode.BAD_REQUEST, "考试关联试卷不存在或未发布")
        exam.is_published = True
        exam.updated_at = timezone.now()
        exam.save(update_fields=["is_published", "updated_at"])
        return api_response(ResponseCode.SUCCESS, "考试发布成功")

    def delete(self, _, **kwargs):
        exam = Exam.objects.filter(id=kwargs.get("id"), is_deleted=False).first()
        if exam is None:
            return api_response(ResponseCode.NOT_FOUND, "考试不存在")
        exam.is_published = False
        exam.updated_at = timezone.now()
        exam.save(update_fields=["is_published", "updated_at"])
        return api_response(ResponseCode.SUCCESS, "取消发布成功")


class ExamAttendView(APIView):
    def get(self, request):
        now = timezone.now()
        queryset = Exam.objects.filter(is_deleted=False, is_published=True, end_time__gte=now).order_by("start_time")
        rows = attach_paper_titles(ExamSerializer(queryset, many=True).data)
        return api_response(ResponseCode.SUCCESS, "查询可参加考试成功", {"total": len(rows), "data": rows})


class ExamScheduleView(APIView):
    def get(self, request):
        now = timezone.now()
        queryset = Exam.objects.filter(is_deleted=False, is_published=True).order_by("start_time")
        status = request.query_params.get("status")
        if status == "pending":
            queryset = queryset.filter(start_time__gt=now)
        elif status == "running":
            queryset = queryset.filter(start_time__lte=now, end_time__gte=now)
        elif status == "ended":
            queryset = queryset.filter(end_time__lt=now)
        return api_response(ResponseCode.SUCCESS, "查询考试安排成功", ExamSerializer(queryset, many=True).data)


class ExamDetailView(APIView):
    def get(self, request):
        exam_id = request.query_params.get("exam_id")
        if not exam_id:
            return api_response(ResponseCode.BAD_REQUEST, "exam_id 为必填项")
        exam = Exam.objects.filter(id=exam_id, is_deleted=False).first()
        if exam is None:
            return api_response(ResponseCode.NOT_FOUND, "考试不存在")
        data = ExamSerializer(exam).data
        paper = Paper.objects.filter(id=exam.paper_id).first()
        data["paper"] = {"paper_id": paper.id, "title": paper.title} if paper else None
        return api_response(ResponseCode.SUCCESS, "查询考试详情成功", data)


class ExamEnterView(APIView):
    def post(self, request):
        serializer = ExamEnterRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return api_response(ResponseCode.BAD_REQUEST, "参数校验失败", serializer.errors)
        exam_id = serializer.validated_data["exam_id"]
        student_id = serializer.validated_data["student_id"]

        exam = Exam.objects.filter(id=exam_id, is_deleted=False, is_published=True).first()
        if exam is None:
            return api_response(ResponseCode.NOT_FOUND, "考试不存在或未发布")

        now = timezone.now()
        if now < exam.start_time:
            return api_response(ResponseCode.BAD_REQUEST, "考试未开始")
        if now > exam.end_time:
            return api_response(ResponseCode.BAD_REQUEST, "考试已结束")

        paper_exists = Paper.objects.filter(id=exam.paper_id, is_published=True).exists()
        if not paper_exists:
            return api_response(ResponseCode.BAD_REQUEST, "考试关联试卷不存在或未发布")

        score, created = Score.objects.get_or_create(
            exam_id=exam_id,
            student_id=student_id,
            defaults={"start_time": now},
        )
        if not created and score.start_time is None:
            score.start_time = now
            score.save(update_fields=["start_time", "updated_at"])

        return api_response(
            ResponseCode.SUCCESS,
            "进入考试成功",
            {
                "exam_id": exam_id,
                "student_id": student_id,
                "exam_result_id": score.id,
                "start_time": score.start_time,
                "paper_id": exam.paper_id,
            },
        )
