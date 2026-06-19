from django.conf import settings
from drf_spectacular.utils import OpenApiExample, extend_schema, inline_serializer
from rest_framework import serializers, status
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView


class HealthCheckView(APIView):
    """Public HTTP adapter used by people and infrastructure probes."""

    authentication_classes: list[type] = []
    permission_classes = [AllowAny]

    @extend_schema(
        tags=["Health"],
        summary="Check service health",
        responses={
            200: inline_serializer(
                name="HealthResponse",
                fields={
                    "status": serializers.CharField(),
                    "service": serializers.CharField(),
                    "environment": serializers.CharField(),
                },
            )
        },
        examples=[
            OpenApiExample(
                "Healthy service",
                value={
                    "status": "ok",
                    "service": "eduplain-backend",
                    "environment": "development",
                },
                response_only=True,
            )
        ],
    )
    def get(self, request: Request) -> Response:
        return Response(
            {
                "status": "ok",
                "service": "eduplain-backend",
                "environment": settings.ENVIRONMENT,
            },
            status=status.HTTP_200_OK,
        )
