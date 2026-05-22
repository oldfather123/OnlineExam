from collections import defaultdict

from django.core.paginator import Paginator
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
    PaginationQuerySerializer,
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
                answer.save(update_fields=["answer_type", "answer_payload", "solution", "last_client_ts", "updated_at"])

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
        student_id = request.query_params.get("student_id")
        if not student_id:
            return api_response(ResponseCode.BAD_REQUEST, "student_id 为必填项")

        scores = list(Score.objects.filter(student_id=student_id).order_by("-start_time").values(
            "id", "exam_id", "result_mark", "submit_status", "start_time", "submitted_at"
        ))
        if not scores:
            return api_response(
                ResponseCode.SUCCESS,
                "获取学习分析成功",
                {
                    "student_id": student_id,
                    "exam_count": 0,
                    "submitted_count": 0,
                    "average_score": 0,
                    "trend": [],
                    "question_type_stats": {},
                },
            )

        exam_ids = [s["exam_id"] for s in scores]
        exams = {e.id: e for e in Exam.objects.filter(id__in=exam_ids).only("id", "title", "paper_id")}

        submitted = [x for x in scores if x["submit_status"]]
        average_score = round(sum(float(x["result_mark"] or 0) for x in submitted) / len(submitted), 2) if submitted else 0

        trend = []
        result_ids = [s["id"] for s in scores]
        details = list(ScoreDetail.objects.filter(exam_result_id__in=result_ids).values("exam_result_id", "question_id", "mark"))

        score_to_exam = {s["id"]: s["exam_id"] for s in scores}
        exam_qid_set = defaultdict(set)
        for exam in exams.values():
            for row in PaperQuestions.objects.filter(paper_id=exam.paper_id).values("question_id"):
                exam_qid_set[exam.id].add(row["question_id"])

        all_qids = set()
        for s in exam_qid_set.values():
            all_qids |= s
        q_types = {q.id: q.type for q in Questions.objects.filter(id__in=list(all_qids)).only("id", "type")}

        type_stat = defaultdict(lambda: {"full_mark": 0.0, "actual_mark": 0.0})
        for exam in exams.values():
            for row in PaperQuestions.objects.filter(paper_id=exam.paper_id).values("question_id", "marks"):
                q_type = q_types.get(row["question_id"], "unknown")
                type_stat[q_type]["full_mark"] += float(row["marks"] or 0)

        for row in details:
            exam_id = score_to_exam.get(row["exam_result_id"])
            if not exam_id:
                continue
            q_type = q_types.get(row["question_id"], "unknown")
            type_stat[q_type]["actual_mark"] += float(row["mark"] or 0)

        question_type_stats = {}
        for k, v in type_stat.items():
            rate = 0 if v["full_mark"] == 0 else round(v["actual_mark"] / v["full_mark"], 4)
            question_type_stats[k] = {**v, "score_rate": rate}

        for s in scores:
            e = exams.get(s["exam_id"])
            trend.append(
                {
                    "exam_result_id": s["id"],
                    "exam_id": s["exam_id"],
                    "exam_title": e.title if e else "",
                    "score": float(s["result_mark"] or 0),
                    "submit_status": s["submit_status"],
                    "start_time": s["start_time"],
                    "submitted_at": s["submitted_at"],
                }
            )

        return api_response(
            ResponseCode.SUCCESS,
            "获取学习分析成功",
            {
                "student_id": student_id,
                "exam_count": len(scores),
                "submitted_count": len(submitted),
                "average_score": average_score,
                "trend": trend,
                "question_type_stats": question_type_stats,
            },
        )


class ReviewPaperListView(APIView):
    def get(self, request):
        page_ser = PaginationQuerySerializer(data=request.query_params)
        if not page_ser.is_valid():
            return api_response(ResponseCode.BAD_REQUEST, "参数校验失败", page_ser.errors)
        page = page_ser.validated_data["page"]
        page_size = page_ser.validated_data["page_size"]

        exams = list(Exam.objects.filter(is_deleted=False, is_published=True).order_by("-start_time").values(
            "id", "title", "start_time", "end_time", "paper_id"
        ))
        exam_ids = [e["id"] for e in exams]

        stats = {
            row["exam_id"]: row
            for row in Score.objects.filter(exam_id__in=exam_ids)
            .values("exam_id")
            .annotate(total_students=Count("id"), submitted_students=Count("id", filter=Q(submit_status=True)))
        }

        paper_ids = [e["paper_id"] for e in exams]
        papers = {p.id: p for p in Paper.objects.filter(id__in=paper_ids).only("id", "title")}

        rows = []
        for exam in exams:
            paper = papers.get(exam["paper_id"])
            s = stats.get(exam["id"], {})
            rows.append(
                {
                    "exam_id": exam["id"],
                    "exam_title": exam["title"],
                    "start_time": exam["start_time"],
                    "end_time": exam["end_time"],
                    "paper": {
                        "paper_id": exam["paper_id"],
                        "title": paper.title if paper else "",
                    },
                    "review_stats": {
                        "total_students": s.get("total_students", 0),
                        "submitted_students": s.get("submitted_students", 0),
                    },
                }
            )

        paginator = Paginator(rows, page_size)
        page_obj = paginator.get_page(page)
        return api_response(
            ResponseCode.SUCCESS,
            "获取批阅试卷列表成功",
            {"total": paginator.count, "page": page_obj.number, "page_size": page_size, "items": list(page_obj.object_list)},
        )


