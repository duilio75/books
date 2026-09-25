from django.test import TestCase, Client, override_settings
from django.urls import reverse

from users.models import CookieConsent


@override_settings(SECURE_SSL_REDIRECT=False, COOKIE_CONSENT_VERSION="1")
class CookieConsentTests(TestCase):
    def setUp(self):
        self.client = Client()

    def post(self, **data):
        return self.client.post(reverse("cookie_consent"), data)

    def granted(self):
        return self.client.get(reverse("cookie_policy")).context["cookie_consent"]["granted"]

    def test_banner_shown_until_choice(self):
        r = self.client.get(reverse("cookie_policy"))
        self.assertFalse(r.context["cookie_consent"]["given"])
        self.assertContains(r, 'id="cookie-banner"')

        self.post(action="reject_all")
        r = self.client.get(reverse("cookie_policy"))
        self.assertTrue(r.context["cookie_consent"]["given"])

    def test_nothing_granted_by_default(self):
        self.assertEqual(self.granted(), {"analytics": False, "marketing": False})

    def test_accept_all(self):
        self.post(action="accept_all")
        self.assertEqual(self.granted(), {"analytics": True, "marketing": True})

    def test_save_keeps_only_known_categories(self):
        self.post(action="save", categories=["analytics", "bogus"])
        self.assertEqual(self.granted(), {"analytics": True, "marketing": False})

    def test_withdraw_keeps_consent_id_and_logs_each_choice(self):
        self.post(action="accept_all")
        self.post(action="reject_all")
        self.assertEqual(self.granted(), {"analytics": False, "marketing": False})
        rows = CookieConsent.objects.order_by("created_at")
        self.assertEqual([row.granted for row in rows], [["analytics", "marketing"], []])
        self.assertEqual(rows[0].consent_id, rows[1].consent_id)

    def test_new_version_asks_again(self):
        self.post(action="accept_all")
        with self.settings(COOKIE_CONSENT_VERSION="2"):
            r = self.client.get(reverse("cookie_policy"))
        self.assertFalse(r.context["cookie_consent"]["given"])

    def test_redirects_back_but_not_offsite(self):
        r = self.post(action="reject_all", next="/books/")
        self.assertEqual(r["Location"], "/books/")
        r = self.post(action="reject_all", next="https://evil.example/")
        self.assertEqual(r["Location"], "/")

    def test_json_response_for_fetch(self):
        r = self.client.post(reverse("cookie_consent"), {"action": "accept_all"},
                             HTTP_ACCEPT="application/json")
        self.assertEqual(r.json(), {"granted": ["analytics", "marketing"]})
        self.assertTrue(r.cookies["cookie_consent"]["httponly"])

    def test_get_not_allowed(self):
        self.assertEqual(self.client.get(reverse("cookie_consent")).status_code, 405)
