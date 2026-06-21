from django.urls import path

from .views import PdfToMarkdownView

app_name = "documents"

urlpatterns = [
    path("pdf-to-markdown/", PdfToMarkdownView.as_view(), name="pdf-to-markdown"),
]
