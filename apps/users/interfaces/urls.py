from django.urls import path

from .views import PublicUserListView

app_name = "users"

urlpatterns = [
    path("public/", PublicUserListView.as_view(), name="public-list"),
]
