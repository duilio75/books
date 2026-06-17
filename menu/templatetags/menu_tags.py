from django import template
from menu.models import MenuItem

register = template.Library()


@register.inclusion_tag("menu/menu.html")
def render_menu(menu_slug):
    items = (
        MenuItem.objects
        .filter(menu__slug=menu_slug, parent=None, is_active=True)
        .prefetch_related("children")
        .order_by("order")
    )
    return {"items": items}