from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.test import override_settings

from users.models import TermsVersion, TermsAcceptance
from users.terms import outstanding_documents


@override_settings(REQUIRED_TERMS_TYPES=["terms_of_service", "privacy_policy"],
                   SECURE_SSL_REDIRECT=False)
class TermsGateTests(TestCase):
    def setUp(self):
        self.tos_v1 = TermsVersion.objects.create(
            version="10", title="ToS", type="terms_of_service",
            content="tos body", is_active=True)
        self.pp_v1 = TermsVersion.objects.create(
            version="11", title="PP", type="privacy_policy",
            content="pp body", is_active=True)
        self.user = User.objects.create_user("gate_user", "g@e.com", "pw12345!x")
        self.client = Client()
        self.client.force_login(self.user)

    def test_both_outstanding_initially(self):
        self.assertEqual(len(outstanding_documents(self.user)), 2)

    def test_middleware_redirects_to_dashboard(self):
        r = self.client.get("/books/")
        self.assertEqual(r.status_code, 302)
        self.assertEqual(r["Location"], reverse("dashboard"))

    def test_document_pages_not_gated(self):
        for name in ("terms", "policy", "dashboard"):
            self.assertEqual(self.client.get(reverse(name)).status_code, 200, name)

    def test_partial_accept_rejected(self):
        r = self.client.post(reverse("accept_terms"),
                             {"accepted_types": ["terms_of_service"]})
        self.assertEqual(r.status_code, 302)
        self.assertEqual(TermsAcceptance.objects.filter(user=self.user).count(), 0)
        self.assertEqual(len(outstanding_documents(self.user)), 2)

    def test_full_accept_clears_gate(self):
        r = self.client.post(reverse("accept_terms"),
                             {"accepted_types": ["terms_of_service", "privacy_policy"]})
        self.assertEqual(r.status_code, 302)
        self.assertEqual(outstanding_documents(self.user), [])
        self.assertEqual(self.client.get("/books/").status_code, 200)
        versions = set(TermsAcceptance.objects.filter(user=self.user)
                       .values_list("terms__type", "version"))
        self.assertEqual(versions,
                         {("terms_of_service", "10"), ("privacy_policy", "11")})

    def test_new_version_re_gates_user(self):
        self.client.post(reverse("accept_terms"),
                         {"accepted_types": ["terms_of_service", "privacy_policy"]})
        self.assertEqual(self.client.get("/books/").status_code, 200)

        self.tos_v1.is_active = False
        self.tos_v1.save()
        TermsVersion.objects.create(version="12", title="ToS", type="terms_of_service",
                                    content="new tos", is_active=True)

        out = outstanding_documents(self.user)
        self.assertEqual([d.version for d in out], ["12"])
        self.assertEqual(self.client.get("/books/")["Location"], reverse("dashboard"))

    def test_dialog_lists_every_outstanding_document(self):
        html = self.client.get(reverse("dashboard")).content.decode()
        self.assertIn('value="terms_of_service"', html)
        self.assertIn('value="privacy_policy"', html)

    @override_settings(REQUIRED_TERMS_TYPES=["terms_of_service"])
    def test_setting_narrows_what_is_required(self):
        self.assertEqual([d.type for d in outstanding_documents(self.user)],
                         ["terms_of_service"])

    def test_unpublished_type_does_not_lock_out(self):
        self.pp_v1.is_active = False
        self.pp_v1.save()
        self.assertEqual([d.type for d in outstanding_documents(self.user)],
                         ["terms_of_service"])
