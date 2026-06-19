from rest_framework import serializers


class PublicUserSerializer(serializers.Serializer):
    """Explicit output contract; no persistence-only field can be exposed."""

    id = serializers.IntegerField(read_only=True)
    full_name = serializers.CharField(read_only=True)
    email = serializers.EmailField(read_only=True)
    role = serializers.CharField(read_only=True)
