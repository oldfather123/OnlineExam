"""URL configuration for ExamOnline project."""

from django.urls import include, path

urlpatterns = [
    path("api/", include("src.apps.User.urls")),
    path("api/", include("src.apps.Question.urls")),
    path("api/", include("src.apps.Paper.urls")),
    path("api/", include("src.apps.Exam.urls")),
    path("api/", include("src.apps.Score.urls")),
]
