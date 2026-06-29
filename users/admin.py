from django.contrib import admin
from .models import TermsVersion, TermsAcceptance

# Register your models here.


@admin.register(TermsVersion)
class TermsVersionAdmin(admin.ModelAdmin):
    list_display = ("version", "is_active", "published_at")
    list_filter = ("is_active", "published_at")
    search_fields = ("version", "content")
    readonly_fields = ("published_at",)
    ordering = ("-published_at",)

    actions = ["make_active"]

    @admin.action(description="Make selected version active")
    def make_active(self, request, queryset):
        selected = queryset.first()

        if selected:
            TermsVersion.objects.update(is_active=False)
            selected.is_active = True
            selected.save()


@admin.register(TermsAcceptance)
class TermsAcceptanceAdmin(admin.ModelAdmin):
    list_display = ("user", "terms", "accepted_at", "ip_address")
    list_filter = ("terms", "accepted_at")
    search_fields = (
        "user__username",
        "user__email",
        "terms__version",
        "ip_address",
    )
    readonly_fields = ("user", "terms", "accepted_at", "ip_address")
    ordering = ("-accepted_at",)

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False