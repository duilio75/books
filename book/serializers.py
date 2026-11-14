from rest_framework import serializers
from .models import Book, BookLabel, BookTopic, BookReview, Source, Edition


class BookLabelSerializer(serializers.ModelSerializer):
    class Meta:
        model = BookLabel
        fields = ["id", "label"]


class BookTopicSerializer(serializers.ModelSerializer):
    class Meta:
        model = BookTopic
        fields = ["id", "topic"]


class SourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Source
        fields = ["id", "source_name", "url", "type", "verified", "format", "added_at"]


class BookReviewSerializer(serializers.ModelSerializer):
    description = serializers.CharField(write_only=True, required=False, allow_blank=True)
    # Year from the search results (e.g. "1991"), used to fill Book.published_year.
    published_date = serializers.CharField(write_only=True, required=False, allow_blank=True)
    # Always the user's id, or 0 when the review was left anonymously. Set from
    # request.user in the view, never from the payload.
    owner = serializers.IntegerField(source="owner_ref", read_only=True)
    # The reviewed book's page slug (/book/<alias>/), named like the search
    # results' _url_alias. The book may have just been created by this review.
    _url_alias = serializers.CharField(source="book.url_alias", read_only=True)

    class Meta:
        model = BookReview
        fields = [
            "id", "book", "owner", "volume_id", "title", "author",
            "cover_url", "rating", "review_text", "created_at",
            "description", "published_date", "_url_alias",
        ]
        read_only_fields = ["id", "book", "owner", "created_at"]

    def validate_rating(self, value):
        if not 1 <= value <= 5:
            raise serializers.ValidationError("Rating must be between 1 and 5.")
        return value


class EditionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Edition
        fields = [
            "id", "book", "isbn13", "isbn10", "publisher", "language",
            "format", "publication_date", "page_count", "cover_url",
        ]
        read_only_fields = ["id"]


class BookSerializer(serializers.ModelSerializer):
    labels = BookLabelSerializer(many=True, read_only=True)
    topics = BookTopicSerializer(many=True, read_only=True)
    sources = SourceSerializer(many=True, read_only=True)
    editions = EditionSerializer(many=True, read_only=True)

    class Meta:
        model = Book
        fields = [
            "id",
            "title",
            "volume",
            "author",
            "cover_url",
            "description",
            "published_year",
            "created_at",
            "labels",
            "topics",
            "sources",
            "editions",
        ]
