from collections.abc import Callable

import pytest
from django.test.client import RequestFactory
from django.test.utils import override_settings
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _

from unfold.settings import CONFIG_DEFAULTS
from unfold.sites import UnfoldAdminSite


def sidebar_callback(request):
    return {
        "navigation": [
            {
                "items": [
                    {
                        "title": _("Link title"),
                        "icon": "dashboard",
                        "link": reverse_lazy("admin:index"),
                    },
                ]
            }
        ]
    }


@override_settings(
    UNFOLD={
        **CONFIG_DEFAULTS,
        **{
            "TABS": [],
            "SIDEBAR": {
                "navigation": [
                    {
                        "items": [
                            {
                                "title": _("Dashboard"),
                                "icon": "dashboard",
                                "link": reverse_lazy("admin:index"),
                            },
                        ],
                    }
                ]
            },
        },
    }
)
@pytest.mark.django_db
def test_sidebar_navigation(admin_user):
    admin_site = UnfoldAdminSite()
    request = RequestFactory().get("/rand")
    request.user = admin_user
    context = admin_site.each_context(request)
    assert context["sidebar_navigation"][0]["items"][0]["title"] == "Dashboard"


@override_settings(
    UNFOLD={
        **CONFIG_DEFAULTS,
        **{
            "SIDEBAR": "tests.test_sidebar_navigation.sidebar_callback",
        },
    }
)
@pytest.mark.django_db
def test_sidebar_navigation_as_import_string(admin_user):
    admin_site = UnfoldAdminSite()
    request = RequestFactory().get("/rand")
    request.user = admin_user
    context = admin_site.each_context(request)

    assert context["sidebar_navigation"][0]["items"][0]["title"] == "Link title"


@override_settings(
    UNFOLD={
        **CONFIG_DEFAULTS,
        **{
            "SIDEBAR": {
                "navigation": [
                    {
                        "items": [
                            {
                                "title": _("Dashboard"),
                                "icon": "dashboard",
                                "link": lambda request: "/lambda/link",
                            },
                        ],
                    }
                ]
            },
        },
    }
)
@pytest.mark.django_db
def test_sidebar_navigation_with_lambda_link(admin_user):
    admin_site = UnfoldAdminSite()
    request = RequestFactory().get("/rand")
    request.user = admin_user
    context = admin_site.each_context(request)

    assert isinstance(context["sidebar_navigation"][0]["items"][0]["link"], Callable)
    assert (
        context["sidebar_navigation"][0]["items"][0]["link"](request) == "/lambda/link"
    )


@override_settings(
    UNFOLD={
        **CONFIG_DEFAULTS,
        **{
            "SIDEBAR": {
                "navigation": [
                    {
                        "items": [
                            {
                                "title": "Example Title 1",
                                "link": "https://example.com/1",
                            },
                            {
                                "title": "Example Title 2",
                                "link": "https://example.com/2",
                            },
                        ]
                    }
                ]
            }
        },
    }
)
def test_navigations_items():
    admin_site = UnfoldAdminSite()
    request = RequestFactory().get("/rand")
    sidebar = admin_site.get_sidebar_list(request)
    assert sidebar[0]["items"][0]["title"] == "Example Title 1"
    assert sidebar[0]["items"][1]["title"] == "Example Title 2"


@override_settings(
    UNFOLD={
        **CONFIG_DEFAULTS,
        **{
            "SIDEBAR": {
                "navigation": [
                    {
                        "items": [
                            {
                                "title": "Example Title 1",
                                "link": "https://example.com/1",
                                "permission": lambda request: True,
                            },
                            {
                                "title": "Example Title 2",
                                "link": "https://example.com/2",
                                "permission": lambda request: False,
                            },
                        ]
                    }
                ]
            }
        },
    }
)
def test_navigations_items_with_permissions():
    admin_site = UnfoldAdminSite()
    request = RequestFactory().get("/rand")
    sidebar = admin_site.get_sidebar_list(request)

    # This fork filters out items whose permission callback returns False,
    # so only the permitted item remains in the sidebar.
    assert len(sidebar[0]["items"]) == 1
    assert sidebar[0]["items"][0]["title"] == "Example Title 1"
    assert sidebar[0]["items"][0]["has_permission"] is True


