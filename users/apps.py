from django.apps import AppConfig
from django.conf import settings
from django.core.checks import Error, register


class UsersConfig(AppConfig):
    name = 'users'

    def ready(self):
        register(check_required_terms_types)


def check_required_terms_types(app_configs, **kwargs):
    """Guard REQUIRED_TERMS_TYPES against typos and empty configuration.

    An unrecognised value would otherwise match no TermsVersion row, silently
    skipping the acceptance record for that document at registration.
    """
    from .models import TermsVersion

    required = getattr(settings, "REQUIRED_TERMS_TYPES", [])
    if not required:
        return [
            Error(
                "REQUIRED_TERMS_TYPES is empty, so no terms acceptance will be "
                "recorded at registration.",
                hint="Set REQUIRED_TERMS_TYPES in .env, e.g. "
                     "terms_of_service,privacy_policy",
                id="users.E001",
            )
        ]

    valid = set(TermsVersion.Type.values)
    unknown = [t for t in required if t not in valid]
    if unknown:
        return [
            Error(
                f"REQUIRED_TERMS_TYPES contains unknown document types: "
                f"{', '.join(unknown)}.",
                hint=f"Valid values are: {', '.join(sorted(valid))}",
                id="users.E002",
            )
        ]

    return []
