from django.contrib.auth.models import AnonymousUser
from django.test.client import RequestFactory
from django.test.utils import override_settings

from unfold.settings import CONFIG_DEFAULTS
from unfold.sites import UnfoldAdminSite


def test_sidebar_defaults():
    admin_site = UnfoldAdminSite()
    request = RequestFactory().get("/rand")
    request.user = AnonymousUser()
    context = admin_site.each_context(request)
    assert context["sidebar_show_all_applications"] is False
    assert context["sidebar_show_search"] is False
    assert context["sidebar_navigation"] == []


@override_settings(UNFOLD={**CONFIG_DEFAULTS, **{"SITE_VERSION": "v1.0.0"}})
def test_sidebar_with_site_version():
    admin_site = UnfoldAdminSite()
    request = RequestFactory().get("/rand")
    request.user = AnonymousUser()
    context = admin_site.each_context(request)
    assert context["site_version"] == "v1.0.0"
