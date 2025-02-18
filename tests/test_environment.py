from django.contrib.auth.models import AnonymousUser
from django.test.client import RequestFactory
from django.test.utils import override_settings

from unfold.settings import CONFIG_DEFAULTS
from unfold.sites import UnfoldAdminSite


def environment_callback(request):
    return ["Testing Environment", "warning"]


def environment_title_prefix_callback(request):
    return "[TEST]"


@override_settings(UNFOLD={**CONFIG_DEFAULTS})
def test_environment_empty_environment_callback():
    admin_site = UnfoldAdminSite()
    request = RequestFactory().get("/rand")
    request.user = AnonymousUser()
    context = admin_site.each_context(request)
    assert "environment" in context
    assert not context["environment"]


@override_settings(
    UNFOLD={
        **CONFIG_DEFAULTS,
        **{
            "ENVIRONMENT": "tests.test_environment.non_existing_environment_callback",
        },
    }
)
def test_environment_incorrect_environment_callback():
    admin_site = UnfoldAdminSite()
    request = RequestFactory().get("/rand")
    request.user = AnonymousUser()
    context = admin_site.each_context(request)
    assert "environment" in context
    assert (
        context["environment"]
        == "tests.test_environment.non_existing_environment_callback"
    )


@override_settings(
    UNFOLD={
        **CONFIG_DEFAULTS,
        **{
            "ENVIRONMENT": "tests.test_environment.environment_callback",
        },
    }
)
def test_environment_correct_environment_callback():
    admin_site = UnfoldAdminSite()
    request = RequestFactory().get("/rand")
    request.user = AnonymousUser()
    context = admin_site.each_context(request)
    assert "environment" in context
    assert context["environment"] == ["Testing Environment", "warning"]


@override_settings(
    UNFOLD={
        **CONFIG_DEFAULTS,
        **{
            "ENVIRONMENT_TITLE_PREFIX": "tests.test_environment.environment_title_prefix_callback",
        },
    }
)
def test_environment_title_prefix_correct_environment_callback():
    admin_site = UnfoldAdminSite()
    request = RequestFactory().get("/rand")
    request.user = AnonymousUser()
    context = admin_site.each_context(request)
    assert "environment_title_prefix" in context
    assert context["environment_title_prefix"] == "[TEST]"
