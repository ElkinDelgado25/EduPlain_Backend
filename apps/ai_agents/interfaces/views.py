from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import serializers, status
from rest_framework.exceptions import ValidationError
from rest_framework.parsers import MultiPartParser
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.ai_agents.application.use_cases import AnalyzeSyllabusPdf, SyllabusAnalysisError
from apps.ai_agents.infrastructure.syllabus_analyzer_factory import get_syllabus_analyzer
from apps.ai_agents.interfaces.serializers import (
    SyllabusAnalysisResultOutputSerializer,
    SyllabusAnalyzeInputSerializer,
)
from apps.documents.infrastructure.pdf_to_markdown import PyMuPDFMarkdownConverter


class SyllabusAnalysisErrorSerializer(serializers.Serializer):
    file = serializers.ListField(child=serializers.CharField())


class SyllabusAnalyzeView(APIView):
    parser_classes = [MultiPartParser]

    @extend_schema(
        tags=["AI Agents"],
        summary="Analyze an academic syllabus PDF",
        description=(
            "Receives a syllabus PDF, extracts its text as Markdown and returns an analysis. "
            "When AI_SYLLABUS_ENABLED is true and OPENAI_API_KEY is configured, the response "
            "is generated with OpenAI. Otherwise a generic phase-1 placeholder is returned."
        ),
        request=SyllabusAnalyzeInputSerializer,
        responses={
            200: SyllabusAnalysisResultOutputSerializer,
            400: OpenApiResponse(
                response=SyllabusAnalysisErrorSerializer,
                description="The uploaded PDF is invalid or could not be analyzed.",
            ),
        },
    )
    def post(self, request: Request) -> Response:
        serializer = SyllabusAnalyzeInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        uploaded_file = serializer.validated_data["file"]
        use_case = AnalyzeSyllabusPdf(
            converter=PyMuPDFMarkdownConverter(),
            analyzer=get_syllabus_analyzer(),
        )

        try:
            result = use_case.execute(
                filename=uploaded_file.name,
                content=uploaded_file.read(),
            )
        except SyllabusAnalysisError as exc:
            raise ValidationError({"file": [str(exc)]}) from exc

        output = SyllabusAnalysisResultOutputSerializer(result)
        return Response(output.data, status=status.HTTP_200_OK)
