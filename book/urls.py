from django.urls import path
from . import views

urlpatterns = [
    path("books/", views.BookListCreate.as_view(), name="book-list"),
    path("books/<uuid:pk>/", views.BookDetail.as_view(), name="book-detail"),
]
