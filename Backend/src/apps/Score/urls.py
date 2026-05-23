from django.urls import path

from .views import (
    AnswerCommitView,
    AnswerGetView,
    AnswerGradeView,
    ReviewAutoGradeView,
    ReviewExamResultDetailView,
    ReviewExamStudentListView,
    ReviewPaperListView,
    DashboardSummaryView,
    ReviewScoreProcessView,
    ReviewStatisticsView,
    ScoreAnalyzeView,
    ScoreBaseView,
    ScoreDetailView,
)

urlpatterns = [
    path("scores", ScoreBaseView.as_view(), name="score-list-create"),
    path("scores/<str:id>", ScoreBaseView.as_view(), name="score-detail"),
    path("scores/detail", ScoreDetailView.as_view(), name="score-detail-view"),
    path("scores/detail/<str:id>", ScoreDetailView.as_view(), name="score-detail-item"),
    path("scores/analyze", ScoreAnalyzeView.as_view(), name="score-analyze"),
    path("dashboard/summary", DashboardSummaryView.as_view(), name="dashboard-summary"),

    # student answer APIs
    path("answers", AnswerGetView.as_view(), name="answer-get"),
    path("answers/grade", AnswerGradeView.as_view(), name="answer-grade"),
    path("answers/grade/<str:id>", AnswerGradeView.as_view(), name="answer-grade-detail"),
    path("answers/commit", AnswerCommitView.as_view(), name="answer-commit"),
    path("answers/commit/<str:id>", AnswerCommitView.as_view(), name="answer-commit-detail"),

    # teacher review system APIs
    path("reviews/papers", ReviewPaperListView.as_view(), name="review-paper-list"),
    path("reviews/exams/<str:exam_id>/students", ReviewExamStudentListView.as_view(), name="review-exam-students"),
    path("reviews/exams/<str:exam_id>/statistics", ReviewStatisticsView.as_view(), name="review-exam-statistics"),
    path("reviews/exam-results/<str:exam_result_id>", ReviewExamResultDetailView.as_view(), name="review-exam-result-detail"),
    path("reviews/exam-results/<str:exam_result_id>/auto-grade", ReviewAutoGradeView.as_view(), name="review-auto-grade"),
    path("reviews/exam-results/<str:exam_result_id>/grade", ReviewScoreProcessView.as_view(), name="review-score-process"),
]
