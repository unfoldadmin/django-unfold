from django.contrib.auth.models import AnonymousUser
from django.test.client import RequestFactory
from django.test.utils import override_settings

from unfold.settings import CONFIG_DEFAULTS
from unfold.sites import UnfoldAdminSite


def tools_config_callback(request):
    return {
        "show_tools": True,
        "title": "Test Tools",
        "tools": [
            {
                "name": "Test Tool",
                "url": "http://test.com",
                "icon": "code",
                "new_tab": True,
            }
        ],
    }


@override_settings(UNFOLD={**CONFIG_DEFAULTS})
def test_tools_empty_config():
    admin_site = UnfoldAdminSite()
    request = RequestFactory().get("/rand")
    request.user = AnonymousUser()
    context = admin_site.each_context(request)
    assert "tools_config" in context
    assert context["tools_config"] == CONFIG_DEFAULTS["TOOLS_CONFIG"]


@override_settings(
    UNFOLD={
        **CONFIG_DEFAULTS,
        **{"TOOLS_CONFIG": {"show_tools": False, "title": "Custom Tools", "tools": []}},
    }
)
def test_tools_custom_config():
    admin_site = UnfoldAdminSite()
    request = RequestFactory().get("/rand")
    request.user = AnonymousUser()
    context = admin_site.each_context(request)
    assert "tools_config" in context
    assert context["tools_config"]["show_tools"] is False
    assert context["tools_config"]["title"] == "Custom Tools"
    assert context["tools_config"]["tools"] == []


@override_settings(
    UNFOLD={
        **CONFIG_DEFAULTS,
        **{
            "TOOLS_CONFIG": {
                "show_tools": True,
                "title": "Test Tools",
                "tools": [
                    {
                        "name": "Test Tool",
                        "url": "http://test.com",
                        "icon": "code",
                        "new_tab": True,
                    }
                ],
            }
        },
    }
)
def test_tools_with_items():
    admin_site = UnfoldAdminSite()
    request = RequestFactory().get("/rand")
    request.user = AnonymousUser()
    context = admin_site.each_context(request)
    assert "tools_config" in context
    assert context["tools_config"]["show_tools"] is True
    assert context["tools_config"]["title"] == "Test Tools"
    assert len(context["tools_config"]["tools"]) == 1
    assert context["tools_config"]["tools"][0]["name"] == "Test Tool"
    assert context["tools_config"]["tools"][0]["url"] == "http://test.com"
    assert context["tools_config"]["tools"][0]["icon"] == "code"
    assert context["tools_config"]["tools"][0]["new_tab"] is True


@override_settings(
    UNFOLD={
        **CONFIG_DEFAULTS,
        **{
            "TOOLS_CONFIG": {
                "show_tools": True,
                "title": "Multiple Tools",
                "tools": [
                    {
                        "name": "Tool 1",
                        "url": "http://tool1.com",
                        "icon": "code",
                        "new_tab": True,
                    },
                    {
                        "name": "Tool 2",
                        "url": "http://tool2.com",
                        "icon": "bug_report",
                        "new_tab": False,
                    },
                ],
            }
        },
    }
)
def test_tools_multiple_items():
    admin_site = UnfoldAdminSite()
    request = RequestFactory().get("/rand")
    request.user = AnonymousUser()
    context = admin_site.each_context(request)
    assert "tools_config" in context
    assert len(context["tools_config"]["tools"]) == 2
    assert context["tools_config"]["tools"][0]["name"] == "Tool 1"
    assert context["tools_config"]["tools"][1]["name"] == "Tool 2"
    assert context["tools_config"]["tools"][0]["new_tab"] is True
    assert context["tools_config"]["tools"][1]["new_tab"] is False
