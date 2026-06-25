import uuid

from django.db import models
from django.utils.text import slugify
from tinymce.models import HTMLField


class Book(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    isbn = models.CharField(max_length=255)
    author = models.CharField(max_length=75)
    cover_url = models.CharField(max_length=255)
    description = HTMLField()
    published_year = models.IntegerField(blank=True, null=True)
    # ASCII slug derived from the title, e.g. "Café Society" -> "cafe-society".
    url_alias = models.SlugField(max_length=255, unique=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        base = slugify(self.url_alias) if self.url_alias else slugify(self.title)
        alias = base
        counter = 1
        qs = Book.objects.exclude(pk=self.pk)
        while qs.filter(url_alias=alias).exists():
            counter += 1
            alias = f"{base}-{counter}"
        self.url_alias = alias
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class BookLabel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name="labels")
    label = models.CharField(max_length=255)

    class Meta:
        unique_together = ("book", "label")

    def __str__(self):
        return self.label


class BookTopic(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name="topics")
    topic = models.CharField(max_length=255)

    class Meta:
        unique_together = ("book", "topic")

    def __str__(self):
        return self.topic


class Source(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name="sources")
    source_name = models.TextField(blank=True, null=True)
    url = models.CharField(max_length=255)
    type = models.CharField(max_length=255)
    verified = models.BooleanField(default=False)
    format = models.CharField(max_length=255)
    added_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.url
