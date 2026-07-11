from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import serializers, status
from rest_framework.exceptions import APIException, NotFound, ValidationError
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.documents.application.use_cases import (
    ConvertPdfToMarkdown,
    DocumentConversionError,
    DocumentStorageError,
    GetStoredPdfDocument,
    ListStoredPdfDocuments,
    SavePdfDocument,
    StoredPdfNotFoundError,
)
from apps.documents.infrastructure.pdf_to_markdown import PyMuPDFMarkdownConverter
from apps.documents.infrastructure.storage import get_pdf_document_storage
from apps.documents.interfaces.serializers import (
    PdfToMarkdownInputSerializer,
    PdfToMarkdownOutputSerializer,
    StoredPdfInputSerializer,
    StoredPdfOutputSerializer,
)


class PdfConversionErrorSerializer(serializers.Serializer):
    file = serializers.ListField(child=serializers.CharField())


class PdfStorageApiError(APIException):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    default_detail = "The PDF storage backend could not complete the operation."
    default_code = "pdf_storage_error"


class PdfToMarkdownView(APIView):
    """Public lab endpoint for Syllabus Lab while institutional auth is not available."""

    authentication_classes: list[type] = []
    permission_classes = [AllowAny]
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


class StoredPdfListCreateView(APIView):
    parser_classes = [MultiPartParser]

    @extend_schema(
        tags=["Documents"],
        summary="List stored PDF documents",
        responses={200: StoredPdfOutputSerializer(many=True)},
    )
    def get(self, request: Request) -> Response:
        try:
            use_case = ListStoredPdfDocuments(storage=get_pdf_document_storage())
            documents = use_case.execute()
        except DocumentStorageError as exc:
            raise PdfStorageApiError(str(exc)) from exc

        return Response(StoredPdfOutputSerializer(documents, many=True).data)

    @extend_schema(
        tags=["Documents"],
        summary="Store a PDF document",
        request=StoredPdfInputSerializer,
        responses={
            201: StoredPdfOutputSerializer,
            400: OpenApiResponse(
                response=PdfConversionErrorSerializer,
                description="The uploaded PDF is invalid or could not be stored.",
            ),
        },
    )
    def post(self, request: Request) -> Response:
        serializer = StoredPdfInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        uploaded_file = serializer.validated_data["file"]

        try:
            use_case = SavePdfDocument(storage=get_pdf_document_storage())
            document = use_case.execute(
                filename=uploaded_file.name,
                content=uploaded_file.read(),
                content_type=uploaded_file.content_type,
            )
        except DocumentConversionError as exc:
            raise ValidationError({"file": [str(exc)]}) from exc
        except DocumentStorageError as exc:
            raise PdfStorageApiError(str(exc)) from exc

        return Response(StoredPdfOutputSerializer(document).data, status=status.HTTP_201_CREATED)


class StoredPdfDetailView(APIView):
    @extend_schema(
        tags=["Documents"],
        summary="Get stored PDF document metadata",
        responses={200: StoredPdfOutputSerializer, 404: OpenApiResponse(description="Not found")},
    )
    def get(self, request: Request, document_id: str) -> Response:
        try:
            use_case = GetStoredPdfDocument(storage=get_pdf_document_storage())
            document = use_case.execute(document_id=document_id)
        except StoredPdfNotFoundError as exc:
            raise NotFound(str(exc)) from exc
        except DocumentStorageError as exc:
            raise PdfStorageApiError(str(exc)) from exc

        return Response(StoredPdfOutputSerializer(document).data)
