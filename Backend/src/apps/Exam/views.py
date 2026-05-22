from django.utils import timezone
from rest_framework.views import APIView

from src.apps.Paper.models import Paper
from src.apps.Score.models import Score
from src.utils.response_utils import ResponseCode, api_response

from .models import Exam


class ExamBaseView(APIView):
    def post(self, request):
        return api_response(ResponseCode.METHOD_NOT_ALLOWED, "暂未实现")

    def delete(self, _, **kwargs):
        return api_response(ResponseCode.METHOD_NOT_ALLOWED, "暂未实现")

    def put(self, request, **kwargs):
        return api_response(ResponseCode.METHOD_NOT_ALLOWED, "暂未实现")

    def get(self, request):
        return api_response(ResponseCode.METHOD_NOT_ALLOWED, "暂未实现")


class ExamPublishView(APIView):
    def post(self, _, **kwargs):
        return api_response(ResponseCode.METHOD_NOT_ALLOWED, "暂未实现")

    def delete(self, _, **kwargs):
        return api_response(ResponseCode.METHOD_NOT_ALLOWED, "暂未实现")


class ExamAttendView(APIView):
    def get(self, request):
        return api_response(ResponseCode.METHOD_NOT_ALLOWED, "暂未实现")


class ExamScheduleView(APIView):
    def get(self, request):
        return api_response(ResponseCode.METHOD_NOT_ALLOWED, "暂未实现")


class ExamDetailView(APIView):
    def get(self, request):
        return api_response(ResponseCode.METHOD_NOT_ALLOWED, "暂未实现")


class ExamEnterView(APIView):
    def post(self, request):
        exam_id = request.data.get("exam_id")
        student_id = request.data.get("student_id")

        if not exam_id or not student_id:
            return api_response(ResponseCode.BAD_REQUEST, "exam_id 和 student_id 为必填项")

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

