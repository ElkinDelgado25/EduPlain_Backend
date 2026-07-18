from rest_framework import serializers

MAX_PDF_UPLOAD_SIZE_MB = 10
MAX_PDF_UPLOAD_SIZE_BYTES = MAX_PDF_UPLOAD_SIZE_MB * 1024 * 1024


class SyllabusAnalyzeInputSerializer(serializers.Serializer):
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


class SyllabusTopicDraftOutputSerializer(serializers.Serializer):
    title = serializers.CharField(read_only=True)
    subtopics = serializers.ListField(child=serializers.CharField(), read_only=True)


class SyllabusUnitDraftOutputSerializer(serializers.Serializer):
    number = serializers.IntegerField(read_only=True)
    title = serializers.CharField(read_only=True)
    topics = SyllabusTopicDraftOutputSerializer(many=True, read_only=True)


class SyllabusAnalysisDraftOutputSerializer(serializers.Serializer):
    course_name = serializers.CharField(read_only=True, allow_null=True)
    general_objective = serializers.CharField(read_only=True, allow_null=True)
    units = SyllabusUnitDraftOutputSerializer(many=True, read_only=True)
    confidence = serializers.CharField(read_only=True)
    notes = serializers.CharField(read_only=True)


class SyllabusAnalysisResultOutputSerializer(serializers.Serializer):
    status = serializers.CharField(read_only=True)
    filename = serializers.CharField(read_only=True)
    characters_extracted = serializers.IntegerField(read_only=True)
    markdown_preview = serializers.CharField(read_only=True)
    analysis = SyllabusAnalysisDraftOutputSerializer(read_only=True)
    phase = serializers.IntegerField(read_only=True)
    agent = serializers.CharField(read_only=True)
    version = serializers.CharField(read_only=True)
    steps_completed = serializers.ListField(child=serializers.CharField(), read_only=True)
