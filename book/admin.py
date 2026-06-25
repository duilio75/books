from django.contrib import admin
from .models import Book, BookLabel, BookTopic, Source


class BookLabelInline(admin.TabularInline):
    model = BookLabel
    extra = 1


class BookTopicInline(admin.TabularInline):
    model = BookTopic
    extra = 1


class SourceInline(admin.TabularInline):
    model = Source
    extra = 1


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ("title", "author", "isbn", "published_year", "created_at")
    search_fields = ("title", "author", "isbn")
    inlines = [BookLabelInline, BookTopicInline, SourceInline]


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
