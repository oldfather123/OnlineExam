import json

from django.core.paginator import Paginator
from django.db.models import Sum
from django.utils import timezone
from rest_framework.views import APIView

from src.apps.Question.models import Questions
from src.utils.response_utils import ResponseCode, api_response

from .models import Paper, PaperModule, PaperQuestions
from .serializers import PaperModuleSerializer, PaperQuestionsSerializer, PaperSerializer


class PaperBaseView(APIView):
    def post(self, request):
        serializer = PaperSerializer(data=request.data)
        if not serializer.is_valid():
            return api_response(ResponseCode.BAD_REQUEST, "创建失败", serializer.errors)
        serializer.save()
        return api_response(ResponseCode.SUCCESS, "创建成功", serializer.data)

    def delete(self, _, **kwargs):
        paper = Paper.objects.filter(id=kwargs.get("id")).first()
        if paper is None:
            return api_response(ResponseCode.NOT_FOUND, "试卷不存在")
        paper.delete()
        return api_response(ResponseCode.SUCCESS, "删除成功")

    def put(self, request, **kwargs):
        paper = Paper.objects.filter(id=kwargs.get("id")).first()
        if paper is None:
            return api_response(ResponseCode.NOT_FOUND, "试卷不存在")

        payload = request.data.copy()
        for key in ["id", "created_at", "updated_at"]:
            payload.pop(key, None)

        serializer = PaperSerializer(paper, data=payload, partial=True)
        if not serializer.is_valid():
            return api_response(ResponseCode.BAD_REQUEST, "编辑失败", serializer.errors)
        serializer.save()
        return api_response(ResponseCode.SUCCESS, "编辑成功", serializer.data)

    def get(self, request, **kwargs):
        paper_id = kwargs.get("id")
        if paper_id:
            paper = Paper.objects.filter(id=paper_id).first()
            if paper is None:
                return api_response(ResponseCode.NOT_FOUND, "试卷不存在")
            data = PaperSerializer(paper).data
            total = PaperQuestions.objects.filter(paper_id=paper_id).aggregate(v=Sum("marks")).get("v") or 0
            data["actual_total"] = float(total)
            return api_response(ResponseCode.SUCCESS, "查询试卷详情成功", data)

        queryset = Paper.objects.all().order_by("-created_at")
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

        rows = PaperSerializer(page_obj.object_list, many=True).data
        for item in rows:
            total = PaperQuestions.objects.filter(paper_id=item["id"]).aggregate(v=Sum("marks")).get("v") or 0
            item["actual_total"] = float(total)

        return api_response(ResponseCode.SUCCESS, "查询成功", {"total": paginator.count, "data": rows})


class PaperModuleView(APIView):
    def post(self, request):
        paper_id = request.data.get("paper_id")
        if not paper_id:
            return api_response(ResponseCode.BAD_REQUEST, "paper_id 为必填项")

        payload = request.data.copy()
        if "sequence_number" not in payload:
            payload["sequence_number"] = PaperModule.objects.filter(paper_id=paper_id).count() + 1

        serializer = PaperModuleSerializer(data=payload)
        if not serializer.is_valid():
            return api_response(ResponseCode.BAD_REQUEST, "创建失败", serializer.errors)
        serializer.save()
        return api_response(ResponseCode.SUCCESS, "创建成功", serializer.data)

    def delete(self, request):
        module_id = request.data.get("id")
        paper_id = request.data.get("paper_id")
        module = PaperModule.objects.filter(id=module_id).first()
        if module is None:
            return api_response(ResponseCode.NOT_FOUND, "模块不存在")

        has_questions = PaperQuestions.objects.filter(paper_id=paper_id, module=module_id).exists()
        if has_questions:
            return api_response(ResponseCode.BAD_REQUEST, "该模块已关联试题，无法删除")

        module.delete()
        return api_response(ResponseCode.SUCCESS, "删除模块成功")

    def put(self, request, **kwargs):
        module = PaperModule.objects.filter(id=kwargs.get("id")).first()
        if module is None:
            return api_response(ResponseCode.NOT_FOUND, "模块不存在")

        payload = request.data.copy()
        for key in ["id", "created_at", "updated_at"]:
            payload.pop(key, None)

        serializer = PaperModuleSerializer(module, data=payload, partial=True)
        if not serializer.is_valid():
            return api_response(ResponseCode.BAD_REQUEST, "编辑失败", serializer.errors)
        serializer.save()
        return api_response(ResponseCode.SUCCESS, "编辑成功", serializer.data)

    def get(self, _, **kwargs):
        paper_id = kwargs.get("id")
        if not Paper.objects.filter(id=paper_id).exists():
            return api_response(ResponseCode.NOT_FOUND, "试卷不存在")
        rows = PaperModule.objects.filter(paper_id=paper_id).order_by("sequence_number")
        return api_response(ResponseCode.SUCCESS, "获取试卷模块详情成功", PaperModuleSerializer(rows, many=True).data)


