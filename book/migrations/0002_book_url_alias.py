from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('book', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='book',
            name='url_alias',
            field=models.SlugField(blank=True, max_length=255, unique=True),
        ),
    ]
