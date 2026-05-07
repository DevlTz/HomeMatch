from django.urls import path

from apps.ai_analysis.views import AnalyzePropertyView

urlpatterns = [
    path("properties/<int:pk>/analyze/", AnalyzePropertyView.as_view()),
]
