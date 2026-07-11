from django.urls import path

from apps.ai_agents.interfaces.views import SyllabusAnalyzeView

app_name = "ai_agents"

urlpatterns = [
    path("syllabus/analyze/", SyllabusAnalyzeView.as_view(), name="syllabus-analyze"),
]
