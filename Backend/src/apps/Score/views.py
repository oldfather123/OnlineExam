from django.db import transaction
from django.db.models import Count, Q, Sum
from django.utils import timezone
from rest_framework.views import APIView

from src.apps.Exam.models import Exam
from src.apps.Paper.models import Paper, PaperQuestions
from src.apps.Question.models import Questions
from src.utils.response_utils import ResponseCode, api_response

from .models import Answer, Score, ScoreDetail
from .serializers import (
    AnswerCommitRequestSerializer,
    AnswerCommitStatusQuerySerializer,
    ReviewScoreProcessRequestSerializer,
)


class ScoreBaseView(APIView):
    def post(self, request):
        return api_response(ResponseCode.METHOD_NOT_ALLOWED, "暂未实现")

    def delete(self, _, **kwargs):
        return api_response(ResponseCode.METHOD_NOT_ALLOWED, "暂未实现")

    def put(self, request, **kwargs):
        return api_response(ResponseCode.METHOD_NOT_ALLOWED, "暂未实现")

    def get(self, request, **kwargs):
        return api_response(ResponseCode.METHOD_NOT_ALLOWED, "暂未实现")


class AnswerGetView(APIView):
    def get(self, request):
        exam_result_id = request.query_params.get("exam_result_id")
        if not exam_result_id:
            return api_response(ResponseCode.BAD_REQUEST, "exam_result_id 为必填项")

        answers = Answer.objects.filter(exam_result_id=exam_result_id).order_by("updated_at")
        data = [
            {
                "question_id": a.question_id,
                "type": a.answer_type,
                "payload": a.answer_payload,
                "updated_at": a.updated_at,
                "client_ts": a.last_client_ts,
            }
            for a in answers
        ]
        return api_response(ResponseCode.SUCCESS, "获取答案成功", data)


class AnswerGradeView(APIView):
    def post(self, request):
        return api_response(ResponseCode.METHOD_NOT_ALLOWED, "请使用 reviews/exam-results/{id}/grade")

    def delete(self, _, **kwargs):
        return api_response(ResponseCode.METHOD_NOT_ALLOWED, "暂未实现")

    def put(self, request, **kwargs):
        return api_response(ResponseCode.METHOD_NOT_ALLOWED, "暂未实现")

    def get(self, request, **kwargs):
        return api_response(ResponseCode.METHOD_NOT_ALLOWED, "暂未实现")


class ScoreDetailView(APIView):
    def post(self, request):
        return api_response(ResponseCode.METHOD_NOT_ALLOWED, "暂未实现")

    def delete(self, _, **kwargs):
        return api_response(ResponseCode.METHOD_NOT_ALLOWED, "暂未实现")

    def get(self, request):
        return api_response(ResponseCode.METHOD_NOT_ALLOWED, "暂未实现")


