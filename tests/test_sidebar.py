from django.contrib.auth.models import AnonymousUser
from django.test.client import RequestFactory

from unfold.sites import UnfoldAdminSite


def test_sidebar_defaults():
    admin_site = UnfoldAdminSite()
    request = RequestFactory().get("/rand")
    request.user = AnonymousUser()
    context = admin_site.each_context(request)
    assert context["sidebar_show_all_applications"] is False
    assert context["sidebar_show_search"] is False
    assert context["sidebar_navigation"] == []
