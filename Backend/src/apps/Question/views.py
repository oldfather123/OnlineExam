import json
import random

from django.core.paginator import Paginator
from django.db.models import Q
from rest_framework.views import APIView

from src.utils.response_utils import ResponseCode, api_response

from .models import ErrorArchive, Questions
from .serializers import ErrorArchiveSerializer, QuestionSerializer


class QuestionBaseView(APIView):
    def post(self, request):
        serializer = QuestionSerializer(data=request.data)
        if not serializer.is_valid():
            return api_response(ResponseCode.BAD_REQUEST, "创建失败", serializer.errors)
        serializer.save()
        return api_response(ResponseCode.SUCCESS, "创建成功", serializer.data)

    def put(self, request, **kwargs):
        question = Questions.objects.filter(id=kwargs.get("id")).first()
        if question is None:
            return api_response(ResponseCode.NOT_FOUND, "编辑失败!试题不存在")

        payload = request.data.copy()
        for key in ["id", "created_at", "updated_at"]:
            payload.pop(key, None)

        serializer = QuestionSerializer(question, data=payload, partial=True)
        if not serializer.is_valid():
            return api_response(ResponseCode.BAD_REQUEST, "编辑失败", serializer.errors)
        serializer.save()
        return api_response(ResponseCode.SUCCESS, "编辑成功", serializer.data)

    def delete(self, _, **kwargs):
        question = Questions.objects.filter(id=kwargs.get("id")).first()
        if question is None:
            return api_response(ResponseCode.NOT_FOUND, "删除失败!试题不存在")
        question.delete()
        return api_response(ResponseCode.SUCCESS, "删除成功")

    def get(self, request, **kwargs):
        question_id = kwargs.get("id")
        if question_id:
            question = Questions.objects.filter(id=question_id).first()
            if question is None:
                return api_response(ResponseCode.NOT_FOUND, "试题不存在")
            return api_response(ResponseCode.SUCCESS, "查询试题详情成功", QuestionSerializer(question).data)

        topic = request.query_params.get("topic")
        q_type = request.query_params.get("type")
        queryset = Questions.objects.all().order_by("-created_at")

        if topic:
            queryset = queryset.filter(topic__icontains=topic)
        if q_type:
            queryset = queryset.filter(type=q_type)

        page = max(int(request.query_params.get("currentPage", 1)), 1)
        page_size = max(int(request.query_params.get("pageSize", 50)), 1)
        paginator = Paginator(queryset, page_size)
        page_obj = paginator.get_page(page)
        data = QuestionSerializer(page_obj.object_list, many=True).data
        return api_response(ResponseCode.SUCCESS, "查询成功", {"total": paginator.count, "data": data})


class QuestionsPaperView(APIView):
    def get(self, request):
        q_type = request.query_params.get("type")
        topic = request.query_params.get("topic")

        queryset = Questions.objects.all().order_by("created_at")
        if q_type:
            queryset = queryset.filter(type=q_type)
        if topic:
            queryset = queryset.filter(topic__icontains=topic)

        return api_response(ResponseCode.SUCCESS, "获取题库试题成功", QuestionSerializer(queryset, many=True).data)


class AgentSelectQuestionsView(APIView):
    def get(self, request):
        random_type = request.query_params.get("randomQuestionType") or request.query_params.get("type")
        random_num = request.query_params.get("randomNumber") or request.query_params.get("count") or "5"

        queryset = Questions.objects.all()
        if random_type in ["select", "judge"]:
            queryset = queryset.filter(type=random_type)

        question_data = QuestionSerializer(queryset, many=True).data

        try:
            n = int(random_num)
            if n <= 0 or n > len(question_data):
                return api_response(ResponseCode.BAD_REQUEST, "参数错误！随机数量不能大于可选题总数或小于等于0")
        except Exception:
            return api_response(ResponseCode.BAD_REQUEST, "参数错误！请输入正确的参数")

        return api_response(ResponseCode.SUCCESS, "智能选题成功", random.sample(list(question_data), n))


class ErrorArchiveView(APIView):
    def post(self, request):
        collector = request.data.get("collector")
        question_id = request.data.get("question_id")
        if not collector or not question_id:
            return api_response(ResponseCode.BAD_REQUEST, "collector 和 question_id 为必填项")

        exists = ErrorArchive.objects.filter(collector=collector, question_id=question_id).exists()
        if exists:
            return api_response(ResponseCode.SUCCESS, "加入错题集失败！已有错题记录，无需再次收藏")

        serializer = ErrorArchiveSerializer(data=request.data)
        if not serializer.is_valid():
            return api_response(ResponseCode.BAD_REQUEST, "收藏错题失败", serializer.errors)
        serializer.save()
        return api_response(ResponseCode.SUCCESS, "收藏错题成功", serializer.data)

    def delete(self, request):
        collector = request.data.get("collector")
        question_id = request.data.get("question_id")
        if not collector or not question_id:
            return api_response(ResponseCode.BAD_REQUEST, "collector 和 question_id 为必填项")

        deleted, _ = ErrorArchive.objects.filter(collector=collector, question_id=question_id).delete()
        if deleted == 0:
            return api_response(ResponseCode.SUCCESS, "取消收藏错题失败！没有收藏记录")
        return api_response(ResponseCode.SUCCESS, "取消收藏错题成功")

    def get(self, request, **kwargs):
        archive_id = kwargs.get("id")
        if archive_id:
            archive = ErrorArchive.objects.filter(id=archive_id).first()
            if archive is None:
                return api_response(ResponseCode.NOT_FOUND, "错题记录不存在")
            return api_response(ResponseCode.SUCCESS, "查询成功", ErrorArchiveSerializer(archive).data)

        collector = request.query_params.get("collector")
        if not collector:
            return api_response(ResponseCode.BAD_REQUEST, "collector 为必填项")

        topic = request.query_params.get("topic")
        queryset = ErrorArchive.objects.filter(collector=collector).order_by("-created_at")
        if topic:
            question_ids = list(Questions.objects.filter(topic__icontains=topic).values_list("id", flat=True))
            queryset = queryset.filter(question_id__in=question_ids)

        page = max(int(request.query_params.get("currentPage", 1)), 1)
        page_size = max(int(request.query_params.get("pageSize", 50)), 1)
        paginator = Paginator(queryset, page_size)
        page_obj = paginator.get_page(page)
        data = ErrorArchiveSerializer(page_obj.object_list, many=True).data
        return api_response(ResponseCode.SUCCESS, "查询成功", {"total": paginator.count, "data": data})

    def put(self, request, **kwargs):
        archive = ErrorArchive.objects.filter(id=kwargs.get("id")).first()
        if archive is None:
            return api_response(ResponseCode.NOT_FOUND, "编辑失败!收藏记录不存在")

        serializer = ErrorArchiveSerializer(archive, data=request.data, partial=True)
        if not serializer.is_valid():
            return api_response(ResponseCode.BAD_REQUEST, "编辑失败", serializer.errors)
        serializer.save()
        return api_response(ResponseCode.SUCCESS, "编辑成功", serializer.data)
