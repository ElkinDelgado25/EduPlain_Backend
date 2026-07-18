from rest_framework import serializers

MAX_PDF_UPLOAD_SIZE_MB = 10
MAX_PDF_UPLOAD_SIZE_BYTES = MAX_PDF_UPLOAD_SIZE_MB * 1024 * 1024


class PdfToMarkdownInputSerializer(serializers.Serializer):
    file = serializers.FileField()

    def validate_file(self, uploaded_file):
        filename = uploaded_file.name or ""
        if not filename.lower().endswith(".pdf"):
            raise serializers.ValidationError("Only PDF files are supported.")
        if uploaded_file.size > MAX_PDF_UPLOAD_SIZE_BYTES:
            raise serializers.ValidationError(
                f"PDF files must be {MAX_PDF_UPLOAD_SIZE_MB} MB or smaller."
            )
        return uploaded_file


class PdfToMarkdownOutputSerializer(serializers.Serializer):
    filename = serializers.CharField(read_only=True)
    characters = serializers.IntegerField(read_only=True)
    markdown = serializers.CharField(read_only=True)


class StoredPdfInputSerializer(PdfToMarkdownInputSerializer):
    pass


class StoredPdfOutputSerializer(serializers.Serializer):
    id = serializers.CharField(read_only=True)
    filename = serializers.CharField(read_only=True)
    content_type = serializers.CharField(read_only=True)
    size_bytes = serializers.IntegerField(read_only=True)
    storage_backend = serializers.CharField(read_only=True)
    storage_key = serializers.CharField(read_only=True)
    created_at = serializers.CharField(read_only=True)
