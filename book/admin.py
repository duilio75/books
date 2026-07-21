from django.contrib import admin
from .models import Book, BookLabel, BookTopic, Source, Edition


class BookLabelInline(admin.TabularInline):
    model = BookLabel
    extra = 1


class BookTopicInline(admin.TabularInline):
    model = BookTopic
    extra = 1


class SourceInline(admin.TabularInline):
    model = Source
    extra = 1


class EditionInline(admin.TabularInline):
    model = Edition
    extra = 1


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ("title", "author", "volume", "published_year", "created_at")
    search_fields = ("title", "author", "volume")
    inlines = [BookLabelInline, BookTopicInline, SourceInline, EditionInline]


@admin.register(BookLabel)
class BookLabelAdmin(admin.ModelAdmin):
    list_display = ("label", "book")
    search_fields = ("label",)


@admin.register(BookTopic)
class BookTopicAdmin(admin.ModelAdmin):
    list_display = ("topic", "book")
    search_fields = ("topic",)


@admin.register(Source)
class SourceAdmin(admin.ModelAdmin):
    list_display = ("url", "book", "source_name", "type", "verified")
    list_filter = ("verified", "type")
    search_fields = ("url", "source_name")


@admin.register(Edition)
class EditionAdmin(admin.ModelAdmin):
    list_display = ("book", "format", "publisher", "isbn13", "isbn10", "publication_date")
    list_filter = ("format", "language")
    search_fields = ("isbn13", "isbn10", "publisher")
