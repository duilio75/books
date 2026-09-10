from django import template
from menu.models import MenuItem

register = template.Library()


def _is_current(item, current_path):
    """Whether `item` points at the page being rendered.

    An exact match wins; otherwise a menu URL that is a path prefix of the
    request counts too, so /books/register/ also highlights a /books/ entry.
    "/" is matched exactly, since it prefixes everything.
    """
    url = item.get_url()
    if not url or url == "#":
        return False
    if url == current_path:
        return True
    if url == "/":
        return False
    return current_path.startswith(url.rstrip("/") + "/")


@register.inclusion_tag("menu/menu.html", takes_context=True)
def render_menu(context, menu_slug):
    items = list(
        MenuItem.objects
        .filter(menu__slug=menu_slug, parent=None, is_active=True)
        .prefetch_related("children")
        .order_by("order")
    )

    # `request` comes from django.template.context_processors.request; guard
    # anyway so the tag still renders if it is ever called without one.
    request = context.get("request")
    current_path = request.path if request else ""

    for item in items:
        # A parent stays highlighted while one of its children is the open page.
        item.is_current = _is_current(item, current_path) or any(
            _is_current(child, current_path) for child in item.children.all()
        )

    return {"items": items}
