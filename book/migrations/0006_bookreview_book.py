from django.db import migrations, models
from django.utils.text import slugify
import django.db.models.deletion


def backfill_book(apps, schema_editor):
    Book = apps.get_model("book", "Book")
    BookReview = apps.get_model("book", "BookReview")
    for review in BookReview.objects.filter(book__isnull=True):
        book = Book.objects.filter(isbn=review.isbn or "").first()
        if book is None:
            base = slugify(review.title)
            alias = base
            counter = 1
            while Book.objects.filter(url_alias=alias).exists():
                counter += 1
                alias = f"{base}-{counter}"
            book = Book.objects.create(
                isbn=review.isbn or "",
                title=review.title,
                author=review.author,
                cover_url=review.cover_url,
                description="",
                url_alias=alias,
            )
        review.book = book
        review.save(update_fields=["book"])


def noop_reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('book', '0005_alter_bookreview_isbn'),
    ]

    operations = [
        migrations.AddField(
            model_name='bookreview',
            name='book',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='reviews', to='book.book'),
        ),
        migrations.RunPython(backfill_book, noop_reverse),
        migrations.AlterField(
            model_name='bookreview',
            name='book',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reviews', to='book.book'),
        ),
    ]