class AnswerCommitView(APIView):
    """
    Unified answer payload format:
    {
      "exam_result_id": "..."  # or exam_id + student_id
      "exam_id": "...",
      "student_id": "...",
      "action": "save" | "submit",
      "client_ts": 1710000000000,
      "answers": [
        {
          "question_id": "...",
          "type": "select|blank|subjective",
          "payload": {"value": "A", "meta": {"index": 1}}
        }
      ]
    }
    """

    @transaction.atomic
    def post(self, request):
        serializer = AnswerCommitRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return api_response(ResponseCode.BAD_REQUEST, "参数校验失败", serializer.errors)
        payload = serializer.validated_data

        action = payload.get("action", "save")
        client_ts = payload["client_ts"]

        score = self._resolve_exam_result(payload)
        if score is None:
            return api_response(ResponseCode.NOT_FOUND, "考试记录不存在，请先进入考试")

        # consistency check to avoid out-of-order overwrite
        if client_ts < score.last_client_ts:
            return api_response(
                ResponseCode.CONFLICT,
                "检测到过期提交，已拒绝覆盖最新答案",
                {"server_last_client_ts": score.last_client_ts},
            )

        if score.submit_status:
            return api_response(
                ResponseCode.CONFLICT,
                "该答卷已提交，不能重复提交或修改",
                {"submitted_at": score.submitted_at, "submitted_client_ts": score.submitted_client_ts},
            )

        answers = payload.get("answers", [])

        now = timezone.now()
        for item in answers:
            question_id = item["question_id"]
            answer_type = item.get("type") or "subjective"
            answer_payload = item.get("payload", {})

            answer, _ = Answer.objects.get_or_create(
                exam_result_id=score.id,
                question_id=question_id,
                defaults={
                    "answer_type": answer_type,
                    "answer_payload": answer_payload,
                    "solution": str(answer_payload.get("value", "")) if isinstance(answer_payload, dict) else str(answer_payload),
                    "last_client_ts": client_ts,
                },
            )

            if answer.last_client_ts <= client_ts:
                answer.answer_type = answer_type
                answer.answer_payload = answer_payload if isinstance(answer_payload, dict) else {"value": answer_payload}
                answer.solution = str(answer.answer_payload.get("value", ""))
                answer.last_client_ts = client_ts
                answer.save(
                    update_fields=[
                        "answer_type",
                        "answer_payload",
                        "solution",
                        "last_client_ts",
                        "updated_at",
                    ]
                )

        score.last_client_ts = client_ts
        score.last_save_at = now

        if action == "submit":
            score.submit_status = True
            score.submitted_at = now
            score.submitted_client_ts = client_ts
            if score.end_time is None:
                score.end_time = now

        score.save(
            update_fields=[
                "last_client_ts",
                "last_save_at",
                "submit_status",
                "submitted_at",
                "submitted_client_ts",
                "end_time",
                "updated_at",
            ]
        )

        return api_response(
            ResponseCode.SUCCESS,
            "答案保存成功" if action == "save" else "答案提交成功",
            {
                "exam_result_id": score.id,
                "submit_status": score.submit_status,
                "last_client_ts": score.last_client_ts,
                "last_save_at": score.last_save_at,
                "submitted_at": score.submitted_at,
            },
        )

    def get(self, request, **kwargs):
        exam_result_id = kwargs.get("id") or request.query_params.get("exam_result_id")
        if not exam_result_id:
            return api_response(ResponseCode.BAD_REQUEST, "exam_result_id 为必填项")
        qs = AnswerCommitStatusQuerySerializer(data={"exam_result_id": exam_result_id})
        if not qs.is_valid():
            return api_response(ResponseCode.BAD_REQUEST, "参数校验失败", qs.errors)

        score = Score.objects.filter(id=exam_result_id).first()
        if score is None:
            return api_response(ResponseCode.NOT_FOUND, "考试记录不存在")

        return api_response(
            ResponseCode.SUCCESS,
            "获取提交状态成功",
            {
                "exam_result_id": score.id,
                "submit_status": score.submit_status,
                "last_client_ts": score.last_client_ts,
                "last_save_at": score.last_save_at,
                "submitted_at": score.submitted_at,
            },
        )

    def _resolve_exam_result(self, payload):
        exam_result_id = payload.get("exam_result_id")
        if exam_result_id:
            return Score.objects.select_for_update().filter(id=exam_result_id).first()

        exam_id = payload.get("exam_id")
        student_id = payload.get("student_id")
        if not exam_id or not student_id:
            return None
        return Score.objects.select_for_update().filter(exam_id=exam_id, student_id=student_id).first()


class ScoreAnalyzeView(APIView):
    def get(self, request):
        return api_response(ResponseCode.METHOD_NOT_ALLOWED, "暂未实现")


class ReviewPaperListView(APIView):
    """Module: paper management for teacher review."""

    def get(self, request):
        exams = Exam.objects.filter(is_deleted=False, is_published=True).order_by("-start_time")
        exam_ids = [e.id for e in exams]

        stats = {
            row["exam_id"]: row
            for row in Score.objects.filter(exam_id__in=exam_ids)
            .values("exam_id")
            .annotate(total_students=Count("id"), submitted_students=Count("id", filter=Q(submit_status=True)))
        }

        paper_ids = [e.paper_id for e in exams]
        papers = {p.id: p for p in Paper.objects.filter(id__in=paper_ids)}

        data = []
        for exam in exams:
            paper = papers.get(exam.paper_id)
            s = stats.get(exam.id, {})
            data.append(
                {
                    "exam_id": exam.id,
                    "exam_title": exam.title,
                    "start_time": exam.start_time,
                    "end_time": exam.end_time,
                    "paper": {
                        "paper_id": exam.paper_id,
                        "title": paper.title if paper else "",
                    },
                    "review_stats": {
                        "total_students": s.get("total_students", 0),
                        "submitted_students": s.get("submitted_students", 0),
                    },
                }
            )
        return api_response(ResponseCode.SUCCESS, "获取批阅试卷列表成功", data)


