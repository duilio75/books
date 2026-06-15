from django.contrib import admin
from .models import BasicPage



# Register your models here.

@admin.register(BasicPage)
class BasicPageAdmin(admin.ModelAdmin):
    list_display = ("title", "url_alias", "created_at")
    # url_alias is auto-generated, so show it read-only.
    readonly_fields = ("url_alias", "created_at", "updated_at")
    search_fields = ("title", "subtitle", "body")