@override_settings(
    UNFOLD={
        **CONFIG_DEFAULTS,
        **{
            "SIDEBAR": {
                "navigation": [
                    {
                        "items": [
                            {
                                "title": "Example Title 1",
                                "link": "https://example.com/1",
                                "active": lambda request: True,
                            },
                            {
                                "title": "Example Title 2",
                                "link": "https://example.com/2",
                                "active": lambda request: False,
                            },
                        ]
                    }
                ]
            }
        },
    }
)
def test_navigations_items_with_active():
    admin_site = UnfoldAdminSite()
    request = RequestFactory().get("/rand")
    sidebar = admin_site.get_sidebar_list(request)
    assert sidebar[0]["items"][0]["active"] is True
    assert sidebar[0]["items"][1]["active"] is False


@override_settings(
    UNFOLD={
        **CONFIG_DEFAULTS,
        **{
            "SIDEBAR": {
                "navigation": [
                    {
                        "items": [
                            {
                                "title": "Example Title 1",
                                "link": None,
                                "active": lambda request: True,
                            },
                            {
                                "title": "Example Title 2",
                                "active": lambda request: False,
                            },
                        ]
                    }
                ]
            }
        },
    }
)
def test_navigation_items_with_empty_link():
    admin_site = UnfoldAdminSite()
    request = RequestFactory().get("/rand")
    sidebar = admin_site.get_sidebar_list(request)

    # This fork drops link-less leaf items and omits any group left with no
    # visible items, so the sidebar ends up empty.
    assert sidebar == []


@override_settings(
    UNFOLD={
        **CONFIG_DEFAULTS,
        **{
            "SIDEBAR": {
                "navigation": [
                    {
                        "items": [
                            {
                                "title": "Submenu parent",
                                # No link of its own — it only groups children.
                                "items": [
                                    {
                                        "title": "Child 1",
                                        "link": "https://example.com/1",
                                    },
                                ],
                            },
                        ]
                    }
                ]
            },
        },
    }
)
def test_navigation_items_nested_submenu_without_link():
    admin_site = UnfoldAdminSite()
    request = RequestFactory().get("/rand")
    sidebar = admin_site.get_sidebar_list(request)

    # Regression: a link-less item that has nested children is a submenu
    # parent and must be preserved (upstream's "drop link-less items" guard
    # otherwise hides the whole submenu).
    assert len(sidebar[0]["items"]) == 1
    assert sidebar[0]["items"][0]["title"] == "Submenu parent"
    assert len(sidebar[0]["items"][0]["items"]) == 1
    assert sidebar[0]["items"][0]["items"][0]["title"] == "Child 1"


@override_settings(
    UNFOLD={
        **CONFIG_DEFAULTS,
        **{
            "TABS": [
                {
                    "items": [
                        {
                            "title": "Tab Title 1",
                            "link": "/menu-link-1",
                        },
                        {
                            "title": "Tab Title 1",
                            "link": "/menu-link-1?sample=example",
                        },
                        {
                            "title": "Tab Title 1",
                            "link": "/menu-link-1/sample-1",
                        },
                    ],
                },
            ],
            "SIDEBAR": {
                "navigation": [
                    {
                        "items": [
                            {
                                "title": "Example Title 1",
                                "link": "/menu-link-1",
                            },
                            {
                                "title": "Example Title 2",
                                "link": "/menu-link-2",
                            },
                        ]
                    }
                ]
            },
        },
    }
)
def test_navigation_items_with_tabs():
    admin_site = UnfoldAdminSite()
    request = RequestFactory().get("/menu-link-1")
    sidebar = admin_site.get_sidebar_list(request)
    assert sidebar[0]["items"][0]["active"] is True
    assert sidebar[0]["items"][1]["active"] is False