class ReviewExamStudentListView(APIView):
    """Module: answer sheet overview."""

    def get(self, request, exam_id):
        exam = Exam.objects.filter(id=exam_id).first()
        if exam is None:
            return api_response(ResponseCode.NOT_FOUND, "考试不存在")

        queryset = Score.objects.filter(exam_id=exam_id).order_by("student_id")
        data = [
            {
                "exam_result_id": s.id,
                "student_id": s.student_id,
                "submit_status": s.submit_status,
                "start_time": s.start_time,
                "submitted_at": s.submitted_at,
                "result_mark": s.result_mark,
            }
            for s in queryset
        ]
        return api_response(ResponseCode.SUCCESS, "获取考生答卷列表成功", data)


class ReviewExamResultDetailView(APIView):
    def get(self, request, exam_result_id):
        score = Score.objects.filter(id=exam_result_id).first()
        if score is None:
            return api_response(ResponseCode.NOT_FOUND, "考试记录不存在")

        exam = Exam.objects.filter(id=score.exam_id).first()
        if exam is None:
            return api_response(ResponseCode.NOT_FOUND, "考试不存在")

        pq_list = list(PaperQuestions.objects.filter(paper_id=exam.paper_id).order_by("sequence_number").values())
        question_ids = [x["question_id"] for x in pq_list]
        q_map = {q.id: q for q in Questions.objects.filter(id__in=question_ids)}

        answers = {a.question_id: a for a in Answer.objects.filter(exam_result_id=exam_result_id)}
        score_details = {d.question_id: d for d in ScoreDetail.objects.filter(exam_result_id=exam_result_id)}

        items = []
        for pq in pq_list:
            q = q_map.get(pq["question_id"])
            if q is None:
                continue
            ans = answers.get(q.id)
            sd = score_details.get(q.id)
            items.append(
                {
                    "question_id": q.id,
                    "topic": q.topic,
                    "type": q.type,
                    "marks": pq["marks"],
                    "standard_answer": q.answer,
                    "student_answer": ans.answer_payload if ans else {},
                    "score": sd.mark if sd else 0,
                    "comment": sd.comment if sd else "",
                }
            )

        return api_response(
            ResponseCode.SUCCESS,
            "获取答卷详情成功",
            {
                "exam_result": {
                    "id": score.id,
                    "exam_id": score.exam_id,
                    "student_id": score.student_id,
                    "submit_status": score.submit_status,
                    "submitted_at": score.submitted_at,
                    "result_mark": score.result_mark,
                },
                "questions": items,
            },
        )


class ReviewScoreProcessView(APIView):
    """Module: score processing."""

    @transaction.atomic
    def post(self, request, exam_result_id):
        serializer = ReviewScoreProcessRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return api_response(ResponseCode.BAD_REQUEST, "参数校验失败", serializer.errors)
        payload = serializer.validated_data

        score = Score.objects.select_for_update().filter(id=exam_result_id).first()
        if score is None:
            return api_response(ResponseCode.NOT_FOUND, "考试记录不存在")

        items = payload["items"]
        grader_id = payload.get("grader_id", "")
        finalize = payload.get("finalize", False)

        now = timezone.now()
        for item in items:
            qid = item["question_id"]
            mark = float(item["mark"])
            comment = item.get("comment", "")

            detail, _ = ScoreDetail.objects.get_or_create(
                exam_result_id=exam_result_id,
                question_id=qid,
                defaults={
                    "mark": mark,
                    "comment": comment,
                    "graded_by": grader_id,
                    "graded_at": now,
                },
            )
            detail.mark = mark
            detail.comment = comment
            detail.graded_by = grader_id
            detail.graded_at = now
            detail.save(update_fields=["mark", "comment", "graded_by", "graded_at"])

        total = (
            ScoreDetail.objects.filter(exam_result_id=exam_result_id).aggregate(total_mark=Sum("mark")).get("total_mark")
            or 0
        )
        score.result_mark = float(total)
        if finalize and score.end_time is None:
            score.end_time = now
        score.save(update_fields=["result_mark", "end_time", "updated_at"])

        return api_response(
            ResponseCode.SUCCESS,
            "评分处理成功",
            {"exam_result_id": score.id, "result_mark": score.result_mark, "finalize": finalize},
        )
