import uuid

from django.core.paginator import Paginator
from django.db.models import Q
from rest_framework.views import APIView

from src.utils.response_utils import ResponseCode, api_response

from .models import Student, Teacher
from .serializers import StudentSerializer, TeacherSerializer


def public_user(user, role):
    return {
        "id": user.id,
        "username": user.username,
        "real_name": user.real_name,
        "role": role,
        "created_at": user.created_at,
        "updated_at": user.updated_at,
    }


class UserBaseView(APIView):
    model_serializer = None
    model = None
    role = ""

    def post(self, request):
        payload = request.data.copy()
        if not payload.get("id"):
            payload["id"] = str(uuid.uuid4())
        if not payload.get("password"):
            payload["password"] = "123456"

        serializer = self.model_serializer(data=payload)
        if not serializer.is_valid():
            return api_response(ResponseCode.BAD_REQUEST, "创建失败", serializer.errors)
        serializer.save()
        user = self.model.objects.get(id=serializer.data["id"])
        return api_response(ResponseCode.SUCCESS, "创建成功", public_user(user, self.role))

    def put(self, request, **kwargs):
        user = self.model.objects.filter(id=kwargs.get("id")).first()
        if user is None:
            return api_response(ResponseCode.NOT_FOUND, "用户不存在")

        payload = request.data.copy()
        for key in ["id", "created_at", "updated_at"]:
            payload.pop(key, None)

        serializer = self.model_serializer(user, data=payload, partial=True)
        if not serializer.is_valid():
            return api_response(ResponseCode.BAD_REQUEST, "编辑失败", serializer.errors)
        serializer.save()
        user.refresh_from_db()
        return api_response(ResponseCode.SUCCESS, "编辑成功", public_user(user, self.role))

    def delete(self, _, **kwargs):
        user = self.model.objects.filter(id=kwargs.get("id")).first()
        if user is None:
            return api_response(ResponseCode.NOT_FOUND, "用户不存在")
        user.delete()
        return api_response(ResponseCode.SUCCESS, "删除成功")

    def get(self, request, **kwargs):
        user_id = kwargs.get("id")
        if user_id:
            user = self.model.objects.filter(id=user_id).first()
            if user is None:
                return api_response(ResponseCode.NOT_FOUND, "用户不存在")
            return api_response(ResponseCode.SUCCESS, "查询用户详情成功", public_user(user, self.role))

        keyword = request.query_params.get("keyword")
        queryset = self.model.objects.all().order_by("-created_at")
        if keyword:
            queryset = queryset.filter(Q(username__icontains=keyword) | Q(real_name__icontains=keyword) | Q(id__icontains=keyword))

        page = max(int(request.query_params.get("currentPage", 1)), 1)
        page_size = max(int(request.query_params.get("pageSize", 50)), 1)
        paginator = Paginator(queryset, page_size)
        page_obj = paginator.get_page(page)
        rows = [public_user(user, self.role) for user in page_obj.object_list]
        return api_response(ResponseCode.SUCCESS, "查询成功", {"total": paginator.count, "data": rows})


class ChangePasswordBaseView(APIView):
    model_serializer = None
    model = None

    def put(self, request, **kwargs):
        user = self.model.objects.filter(id=kwargs.get("user_id")).first()
        if user is None:
            return api_response(ResponseCode.NOT_FOUND, "用户不存在")

        old_password = request.data.get("old_password")
        new_password = request.data.get("new_password")
        if not new_password:
            return api_response(ResponseCode.BAD_REQUEST, "new_password 为必填项")
        if old_password is not None and old_password != user.password:
            return api_response(ResponseCode.BAD_REQUEST, "原密码不正确")

        user.password = new_password
        user.save(update_fields=["password", "updated_at"])
        return api_response(ResponseCode.SUCCESS, "密码修改成功")


class LoginBaseView(APIView):
    model = None
    role = ""

    def post(self, request):
        account = request.data.get("username") or request.data.get("id")
        password = request.data.get("password")
        if not account or not password:
            return api_response(ResponseCode.BAD_REQUEST, "用户名和密码为必填项")

        user = self.model.objects.filter(Q(username=account) | Q(id=account)).first()
        if user is None or user.password != password:
            return api_response(ResponseCode.UNAUTHORIZED, "用户名或密码错误")
        return api_response(ResponseCode.SUCCESS, "登录成功", public_user(user, self.role))


class TeacherLoginView(LoginBaseView):
    model = Teacher
    role = "teacher"


class TeacherUserView(UserBaseView):
    model_serializer = TeacherSerializer
    model = Teacher
    role = "teacher"


class TeacherChangePasswordView(ChangePasswordBaseView):
    model_serializer = TeacherSerializer
    model = Teacher


class StudentLoginView(LoginBaseView):
    model = Student
    role = "student"


class StudentUserView(UserBaseView):
    model_serializer = StudentSerializer
    model = Student
    role = "student"


class StudentChangePasswordView(ChangePasswordBaseView):
    model_serializer = StudentSerializer
    model = Student
