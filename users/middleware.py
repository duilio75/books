from django.conf import settings
from django.shortcuts import redirect
from django.urls import reverse

from .terms import outstanding_documents


class TermsMiddleware:
    """Force authenticated users to accept the current required documents.

    Which documents are required comes from ``settings.REQUIRED_TERMS_TYPES``;
    a user is let through only once they have accepted the active version of
    every one of them (see ``users.terms.outstanding_documents``).
    """

    # Reached while the user still has documents outstanding: the acceptance
    # dialog itself, the read-only document pages, and the way back out.
    EXEMPT_URL_NAMES = (
        "dashboard", "accept_terms", "terms", "policy", "logout",
        "cookie_policy", "cookie_consent",
    )

    def __init__(self, get_response):
        self.get_response = get_response
        self._exempt_paths = None

    @property
    def exempt_paths(self):
        # Resolved on first use rather than in __init__ so the middleware does
        # not depend on the URLConf being loaded at instantiation time.
        if self._exempt_paths is None:
            paths = [reverse(name) for name in self.EXEMPT_URL_NAMES]
            paths += ["/admin/", settings.STATIC_URL, settings.MEDIA_URL]
            self._exempt_paths = tuple(path for path in paths if path)
        return self._exempt_paths

    def __call__(self, request):
        user = getattr(request, "user", None)
        if (
            user is not None
            and user.is_authenticated
            and not request.path.startswith(self.exempt_paths)
            and outstanding_documents(user)
        ):
            return redirect("dashboard")

        return self.get_response(request)
