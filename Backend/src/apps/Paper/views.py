import json

from rest_framework.views import APIView

from src.apps.Question.models import Questions
from src.utils.response_utils import ResponseCode, api_response

from .models import Paper, PaperModule, PaperQuestions


class PaperBaseView(APIView):
    def post(self, request):
        return api_response(ResponseCode.METHOD_NOT_ALLOWED, "暂未实现")

    def delete(self, _, **kwargs):
        return api_response(ResponseCode.METHOD_NOT_ALLOWED, "暂未实现")

    def put(self, request, **kwargs):
        return api_response(ResponseCode.METHOD_NOT_ALLOWED, "暂未实现")

    def get(self, request, **kwargs):
        return api_response(ResponseCode.METHOD_NOT_ALLOWED, "暂未实现")


class PaperModuleView(APIView):
    def post(self, request):
        return api_response(ResponseCode.METHOD_NOT_ALLOWED, "暂未实现")

    def delete(self, request):
        return api_response(ResponseCode.METHOD_NOT_ALLOWED, "暂未实现")

    def put(self, request, **kwargs):
        return api_response(ResponseCode.METHOD_NOT_ALLOWED, "暂未实现")

    def get(self, _, **kwargs):
        return api_response(ResponseCode.METHOD_NOT_ALLOWED, "暂未实现")


class PaperQuestionsView(APIView):
    def post(self, request):
        return api_response(ResponseCode.METHOD_NOT_ALLOWED, "暂未实现")

    def delete(self, _, **kwargs):
        return api_response(ResponseCode.METHOD_NOT_ALLOWED, "暂未实现")

    def put(self, request, **kwargs):
        return api_response(ResponseCode.METHOD_NOT_ALLOWED, "暂未实现")

    def get(self, _, **kwargs):
        return api_response(ResponseCode.METHOD_NOT_ALLOWED, "暂未实现")


class PaperPublishView(APIView):
    def post(self, request):
        return api_response(ResponseCode.METHOD_NOT_ALLOWED, "暂未实现")

    def delete(self, request):
        return api_response(ResponseCode.METHOD_NOT_ALLOWED, "暂未实现")


class PaperForSelectorView(APIView):
    def get(self, request):
        return api_response(ResponseCode.METHOD_NOT_ALLOWED, "暂未实现")


class PaperDetailView(APIView):
    def get(self, _, **kwargs):
        return api_response(ResponseCode.METHOD_NOT_ALLOWED, "暂未实现")


class PaperOnlineView(APIView):
    def get(self, request):
        paper_id = request.query_params.get("paper_id")
        if not paper_id:
            exam_id = request.query_params.get("exam_id")
            if exam_id:
                from src.apps.Exam.models import Exam

                exam = Exam.objects.filter(id=exam_id, is_deleted=False, is_published=True).first()
                if exam is None:
                    return api_response(ResponseCode.NOT_FOUND, "考试不存在")
                paper_id = exam.paper_id

        if not paper_id:
            return api_response(ResponseCode.BAD_REQUEST, "paper_id 或 exam_id 必须提供其一")

        paper = Paper.objects.filter(id=paper_id, is_published=True).first()
        if paper is None:
            return api_response(ResponseCode.NOT_FOUND, "试卷不存在或未发布")

        modules = list(PaperModule.objects.filter(paper_id=paper_id).order_by("sequence_number").values())
        pq_list = list(PaperQuestions.objects.filter(paper_id=paper_id).order_by("sequence_number").values())

        question_ids = [item["question_id"] for item in pq_list]
        question_map = {q.id: q for q in Questions.objects.filter(id__in=question_ids)}

        module_map = {}
        for module in modules:
            module_map[module["id"]] = {
                "module_id": module["id"],
                "title": module["title"],
                "description": module["description"],
                "sequence_number": module["sequence_number"],
                "questions": [],
            }

        orphan_questions = []
        for pq in pq_list:
            question = question_map.get(pq["question_id"])
            if question is None:
                continue
            try:
                options = json.loads(question.options)
            except Exception:
                options = question.options

            question_item = {
                "question_id": question.id,
                "topic": question.topic,
                "options": options,
                "type": question.type,
                "marks": pq["marks"],
                "sequence_number": pq["sequence_number"],
            }

            target_module = module_map.get(pq["module"])
            if target_module is None:
                orphan_questions.append(question_item)
            else:
                target_module["questions"].append(question_item)

        modules_data = list(module_map.values())
        if orphan_questions:
            modules_data.append(
                {
                    "module_id": "default",
                    "title": "默认模块",
                    "description": "未归类题目",
                    "sequence_number": 9999,
                    "questions": orphan_questions,
                }
            )

        return api_response(
            ResponseCode.SUCCESS,
            "获取试卷成功",
            {
                "paper": {
                    "id": paper.id,
                    "title": paper.title,
                    "description": paper.description,
                    "duration_minutes": paper.duration_minutes,
                    "total_marks": paper.total_marks,
                },
                "modules": modules_data,
            },
        )