class PaperQuestionsView(APIView):
    def post(self, request):
        link_questions = request.data.get("questions_info", [])
        if not link_questions:
            return api_response(ResponseCode.BAD_REQUEST, "questions_info 不能为空")

        paper_id = link_questions[0].get("paper_id")
        module = link_questions[0].get("module", "")
        linked_count = PaperQuestions.objects.filter(paper_id=paper_id, module=module).count()

        created = []
        errors = []
        for idx, item in enumerate(link_questions):
            payload = dict(item)
            payload["sequence_number"] = linked_count + idx + 1
            serializer = PaperQuestionsSerializer(data=payload)
            if serializer.is_valid():
                serializer.save()
                created.append(serializer.data)
            else:
                errors.append(serializer.errors)

        if errors:
            return api_response(ResponseCode.BAD_REQUEST, "部分关联失败", errors)
        return api_response(ResponseCode.SUCCESS, "批量关联成功", created)

    def delete(self, _, **kwargs):
        link = PaperQuestions.objects.filter(id=kwargs.get("id")).first()
        if link is None:
            return api_response(ResponseCode.NOT_FOUND, "关联关系不存在")

        paper_id, module = link.paper_id, link.module
        link.delete()

        left = list(PaperQuestions.objects.filter(paper_id=paper_id, module=module).order_by("sequence_number"))
        for idx, item in enumerate(left):
            item.sequence_number = idx + 1
        PaperQuestions.objects.bulk_update(left, ["sequence_number"])
        return api_response(ResponseCode.SUCCESS, "取消关联成功")

    def put(self, request, **kwargs):
        link = PaperQuestions.objects.filter(id=kwargs.get("id")).first()
        if link is None:
            return api_response(ResponseCode.NOT_FOUND, "关联关系不存在")

        serializer = PaperQuestionsSerializer(link, data=request.data, partial=True)
        if not serializer.is_valid():
            return api_response(ResponseCode.BAD_REQUEST, "编辑失败", serializer.errors)
        serializer.save()
        return api_response(ResponseCode.SUCCESS, "编辑成功", serializer.data)

    def get(self, _, **kwargs):
        paper_id = kwargs.get("id")
        if not Paper.objects.filter(id=paper_id).exists():
            return api_response(ResponseCode.NOT_FOUND, "试卷不存在")
        rows = PaperQuestions.objects.filter(paper_id=paper_id).order_by("sequence_number")
        return api_response(ResponseCode.SUCCESS, "获取试卷关联的试题信息成功", PaperQuestionsSerializer(rows, many=True).data)


class PaperPublishView(APIView):
    def post(self, request):
        paper = Paper.objects.filter(id=request.data.get("id")).first()
        if paper is None:
            return api_response(ResponseCode.NOT_FOUND, "试卷不存在")
        if not PaperQuestions.objects.filter(paper_id=paper.id).exists():
            return api_response(ResponseCode.BAD_REQUEST, "发布失败！试卷未关联试题")
        paper.is_published = True
        paper.updated_at = timezone.now()
        paper.save(update_fields=["is_published", "updated_at"])
        return api_response(ResponseCode.SUCCESS, "试卷发布成功")

    def delete(self, request):
        paper = Paper.objects.filter(id=request.data.get("id")).first()
        if paper is None:
            return api_response(ResponseCode.NOT_FOUND, "试卷不存在")
        paper.is_published = False
        paper.updated_at = timezone.now()
        paper.save(update_fields=["is_published", "updated_at"])
        return api_response(ResponseCode.SUCCESS, "取消发布成功")


class PaperForSelectorView(APIView):
    def get(self, request):
        queryset = Paper.objects.filter(is_published=True).order_by("-created_at")
        data = PaperSerializer(queryset, many=True).data
        return api_response(ResponseCode.SUCCESS, "查询成功", {"total": len(data), "data": data})


class PaperDetailView(APIView):
    def get(self, _, **kwargs):
        paper_id = kwargs.get("id")
        if not Paper.objects.filter(id=paper_id).exists():
            return api_response(ResponseCode.NOT_FOUND, "试卷不存在")

        modules = PaperModuleSerializer(PaperModule.objects.filter(paper_id=paper_id).order_by("sequence_number"), many=True).data
        links = list(PaperQuestions.objects.filter(paper_id=paper_id).order_by("sequence_number").values())

        q_ids = [x["question_id"] for x in links]
        q_map = {q.id: q for q in Questions.objects.filter(id__in=q_ids)}

        for item in links:
            q = q_map.get(item["question_id"])
            if q is None:
                item["question_detail"] = None
                continue
            try:
                options = json.loads(q.options)
            except Exception:
                options = q.options
            item["question_detail"] = {
                "id": q.id,
                "topic": q.topic,
                "options": options,
                "answer": q.answer,
                "type": q.type,
            }

        result = []
        for m in modules:
            m_questions = [x for x in links if x.get("module") == m["id"]]
            result.append({**m, "questions": m_questions})

        return api_response(ResponseCode.SUCCESS, "获取试卷详情成功", result)


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