class ReviewExamStudentListView(APIView):
    def get(self, request, exam_id):
        page_ser = PaginationQuerySerializer(data=request.query_params)
        if not page_ser.is_valid():
            return api_response(ResponseCode.BAD_REQUEST, "参数校验失败", page_ser.errors)
        page = page_ser.validated_data["page"]
        page_size = page_ser.validated_data["page_size"]

        if not Exam.objects.filter(id=exam_id).exists():
            return api_response(ResponseCode.NOT_FOUND, "考试不存在")

        queryset = list(
            Score.objects.filter(exam_id=exam_id)
            .order_by("student_id")
            .values("id", "student_id", "submit_status", "start_time", "submitted_at", "result_mark")
        )
        paginator = Paginator(queryset, page_size)
        page_obj = paginator.get_page(page)
        items = [
            {
                "exam_result_id": s["id"],
                "student_id": s["student_id"],
                "submit_status": s["submit_status"],
                "start_time": s["start_time"],
                "submitted_at": s["submitted_at"],
                "result_mark": s["result_mark"],
            }
            for s in page_obj.object_list
        ]
        return api_response(
            ResponseCode.SUCCESS,
            "获取考生答卷列表成功",
            {"total": paginator.count, "page": page_obj.number, "page_size": page_size, "items": items},
        )


class ReviewExamResultDetailView(APIView):
    def get(self, request, exam_result_id):
        score = Score.objects.filter(id=exam_result_id).only("id", "exam_id", "student_id", "submit_status", "submitted_at", "result_mark").first()
        if score is None:
            return api_response(ResponseCode.NOT_FOUND, "考试记录不存在")

        exam = Exam.objects.filter(id=score.exam_id).only("id", "paper_id").first()
        if exam is None:
            return api_response(ResponseCode.NOT_FOUND, "考试不存在")

        pq_list = list(PaperQuestions.objects.filter(paper_id=exam.paper_id).order_by("sequence_number").values("question_id", "marks"))
        question_ids = [x["question_id"] for x in pq_list]
        q_map = {q.id: q for q in Questions.objects.filter(id__in=question_ids).only("id", "topic", "type", "answer")}

        answers = {
            a.question_id: a
            for a in Answer.objects.filter(exam_result_id=exam_result_id, question_id__in=question_ids).only("question_id", "answer_payload")
        }
        score_details = {
            d.question_id: d
            for d in ScoreDetail.objects.filter(exam_result_id=exam_result_id, question_id__in=question_ids).only("question_id", "mark", "comment")
        }

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
                defaults={"mark": mark, "comment": comment, "graded_by": grader_id, "graded_at": now},
            )
            detail.mark = mark
            detail.comment = comment
            detail.graded_by = grader_id
            detail.graded_at = now
            detail.save(update_fields=["mark", "comment", "graded_by", "graded_at"])

        total = ScoreDetail.objects.filter(exam_result_id=exam_result_id).aggregate(total_mark=Sum("mark")).get("total_mark") or 0
        score.result_mark = float(total)
        if finalize and score.end_time is None:
            score.end_time = now
        score.save(update_fields=["result_mark", "end_time", "updated_at"])

        return api_response(
            ResponseCode.SUCCESS,
            "评分处理成功",
            {"exam_result_id": score.id, "result_mark": score.result_mark, "finalize": finalize},
        )


