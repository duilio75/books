import requests
from django.conf import settings
from django.core.paginator import Paginator
from django.db.models import Avg, Count
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from rest_framework import generics
from rest_framework.authentication import SessionAuthentication
from rest_framework_simplejwt.authentication import JWTAuthentication
from api.models import ContentBlock
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
    params = {
        "title": query,
        "limit": 8,
        "fields": "key,title,author_name,cover_i,isbn,first_sentence",
    }
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
        first_sentences = doc.get("first_sentence", [])
        items.append({
            "id": volume_id,
            "volumeInfo": {
                "title": doc.get("title", ""),
                "authors": doc.get("author_name", []),
                "description": first_sentences[0] if first_sentences else "",
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
    # Anyone may post a review, but authenticate anyway so a logged-in visitor is
    # recorded as the owner instead of falling through to anonymous.
    authentication_classes = [SessionAuthentication, JWTAuthentication]
    permission_classes = []

    def perform_create(self, serializer):
        data = serializer.validated_data
        description = data.pop("description", "")
        book, _ = Book.objects.get_or_create(
            volume=data.get("volume_id", ""),
            defaults={
                "title": data.get("title", ""),
                "author": data.get("author", ""),
                "cover_url": data.get("cover_url", ""),
                "description": description,
            },
        )
        user = self.request.user
        serializer.save(book=book, owner=user if user.is_authenticated else None)


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


BOOKS_PER_PAGE = 50


def books_page(request):
    """Render the paginated catalog at /books/, 50 books per page."""
    books = (
        Book.objects.annotate(
            review_count=Count("reviews"),
            average_rating=Avg("reviews__rating"),
        )
        .order_by("title", "pk")
    )

    paginator = Paginator(books, BOOKS_PER_PAGE)
    # An out-of-range or non-numeric ?page= falls back to the last/first page
    # instead of raising, so a stale link still renders something.
    page_obj = paginator.get_page(request.GET.get("page"))

    return render(
        request,
        "partials/books_page.html",
        {
            "page_obj": page_obj,
            "paginator": paginator,
            "books": page_obj.object_list,
            # Built here because the template can't pass the current page number
            # to get_elided_page_range().
            "page_range": paginator.get_elided_page_range(page_obj.number),
        },
    )


def search_page(request):
    """Render the standalone /search/ page.

    Reuses the same include (and JS component) as the home page; an optional
    ?q= pre-fills the input so the header search box can link here.
    """
    return render(
        request,
        "partials/search_page.html",
        {"search_query": request.GET.get("q", "").strip()},
    )


def home_page_detail(request):
    """Render the home page, featuring the 4 books with the most reviews
    and the ContentBlock configured via the DEFAULT_HOME_BLOCK env var.
    """
    featured_books = (
        Book.objects.annotate(
            review_count=Count("reviews"),
            average_rating=Avg("reviews__rating"),
        )
        .filter(review_count__gt=0)
        .order_by("-review_count")[:4]
    )

    home_block = None
    if settings.DEFAULT_HOME_BLOCK:
        home_block = ContentBlock.objects.filter(pk=settings.DEFAULT_HOME_BLOCK).first()


    sub_block = None
    if settings.SUB_HOME_BLOCK:
        sub_block = ContentBlock.objects.filter(pk=settings.SUB_HOME_BLOCK).first()



    return render(
        request,
        "partials/home.html",
        {"featured_books": featured_books, "home_block": home_block, "sub_block": sub_block},
    )


class BookListCreate(generics.ListCreateAPIView):
    queryset = Book.objects.all()
    serializer_class = BookSerializer


class BookDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
