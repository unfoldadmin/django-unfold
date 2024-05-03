from django.contrib.auth.models import AnonymousUser
from django.test import TestCase
from django.test.client import RequestFactory
from django.test.utils import override_settings
from unfold.settings import CONFIG_DEFAULTS
from unfold.sites import UnfoldAdminSite


def environment_callback(request):
    return ["Testing Environment", "warning"]


class EnvironmentTestCase(TestCase):
    @override_settings(UNFOLD={**CONFIG_DEFAULTS})
    def test_empty_environment_callback(self):
        admin_site = UnfoldAdminSite()
        request = RequestFactory().get("/rand")
        request.user = AnonymousUser()
        context = admin_site.each_context(request)
        self.assertTrue("environment" not in context)

    @override_settings(
        UNFOLD={
            **CONFIG_DEFAULTS,
            **{
                "ENVIRONMENT": "tests.test_environment.non_existing_environment_callback",
            },
        }
    )
    def test_incorrect_environment_callback(self):
        admin_site = UnfoldAdminSite()
        request = RequestFactory().get("/rand")
        request.user = AnonymousUser()
        context = admin_site.each_context(request)
        self.assertTrue("environment" not in context)

    @override_settings(
        UNFOLD={
            **CONFIG_DEFAULTS,
            **{
                "ENVIRONMENT": "tests.test_environment.environment_callback",
            },
        }
    )
    def test_correct_environment_callback(self):
        admin_site = UnfoldAdminSite()
        request = RequestFactory().get("/rand")
        request.user = AnonymousUser()
        context = admin_site.each_context(request)
        self.assertTrue("environment" in context)
        self.assertEqual(context["environment"], ["Testing Environment", "warning"])
