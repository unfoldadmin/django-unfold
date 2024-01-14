from django.contrib.auth.models import AnonymousUser
from django.templatetags.static import static
from django.test import TestCase
from django.test.client import RequestFactory
from django.test.utils import override_settings
from unfold.settings import CONFIG_DEFAULTS
from unfold.sites import UnfoldAdminSite


class SiteBrandingTestCase(TestCase):
    @override_settings(
        UNFOLD={
            **CONFIG_DEFAULTS,
            **{
                "SITE_ICON": lambda request: static("icon.svg"),
            },
        }
    )
    def test_correct_callback_site_icon(self):
        admin_site = UnfoldAdminSite()
        request = RequestFactory().get("/rand")
        request.user = AnonymousUser()
        context = admin_site.each_context(request)
        self.assertEqual(context["site_icon"], "icon.svg")

    @override_settings(
        UNFOLD={
            **CONFIG_DEFAULTS,
            **{
                "SITE_ICON": "hardcoded-icon.svg",
            },
        }
    )
    def test_correct_string_site_icon(self):
        admin_site = UnfoldAdminSite()
        request = RequestFactory().get("/rand")
        request.user = AnonymousUser()
        context = admin_site.each_context(request)
        self.assertEqual(context["site_icon"], "hardcoded-icon.svg")

    @override_settings(
        UNFOLD={
            **CONFIG_DEFAULTS,
            **{
                "SITE_ICON": {
                    "light": lambda request: static("icon-light.svg"),
                    "dark": lambda request: static("icon-dark.svg"),
                }
            },
        }
    )
    def test_correct_mode_site_icon(self):
        admin_site = UnfoldAdminSite()
        request = RequestFactory().get("/rand")
        request.user = AnonymousUser()
        context = admin_site.each_context(request)
        self.assertDictEqual(
            context["site_icon"], {"light": "icon-light.svg", "dark": "icon-dark.svg"}
        )

    @override_settings(
        UNFOLD={
            **CONFIG_DEFAULTS,
            **{
                "SITE_ICON": {
                    "light": lambda request: static("icon.svg"),
                }
            },
        }
    )
    def test_incorrect_mode_site_icon(self):
        admin_site = UnfoldAdminSite()
        request = RequestFactory().get("/rand")
        request.user = AnonymousUser()
        context = admin_site.each_context(request)
        self.assertIsNone(context["site_icon"])

    @override_settings(
        UNFOLD={
            **CONFIG_DEFAULTS,
            **{
                "SITE_LOGO": lambda request: static("logo.svg"),
            },
        }
    )
    def test_correct_callback_site_logo(self):
        admin_site = UnfoldAdminSite()
        request = RequestFactory().get("/rand")
        request.user = AnonymousUser()
        context = admin_site.each_context(request)
        self.assertEqual(context["site_logo"], "logo.svg")

    @override_settings(
        UNFOLD={
            **CONFIG_DEFAULTS,
            **{
                "SITE_LOGO": "hardcoded-logo.svg",
            },
        }
    )
    def test_correct_string_site_logo(self):
        admin_site = UnfoldAdminSite()
        request = RequestFactory().get("/rand")
        request.user = AnonymousUser()
        context = admin_site.each_context(request)
        self.assertEqual(context["site_logo"], "hardcoded-logo.svg")

    @override_settings(
        UNFOLD={
            **CONFIG_DEFAULTS,
            **{
                "SITE_LOGO": {
                    "light": lambda request: static("logo-light.svg"),
                    "dark": lambda request: static("logo-dark.svg"),
                }
            },
        }
    )
    def test_correct_mode_site_logo(self):
        admin_site = UnfoldAdminSite()
        request = RequestFactory().get("/rand")
        request.user = AnonymousUser()
        context = admin_site.each_context(request)
        self.assertDictEqual(
            context["site_logo"], {"light": "logo-light.svg", "dark": "logo-dark.svg"}
        )

    @override_settings(
        UNFOLD={
            **CONFIG_DEFAULTS,
            **{
                "SITE_LOGO": {
                    "light": lambda request: static("logo.svg"),
                }
            },
        }
    )
    def test_incorrect_mode_site_logo(self):
        admin_site = UnfoldAdminSite()
        request = RequestFactory().get("/rand")
        request.user = AnonymousUser()
        context = admin_site.each_context(request)
        self.assertIsNone(context["site_logo"])
