from django.urls import path

from .views import StudentUserView, TeacherUserView
from .views import StudentLoginView, TeacherLoginView
from .views import StudentChangePasswordView, TeacherChangePasswordView

urlpatterns = [
    path('students', StudentUserView.as_view(), name='student-list-create'),
    path('students/<str:id>', StudentUserView.as_view(), name='student-detail'),
    path('teachers', TeacherUserView.as_view(), name='teacher-list-create'),
    path('teachers/<str:id>', TeacherUserView.as_view(), name='teacher-detail'),
    path('auth/teacher/login', TeacherLoginView.as_view(), name='teacher-login'),
    path('auth/student/login', StudentLoginView.as_view(), name='student-login'),
    path('students/<str:user_id>/password', StudentChangePasswordView.as_view(), name='student-change-password'),
    path('teachers/<str:user_id>/password', TeacherChangePasswordView.as_view(), name='teacher-change-password'),
]


if __name__ == '__main__':
    pass
