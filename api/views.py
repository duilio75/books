import os
import uuid

from django.contrib.admin.views.decorators import staff_member_required
from django.core.files.storage import default_storage
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from django.contrib.auth.models import User
from rest_framework import generics
from .serializers import UserSerializer, NoteSerializer
from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import Note, BasicPage


def basic_page_detail(request, url_alias):
    """Render a BasicPage as a full HTML page, looked up by its url_alias."""
    page = get_object_or_404(BasicPage, url_alias=url_alias)
    return render(request, "partials/basic_page.html", {"page": page})


ALLOWED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg"}
MAX_IMAGE_UPLOAD_SIZE = 5 * 1024 * 1024  # 5MB


@csrf_exempt
@require_POST
@staff_member_required
def tinymce_upload_image(request):
    """Image upload endpoint for the TinyMCE editor used in the Django admin.

    TinyMCE's built-in upload doesn't send a CSRF token, so this view is
    csrf_exempt and instead relies on the admin session (staff_member_required)
    for access control.
    """
    upload = request.FILES.get("file")
    if upload is None:
        return JsonResponse({"error": "No file provided."}, status=400)

    ext = os.path.splitext(upload.name)[1].lower()
    if ext not in ALLOWED_IMAGE_EXTENSIONS:
        return JsonResponse({"error": "Unsupported file type."}, status=400)

    if upload.size > MAX_IMAGE_UPLOAD_SIZE:
        return JsonResponse({"error": "File too large."}, status=400)

    filename = f"{uuid.uuid4().hex}{ext}"
    saved_path = default_storage.save(f"tinymce_uploads/{filename}", upload)
    return JsonResponse({"location": default_storage.url(saved_path)})


class NoteListCreate(generics.ListCreateAPIView):
    serializer_class = NoteSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Note.objects.filter(author=user)

    def perform_create(self, serializer):
        if serializer.is_valid():
            serializer.save(author=self.request.user)
        else:
            print(serializer.errors)


class NoteDelete(generics.DestroyAPIView):
    serializer_class = NoteSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Note.objects.filter(author=user)


class CreateUserView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]
