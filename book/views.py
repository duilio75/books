from django.shortcuts import render, get_object_or_404
from rest_framework import generics
from .models import Book
from .serializers import BookSerializer


def book_page_detail(request, url_alias):
    """Render a Book as a full HTML page, looked up by its url_alias."""
    book = get_object_or_404(Book, url_alias=url_alias)
    return render(request, "partials/book_page.html", {"book": book})


class BookListCreate(generics.ListCreateAPIView):
    queryset = Book.objects.all()
    serializer_class = BookSerializer


class BookDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
