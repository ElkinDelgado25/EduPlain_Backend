from drf_spectacular.utils import extend_schema
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.users.application.use_cases import ListPublicUsers
from apps.users.infrastructure.repositories import DjangoPublicUserRepository
from apps.users.interfaces.serializers import PublicUserSerializer


class PublicUserListView(APIView):
    """Public REST adapter. Authentication is intentionally disabled for now."""

    authentication_classes: list[type] = []
    permission_classes = [AllowAny]

    @extend_schema(
        tags=["Users"],
        summary="List public users",
        responses={200: PublicUserSerializer(many=True)},
    )
    def get(self, request: Request) -> Response:
        use_case = ListPublicUsers(repository=DjangoPublicUserRepository())
        users = use_case.execute()
        return Response(PublicUserSerializer(users, many=True).data)
