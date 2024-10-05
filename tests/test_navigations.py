from django.test.client import RequestFactory
from django.test.utils import override_settings

from unfold.settings import CONFIG_DEFAULTS
from unfold.sites import UnfoldAdminSite


def deny_permission(request):
    return False


def allow_permission(request):
    return True


@override_settings(
    UNFOLD={
        **CONFIG_DEFAULTS,
        **{
            "TABS": [
                {
                    "items": [
                        {
                            "title": "Example Title",
                            "link": "https://example.com",
                            "permission": lambda request: False,
                        }
                    ],
                }
            ]
        },
    }
)
def test_navigations_check_tab_lambda_deny_permission():
    admin_site = UnfoldAdminSite()
    request = RequestFactory().get("/rand")
    tabs = admin_site.get_tabs_list(request)
    assert not tabs[0]["items"][0]["has_permission"]


@override_settings(
    UNFOLD={
        **CONFIG_DEFAULTS,
        **{
            "TABS": [
                {
                    "items": [
                        {
                            "title": "Example Title",
                            "link": "https://example.com",
                            "permission": lambda request: True,
                        }
                    ]
                }
            ]
        },
    }
)
def test_navigations_check_tab_lambda_allow_permission():
    admin_site = UnfoldAdminSite()
    request = RequestFactory().get("/rand")
    tabs = admin_site.get_tabs_list(request)
    assert tabs[0]["items"][0]["has_permission"]


@override_settings(
    UNFOLD={
        **CONFIG_DEFAULTS,
        **{
            "TABS": [
                {
                    "items": [
                        {
                            "title": "Example Title",
                            "link": "https://example.com",
                            "permission": "tests.test_navigations.deny_permission",
                        }
                    ],
                }
            ]
        },
    }
)
def test_navigations_check_tab_path_deny_permission():
    admin_site = UnfoldAdminSite()
    request = RequestFactory().get("/rand")
    tabs = admin_site.get_tabs_list(request)
    assert not tabs[0]["items"][0]["has_permission"]


@override_settings(
    UNFOLD={
        **CONFIG_DEFAULTS,
        **{
            "TABS": [
                {
                    "items": [
                        {
                            "title": "Example Title",
                            "link": "https://example.com",
                            "permission": "tests.test_navigations.allow_permission",
                        }
                    ],
                }
            ]
        },
    }
)
def test_navigations_check_tab_path_allow_permission():
    admin_site = UnfoldAdminSite()
    request = RequestFactory().get("/rand")
    tabs = admin_site.get_tabs_list(request)
    assert tabs[0]["items"][0]["has_permission"]
