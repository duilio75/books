import os
import requests
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from rest_framework import generics
from .models import Book
from .serializers import BookSerializer, BookReviewSerializer


def google_books_search(request):
    query = request.GET.get("q", "").strip()
    if not query:
        return JsonResponse({"error": "Missing query"}, status=400)
    api_key = os.getenv("GOOGLE_BOOKS_API_KEY", "")
    params = {"q": query, "maxResults": 12}
    if api_key:
        params["key"] = api_key
    country = request.GET.get("country", "").strip().upper()
    if country:
        params["country"] = country
    try:
        resp = requests.get(
            "https://www.googleapis.com/books/v1/volumes",
            params=params,
            timeout=10,
        )
        data = resp.json()
        if resp.ok and data.get("items"):
            # collect every ISBN that appears across all results
            all_isbns = set()
            for item in data["items"]:
                for id_entry in item.get("volumeInfo", {}).get("industryIdentifiers", []):
                    all_isbns.add(id_entry.get("identifier", "").strip())

            # single query — map isbn → url_alias for matched books
            isbn_to_alias = {
                b.isbn: b.url_alias
                for b in Book.objects.filter(isbn__in=all_isbns).only("isbn", "url_alias")
            }

            for item in data["items"]:
                isbns = [
                    e.get("identifier", "").strip()
                    for e in item.get("volumeInfo", {}).get("industryIdentifiers", [])
                ]
                matched_alias = next(
                    (isbn_to_alias[isbn] for isbn in isbns if isbn in isbn_to_alias),
                    None,
                )
                item["_in_db"] = matched_alias is not None
                item["_url_alias"] = matched_alias

        return JsonResponse(data, status=resp.status_code)
    except requests.RequestException as exc:
        return JsonResponse({"error": str(exc)}, status=502)


class BookReviewCreate(generics.CreateAPIView):
    serializer_class = BookReviewSerializer
    authentication_classes = []
    permission_classes = []


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
