"""Cookie consent state (GDPR + ePrivacy Directive art. 5(3)).

The visitor's choice lives in the ``settings.COOKIE_CONSENT_NAME`` cookie as
``<version>|<consent id>|<timestamp>|<granted categories joined by +>``. A
cookie written for another ``COOKIE_CONSENT_VERSION`` counts as no choice, so
the banner is shown again.
"""

import time
import uuid

from django.conf import settings


def category_keys():
    return [category["key"] for category in settings.COOKIE_CONSENT_CATEGORIES]


def read_consent(request):
    """The stored choice as ``{"id": UUID, "granted": [keys]}``, or None."""
    raw = request.COOKIES.get(settings.COOKIE_CONSENT_NAME, "")
    parts = raw.split("|")
    if len(parts) != 4 or parts[0] != settings.COOKIE_CONSENT_VERSION:
        return None
    try:
        consent_id = uuid.UUID(parts[1])
    except ValueError:
        return None
    keys = category_keys()
    return {
        "id": consent_id,
        "granted": [key for key in parts[3].split("+") if key in keys],
    }


def write_consent(response, consent_id, granted):
    value = "|".join(
        (settings.COOKIE_CONSENT_VERSION, str(consent_id), str(int(time.time())), "+".join(granted))
    )
    response.set_cookie(
        settings.COOKIE_CONSENT_NAME,
        value,
        max_age=settings.COOKIE_CONSENT_MAX_AGE,
        secure=settings.SESSION_COOKIE_SECURE,
        httponly=True,
        samesite="Lax",
    )


def cookie_consent(request):
    """Template context: whether the visitor chose, and what they granted.

    ``cookie_consent.granted.<key>`` lets templates load optional scripts
    server-side, e.g. ``{% if cookie_consent.granted.analytics %}``.
    """
    consent = read_consent(request)
    granted = consent["granted"] if consent else []
    return {
        "cookie_consent": {
            "given": consent is not None,
            "granted": {key: key in granted for key in category_keys()},
            "granted_list": granted,
            "categories": [
                {**category, "granted": category["key"] in granted}
                for category in settings.COOKIE_CONSENT_CATEGORIES
            ],
        }
    }
