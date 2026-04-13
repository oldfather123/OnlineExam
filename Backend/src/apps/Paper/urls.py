from django.urls import path

from .views import PaperBaseView
from .views import PaperModuleView, PaperQuestionsView
from .views import PaperPublishView, PaperForSelectorView
from .views import PaperDetailView

urlpatterns = [
    path('papers', PaperBaseView.as_view(), name='paper-list-create'),
    path('papers/<str:id>', PaperBaseView.as_view(), name='paper-detail'),
    path('paper-modules', PaperModuleView.as_view(), name='paper-module-list-create'),
    path('paper-modules/<str:id>', PaperModuleView.as_view(), name='paper-module-detail'),
    path('paper-questions', PaperQuestionsView.as_view(), name='paper-question-list-create'),
    path('paper-questions/<str:id>', PaperQuestionsView.as_view(), name='paper-question-detail'),
    path('papers/publish', PaperPublishView.as_view(), name='paper-publish'),
    path('papers/selector', PaperForSelectorView.as_view(), name='paper-selector'),
    path('papers/<str:id>/detail', PaperDetailView.as_view(), name='paper-detail-view'),
]
