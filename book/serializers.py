from rest_framework import serializers
from .models import Book, BookLabel, BookTopic, Source


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


class BookSerializer(serializers.ModelSerializer):
    labels = BookLabelSerializer(many=True, read_only=True)
    topics = BookTopicSerializer(many=True, read_only=True)
    sources = SourceSerializer(many=True, read_only=True)

    class Meta:
        model = Book
        fields = [
            "id",
            "title",
            "isbn",
            "author",
            "cover_url",
            "description",
            "published_year",
            "created_at",
            "labels",
            "topics",
            "sources",
        ]
