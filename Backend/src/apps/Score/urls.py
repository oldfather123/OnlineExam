from django.urls import path

from .views import ScoreDetailView, ScoreBaseView, ScoreAnalyzeView
from .views import AnswerGetView, AnswerGradeView, AnswerCommitView

urlpatterns = [
    path('scores', ScoreBaseView.as_view(), name='score-list-create'),
    path('scores/<str:id>', ScoreBaseView.as_view(), name='score-detail'),
    path('scores/detail', ScoreDetailView.as_view(), name='score-detail-view'),
    path('scores/detail/<str:id>', ScoreDetailView.as_view(), name='score-detail-item'),
    path('scores/analyze', ScoreAnalyzeView.as_view(), name='score-analyze'),
    path('answers', AnswerGetView.as_view(), name='answer-get'),
    path('answers/grade', AnswerGradeView.as_view(), name='answer-grade'),
    path('answers/grade/<str:id>', AnswerGradeView.as_view(), name='answer-grade-detail'),
    path('answers/commit', AnswerCommitView.as_view(), name='answer-commit'),
    path('answers/commit/<str:id>', AnswerCommitView.as_view(), name='answer-commit-detail'),
]
