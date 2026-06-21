from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import serializers, status
from rest_framework.exceptions import ValidationError
from rest_framework.parsers import MultiPartParser
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.documents.application.use_cases import ConvertPdfToMarkdown, DocumentConversionError
from apps.documents.infrastructure.pdf_to_markdown import PyMuPDFMarkdownConverter
from apps.documents.interfaces.serializers import (
    PdfToMarkdownInputSerializer,
    PdfToMarkdownOutputSerializer,
)


class PdfConversionErrorSerializer(serializers.Serializer):
    file = serializers.ListField(child=serializers.CharField())


class PdfToMarkdownView(APIView):
    parser_classes = [MultiPartParser]

    @extend_schema(
        tags=["Documents"],
        summary="Convert a PDF document to Markdown",
        request=PdfToMarkdownInputSerializer,
        responses={
            200: PdfToMarkdownOutputSerializer,
            400: OpenApiResponse(
                response=PdfConversionErrorSerializer,
                description="The uploaded PDF is invalid or could not be converted.",
            ),
        },
    )
    def post(self, request: Request) -> Response:
        serializer = PdfToMarkdownInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        uploaded_file = serializer.validated_data["file"]
        use_case = ConvertPdfToMarkdown(converter=PyMuPDFMarkdownConverter())

        try:
            result = use_case.execute(
                filename=uploaded_file.name,
                content=uploaded_file.read(),
            )
        except DocumentConversionError as exc:
            raise ValidationError({"file": [str(exc)]}) from exc

        output = PdfToMarkdownOutputSerializer(result)
        return Response(output.data, status=status.HTTP_200_OK)
