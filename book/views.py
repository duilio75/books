import requests
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from rest_framework import generics
from common.http import session_with_retries
from .models import Book
from .serializers import BookSerializer, BookReviewSerializer


def google_books_search(request):
    """Search books by title via the Open Library API.

    Kept the historical name/URL (see book/urls.py) and Google-Books-like
    response shape (items[].volumeInfo...) so the existing frontend
    (frontend/src/components/search-book.js) keeps working unchanged.
    """
    query = request.GET.get("q", "").strip()
    if not query:
        return JsonResponse({"error": "Missing query"}, status=400)
    params = {"title": query, "limit": 8, "fields": "key,title,author_name,cover_i,isbn"}
    try:
        resp = session_with_retries().get(
            "https://openlibrary.org/search.json",
            params=params,
            timeout=20,
        )
    except requests.RequestException as exc:
        return JsonResponse({"error": {"message": str(exc)}}, status=502)

    if not resp.ok:
        return JsonResponse(
            {"error": {"code": resp.status_code, "message": "Open Library request failed."}},
            status=resp.status_code,
        )

    docs = resp.json().get("docs", [])

    # single query — map volume key → url_alias for matched books
    volume_to_alias = {
        b.volume: b.url_alias
        for b in Book.objects.filter(
            volume__in=[doc.get("key", "") for doc in docs]
        ).only("volume", "url_alias")
    }

    items = []
    for doc in docs:
        volume_id = doc.get("key", "")
        isbns = doc.get("isbn", [])
        cover_id = doc.get("cover_i")
        items.append({
            "id": volume_id,
            "volumeInfo": {
                "title": doc.get("title", ""),
                "authors": doc.get("author_name", []),
                "industryIdentifiers": [
                    {"type": "ISBN", "identifier": isbn} for isbn in isbns[:5]
                ],
                "imageLinks": (
                    {"thumbnail": f"https://covers.openlibrary.org/b/id/{cover_id}-M.jpg"}
                    if cover_id else {}
                ),
            },
            "_in_db": volume_id in volume_to_alias,
            "_url_alias": volume_to_alias.get(volume_id),
        })

    return JsonResponse({"items": items}, status=200)


class BookReviewCreate(generics.CreateAPIView):
    serializer_class = BookReviewSerializer
    authentication_classes = []
    permission_classes = []

    def perform_create(self, serializer):
        data = serializer.validated_data
        s = ''
        print("BookReview payload before create:", data)
        book, _ = Book.objects.get_or_create(
            volume=data.get("volume_id", ""),
            defaults={
                "title": data.get("title", ""),
                "author": data.get("author", ""),
                "cover_url": data.get("cover_url", ""),
                "description": "",
            },
        )
        serializer.save(book=book)


def book_page_detail(request, url_alias):
    """Render a Book as a full HTML page, looked up by its url_alias."""
    book = get_object_or_404(
        Book.objects.prefetch_related("reviews"), url_alias=url_alias
    )
    return render(
        request,
        "partials/book_page.html",
        {"book": book, "reviews": book.reviews.all()},
    )


class BookListCreate(generics.ListCreateAPIView):
    queryset = Book.objects.all()
    serializer_class = BookSerializer


class BookDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
