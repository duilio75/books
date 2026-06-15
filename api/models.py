from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from tinymce.models import HTMLField



class BasicPage(models.Model):
        title = models.CharField(max_length=200)
        subtitle = models.CharField(max_length=300, blank=True)
        image = models.ImageField(upload_to="basic_pages/", blank=True, null=True)
        body = HTMLField()
        # Filled automatically from the title; unique so two pages can't collide.
        url_alias = models.SlugField(max_length=255, unique=True, blank=True)
        created_at = models.DateTimeField(auto_now_add=True)
        updated_at = models.DateTimeField(auto_now=True)

        def save(self, *args, **kwargs):
            # slugify() lower-cases, strips accents to ASCII, and turns
            # spaces (and other separators) into dashes:
            #   "My First Page" -> "my-first-page"
            base = slugify(self.title)
            alias = base
            counter = 1
            # Guarantee uniqueness by appending -2, -3, ... if needed.
            qs = BasicPage.objects.exclude(pk=self.pk)
            while qs.filter(url_alias=alias).exists():
                counter += 1
                alias = f"{base}-{counter}"
            self.url_alias = alias
            super().save(*args, **kwargs)

        def __str__(self):
            return self.title




class Note(models.Model):
    title = models.CharField(max_length=100)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notes")

    def __str__(self):
        return self.title