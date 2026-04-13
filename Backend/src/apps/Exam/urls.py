from django.urls import path

from .views import ExamBaseView, ExamPublishView, ExamAttendView
from .views import ExamScheduleView, ExamDetailView


urlpatterns = [
     path('exams', ExamBaseView.as_view(), name='exam-list-create'),
     path('exams/<str:id>', ExamBaseView.as_view(), name='exam-detail'),
     path('exams/publish/<str:id>', ExamPublishView.as_view(), name='exam-publish'),
     path('exams/attend', ExamAttendView.as_view(), name='exam-attend'),
     path('exams/schedule', ExamScheduleView.as_view(), name='exam-schedule'),
     path('exams/detail', ExamDetailView.as_view(), name='exam-detail-view'),
]
