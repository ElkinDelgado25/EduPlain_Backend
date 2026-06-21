from rest_framework import serializers

MAX_PDF_UPLOAD_SIZE_BYTES = 10 * 1024 * 1024


class PdfToMarkdownInputSerializer(serializers.Serializer):
    file = serializers.FileField()

    def validate_file(self, uploaded_file):
        filename = uploaded_file.name or ""
        if not filename.lower().endswith(".pdf"):
            raise serializers.ValidationError("Only PDF files are supported.")
        if uploaded_file.size > MAX_PDF_UPLOAD_SIZE_BYTES:
            raise serializers.ValidationError("PDF files must be 10 MB or smaller.")
        return uploaded_file


class PdfToMarkdownOutputSerializer(serializers.Serializer):
    filename = serializers.CharField(read_only=True)
    characters = serializers.IntegerField(read_only=True)
    markdown = serializers.CharField(read_only=True)
