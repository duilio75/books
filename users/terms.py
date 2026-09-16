"""Helpers for resolving which legal documents a user still has to accept.

The set of documents that gate access is configured by
``settings.REQUIRED_TERMS_TYPES`` (a list of ``TermsVersion.Type`` values) and
validated at startup by ``users.apps.check_required_terms_types``.
"""

from django.conf import settings

from .models import TermsVersion, TermsAcceptance


def active_required_documents():
    """The active TermsVersion for each type in REQUIRED_TERMS_TYPES.

    Types with no active version are skipped, so an unpublished document does
    not lock everybody out of the site.
    """
    documents = []
    for doc_type in settings.REQUIRED_TERMS_TYPES:
        document = (
            TermsVersion.objects.filter(type=doc_type, is_active=True)
            .order_by("-published_at")
            .first()
        )
        if document:
            documents.append(document)
    return documents


def outstanding_documents(user):
    """Required documents whose current version `user` has not yet accepted.

    A document counts as accepted only when the user has an acceptance for that
    document type carrying the same version string as the active version, so
    publishing a new version re-gates every user.
    """
    accepted = set(
        TermsAcceptance.objects.filter(user=user).values_list("terms__type", "version")
    )
    return [
        document
        for document in active_required_documents()
        if (document.type, document.version) not in accepted
    ]


def record_acceptance(user, document, ip_address=None):
    """Store `user`'s acceptance of `document`, snapshotting its version."""
    return TermsAcceptance.objects.get_or_create(
        user=user,
        terms=document,
        defaults={"version": document.version, "ip_address": ip_address},
    )
