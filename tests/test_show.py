from django.contrib.auth.models import AnonymousUser
from django.test import TestCase
from django.test.client import RequestFactory
from django.test.utils import override_settings
from unfold.settings import CONFIG_DEFAULTS
from unfold.sites import UnfoldAdminSite


class ShowTestCase(TestCase):
    @override_settings(UNFOLD={**CONFIG_DEFAULTS})
    def test_show_history_default(self):
        admin_site = UnfoldAdminSite()
        request = RequestFactory().get("/rand")
        request.user = AnonymousUser()
        context = admin_site.each_context(request)
        self.assertTrue(context.get("show_history"))

    @override_settings(UNFOLD={**CONFIG_DEFAULTS, **{"SHOW_HISTORY": False}})
    def test_show_history_hide(self):
        admin_site = UnfoldAdminSite()
        request = RequestFactory().get("/rand")
        request.user = AnonymousUser()
        context = admin_site.each_context(request)
        self.assertFalse(context.get("show_history"))

    @override_settings(UNFOLD={**CONFIG_DEFAULTS})
    def test_show_view_on_site_default(self):
        admin_site = UnfoldAdminSite()
        request = RequestFactory().get("/rand")
        request.user = AnonymousUser()
        context = admin_site.each_context(request)
        self.assertTrue(context.get("show_view_on_site"))

    @override_settings(UNFOLD={**CONFIG_DEFAULTS, **{"SHOW_VIEW_ON_SITE": False}})
    def test_show_view_on_site_hide(self):
        admin_site = UnfoldAdminSite()
        request = RequestFactory().get("/rand")
        request.user = AnonymousUser()
        context = admin_site.each_context(request)
        self.assertFalse(context.get("show_view_on_site"))
