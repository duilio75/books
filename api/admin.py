from django.contrib import admin
from .models import BasicPage, BasicPageContentBlock, ContentBlock, Faq, Gallery



# Register your models here.

class BasicPageContentBlockInline(admin.TabularInline):
    model = BasicPageContentBlock
    extra = 1


@admin.register(BasicPage)
class BasicPageAdmin(admin.ModelAdmin):
    list_display = ("title", "url_alias", "created_at")
    # url_alias auto-fills from the title if left blank, but can be edited.
    readonly_fields = ("created_at", "updated_at")
    search_fields = ("title", "subtitle", "body")
    filter_horizontal = ("content_faqs",)
    inlines = [BasicPageContentBlockInline]


@admin.register(ContentBlock)
class ContentBlockAdmin(admin.ModelAdmin):
    list_display = ("title", "sub_title")
    search_fields = ("title", "sub_title", "body")


@admin.register(Gallery)
class GalleryAdmin(admin.ModelAdmin):
    list_display = ("title", "alt")
    search_fields = ("title", "alt")


@admin.register(Faq)
class FaqAdmin(admin.ModelAdmin):
    list_display = ("title", "description")
    search_fields = ("title", "description", "answer")
