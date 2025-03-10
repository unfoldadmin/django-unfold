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


def tools_config_callback(request):
    return {
        "show_tools": True,
        "title": "Test Tools",
        "tools": [
            {
                "name": "Test Tool",
                "url": "http://test.com",
                "icon": "test",
                "new_tab": True,
            }
        ],
    }


@override_settings(UNFOLD={**CONFIG_DEFAULTS})
def test_tools_config_empty():
    admin_site = UnfoldAdminSite()
    request = RequestFactory().get("/rand")
    request.user = AnonymousUser()
    context = admin_site.each_context(request)
    assert "tools_config" in context
    assert context["tools_config"] == CONFIG_DEFAULTS["TOOLS_CONFIG"]


@override_settings(
    UNFOLD={
        **CONFIG_DEFAULTS,
        **{
            "TOOLS_CONFIG": "tests.test_environment.non_existing_tools_config",
        },
    }
)
def test_tools_config_incorrect_callback():
    admin_site = UnfoldAdminSite()
    request = RequestFactory().get("/rand")
    request.user = AnonymousUser()
    context = admin_site.each_context(request)
    assert "tools_config" in context
    assert context["tools_config"] == "tests.test_environment.non_existing_tools_config"


@override_settings(
    UNFOLD={
        **CONFIG_DEFAULTS,
        **{
            "TOOLS_CONFIG": "tests.test_environment.tools_config_callback",
        },
    }
)
def test_tools_config_correct_callback():
    admin_site = UnfoldAdminSite()
    request = RequestFactory().get("/rand")
    request.user = AnonymousUser()
    context = admin_site.each_context(request)
    assert "tools_config" in context
    expected_config = {
        "show_tools": True,
        "title": "Test Tools",
        "tools": [
            {
                "name": "Test Tool",
                "url": "http://test.com",
                "icon": "test",
                "new_tab": True,
            }
        ],
    }
    assert context["tools_config"] == expected_config


@override_settings(
    UNFOLD={
        **CONFIG_DEFAULTS,
        **{"TOOLS_CONFIG": {"show_tools": False, "title": "Custom Tools", "tools": []}},
    }
)
def test_tools_config_direct_settings():
    admin_site = UnfoldAdminSite()
    request = RequestFactory().get("/rand")
    request.user = AnonymousUser()
    context = admin_site.each_context(request)
    assert "tools_config" in context
    assert context["tools_config"]["show_tools"] is False
    assert context["tools_config"]["title"] == "Custom Tools"
    assert context["tools_config"]["tools"] == []
