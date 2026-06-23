from django.urls import path

from .views import PdfToMarkdownView, StoredPdfDetailView, StoredPdfListCreateView

app_name = "documents"

urlpatterns = [
    path("pdf-to-markdown/", PdfToMarkdownView.as_view(), name="pdf-to-markdown"),
    path("pdfs/", StoredPdfListCreateView.as_view(), name="pdf-list"),
    path("pdfs/<str:document_id>/", StoredPdfDetailView.as_view(), name="pdf-detail"),
]
