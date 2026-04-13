from rest_framework.views import APIView

from .models import Student, Teacher
from .serializers import StudentSerializer, TeacherSerializer


# 用户列表管理
class UserBaseView(APIView):
    model_serializer = None
    model = None

    def post(self, request):
        pass

    def put(self, request, **kwargs):
        pass

    def delete(self, _, **kwargs):
        pass

    def get(self, request, **kwargs):
        pass


# 密码修改
class ChangePasswordBaseView(APIView):
    model_serializer = None
    model = None

    def put(self, request, **kwargs):
        pass


# 教师视图
# 教师登录
class TeacherLoginView(APIView):
    def post(self, request):
        pass


# 教师用户管理
class TeacherUserView(UserBaseView):
    model_serializer = TeacherSerializer
    model = Teacher


# 教师密码修改
class TeacherChangePasswordView(ChangePasswordBaseView):
    model_serializer = TeacherSerializer
    model = Teacher


# 学生视图
# 学生登录
class StudentLoginView(APIView):
    def post(self, request):
        pass


# 学生用户管理
class StudentUserView(UserBaseView):
    model_serializer = StudentSerializer
    model = Student


# 学生密码修改
class StudentChangePasswordView(ChangePasswordBaseView):
    model_serializer = StudentSerializer
    model = Student
