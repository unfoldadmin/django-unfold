from typing import Callable

import pytest
from django.contrib.auth.models import AnonymousUser
from django.test import override_settings
from django.test.client import RequestFactory
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _

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
            "SIDEBAR": "tests.test_sidebar.sidebar_callback",
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