class ReviewAutoGradeView(APIView):
    @transaction.atomic
    def post(self, request, exam_result_id):
        score = Score.objects.select_for_update().filter(id=exam_result_id).first()
        if score is None:
            return api_response(ResponseCode.NOT_FOUND, "考试记录不存在")

        exam = Exam.objects.filter(id=score.exam_id).only("id", "paper_id").first()
        if exam is None:
            return api_response(ResponseCode.NOT_FOUND, "考试不存在")

        pq_list = list(PaperQuestions.objects.filter(paper_id=exam.paper_id).values("question_id", "marks"))
        q_ids = [x["question_id"] for x in pq_list]
        q_map = {q.id: q for q in Questions.objects.filter(id__in=q_ids).only("id", "type", "answer")}
        marks_map = {x["question_id"]: float(x["marks"]) for x in pq_list}
        answers = {a.question_id: a for a in Answer.objects.filter(exam_result_id=exam_result_id, question_id__in=q_ids).only("question_id", "answer_payload")}

        graded = 0
        subjective_pending = 0
        now = timezone.now()
        for qid in q_ids:
            q = q_map.get(qid)
            if q is None:
                continue
            if q.type not in ["select", "judge"]:
                subjective_pending += 1
                continue

            ans = answers.get(qid)
            student_val = self._normalize_answer(ans.answer_payload if ans else {})
            standard_val = self._normalize_answer({"value": q.answer})
            mark = marks_map.get(qid, 0.0) if student_val == standard_val else 0.0

            detail, _ = ScoreDetail.objects.get_or_create(
                exam_result_id=exam_result_id,
                question_id=qid,
                defaults={"mark": mark, "comment": "自动判分", "graded_by": "system", "graded_at": now},
            )
            detail.mark = mark
            detail.comment = "自动判分"
            detail.graded_by = "system"
            detail.graded_at = now
            detail.save(update_fields=["mark", "comment", "graded_by", "graded_at"])
            graded += 1

        total = ScoreDetail.objects.filter(exam_result_id=exam_result_id).aggregate(total_mark=Sum("mark")).get("total_mark") or 0
        score.result_mark = float(total)
        score.save(update_fields=["result_mark", "updated_at"])

        return api_response(
            ResponseCode.SUCCESS,
            "客观题自动判分完成",
            {
                "exam_result_id": exam_result_id,
                "auto_graded_count": graded,
                "subjective_pending_count": subjective_pending,
                "result_mark": score.result_mark,
            },
        )

    def _normalize_answer(self, payload):
        if isinstance(payload, dict):
            value = payload.get("value", "")
        else:
            value = payload
        if isinstance(value, list):
            value = ",".join(str(x).strip().upper() for x in value)
        return str(value).strip().upper()


class ReviewStatisticsView(APIView):
    def get(self, request, exam_id):
        exam = Exam.objects.filter(id=exam_id).only("id", "paper_id").first()
        if exam is None:
            return api_response(ResponseCode.NOT_FOUND, "考试不存在")

        scores = list(Score.objects.filter(exam_id=exam_id).values("id", "student_id", "result_mark", "submit_status"))
        result_ids = [x["id"] for x in scores]

        details = list(ScoreDetail.objects.filter(exam_result_id__in=result_ids).values("exam_result_id", "question_id", "mark"))
        pq_list = list(PaperQuestions.objects.filter(paper_id=exam.paper_id).values("question_id", "marks"))
        q_map = {q.id: q for q in Questions.objects.filter(id__in=[x["question_id"] for x in pq_list]).only("id", "type")}
        pq_mark_map = {x["question_id"]: float(x["marks"]) for x in pq_list}

        student_summary = [
            {
                "exam_result_id": s["id"],
                "student_id": s["student_id"],
                "submit_status": s["submit_status"],
                "total_score": float(s["result_mark"] or 0),
            }
            for s in scores
        ]

        type_stat = {}
        for qid, q in q_map.items():
            q_type = q.type
            if q_type not in type_stat:
                type_stat[q_type] = {"full_mark": 0.0, "actual_mark": 0.0}
            type_stat[q_type]["full_mark"] += pq_mark_map.get(qid, 0.0)

        for d in details:
            q = q_map.get(d["question_id"])
            if not q:
                continue
            q_type = q.type
            if q_type not in type_stat:
                type_stat[q_type] = {"full_mark": 0.0, "actual_mark": 0.0}
            type_stat[q_type]["actual_mark"] += float(d["mark"] or 0)

        for t in type_stat:
            full_mark = type_stat[t]["full_mark"]
            actual_mark = type_stat[t]["actual_mark"]
            type_stat[t]["score_rate"] = 0 if full_mark == 0 else round(actual_mark / full_mark, 4)

        submitted = [x for x in scores if x["submit_status"]]
        avg_score = 0.0
        if submitted:
            avg_score = round(sum(float(x["result_mark"] or 0) for x in submitted) / len(submitted), 2)

        return api_response(
            ResponseCode.SUCCESS,
            "获取成绩统计成功",
            {
                "exam_id": exam_id,
                "student_count": len(scores),
                "submitted_count": len(submitted),
                "average_score": avg_score,
                "student_summary": student_summary,
                "question_type_stats": type_stat,
            },
        )

