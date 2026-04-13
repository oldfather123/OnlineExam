from django.urls import path

from .views import QuestionBaseView
from .views import ErrorArchiveView
from .views import QuestionsPaperView
from .views import AgentSelectQuestionsView


urlpatterns = [
    path('questions', QuestionBaseView.as_view(), name='question-list-create'),
    path('questions/<str:id>', QuestionBaseView.as_view(), name='question-detail'),
    path('error-archives', ErrorArchiveView.as_view(), name='error-archive-list-create'),
    path('error-archives/<str:id>', ErrorArchiveView.as_view(), name='error-archive-detail'),
    path('questions/paper-available', QuestionsPaperView.as_view(), name='question-paper-available'),
    path('questions/agent-select', AgentSelectQuestionsView.as_view(), name='question-agent-select'),
]


if __name__ == '__main__':
    pass
