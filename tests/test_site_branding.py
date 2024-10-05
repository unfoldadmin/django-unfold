from django.contrib.auth.models import AnonymousUser
from django.templatetags.static import static
from django.test.client import RequestFactory
from django.test.utils import override_settings

from unfold.settings import CONFIG_DEFAULTS
from unfold.sites import UnfoldAdminSite


@override_settings(
    UNFOLD={
        **CONFIG_DEFAULTS,
        **{
            "SITE_ICON": lambda request: static("icon.svg"),
        },
    }
)
def test_site_branding_correct_callback_site_icon():
    admin_site = UnfoldAdminSite()
    request = RequestFactory().get("/rand")
    request.user = AnonymousUser()
    context = admin_site.each_context(request)
    assert context["site_icon"] == static("icon.svg")


@override_settings(
    UNFOLD={
        **CONFIG_DEFAULTS,
        **{
            "SITE_ICON": "hardcoded-icon.svg",
        },
    }
)
def test_site_branding_correct_string_site_icon():
    admin_site = UnfoldAdminSite()
    request = RequestFactory().get("/rand")
    request.user = AnonymousUser()
    context = admin_site.each_context(request)
    assert context["site_icon"] == "hardcoded-icon.svg"


@override_settings(
    UNFOLD={
        **CONFIG_DEFAULTS,
        **{
            "SITE_ICON": {
                "light": lambda request: static("icon-light.svg"),
                "dark": lambda request: static("icon-dark.svg"),
            }
        },
    }
)
def test_site_branding_correct_mode_site_icon():
    admin_site = UnfoldAdminSite()
    request = RequestFactory().get("/rand")
    request.user = AnonymousUser()
    context = admin_site.each_context(request)
    assert context["site_icon"] == {
        "light": static("icon-light.svg"),
        "dark": static("icon-dark.svg"),
    }


@override_settings(
    UNFOLD={
        **CONFIG_DEFAULTS,
        **{
            "SITE_ICON": {
                "light": lambda request: static("icon.svg"),
            }
        },
    }
)
def test_site_branding_incorrect_mode_site_icon():
    admin_site = UnfoldAdminSite()
    request = RequestFactory().get("/rand")
    request.user = AnonymousUser()
    context = admin_site.each_context(request)
    assert not context["site_icon"]


@override_settings(
    UNFOLD={
        **CONFIG_DEFAULTS,
        **{
            "SITE_LOGO": lambda request: static("logo.svg"),
        },
    }
)
def test_site_branding_correct_callback_site_logo():
    admin_site = UnfoldAdminSite()
    request = RequestFactory().get("/rand")
    request.user = AnonymousUser()
    context = admin_site.each_context(request)
    assert context["site_logo"] == static("logo.svg")


@override_settings(
    UNFOLD={
        **CONFIG_DEFAULTS,
        **{
            "SITE_LOGO": "hardcoded-logo.svg",
        },
    }
)
def test_site_branding_correct_string_site_logo():
    admin_site = UnfoldAdminSite()
    request = RequestFactory().get("/rand")
    request.user = AnonymousUser()
    context = admin_site.each_context(request)
    assert context["site_logo"] == "hardcoded-logo.svg"


@override_settings(
    UNFOLD={
        **CONFIG_DEFAULTS,
        **{
            "SITE_LOGO": {
                "light": lambda request: static("logo-light.svg"),
                "dark": lambda request: static("logo-dark.svg"),
            }
        },
    }
)
def test_site_branding_correct_mode_site_logo():
    admin_site = UnfoldAdminSite()
    request = RequestFactory().get("/rand")
    request.user = AnonymousUser()
    context = admin_site.each_context(request)

    assert context["site_logo"] == {
        "light": static("logo-light.svg"),
        "dark": static("logo-dark.svg"),
    }


@override_settings(
    UNFOLD={
        **CONFIG_DEFAULTS,
        **{
            "SITE_LOGO": {
                "light": lambda request: static("logo.svg"),
            }
        },
    }
)
def test_site_branding_incorrect_mode_site_logo():
    admin_site = UnfoldAdminSite()
    request = RequestFactory().get("/rand")
    request.user = AnonymousUser()
    context = admin_site.each_context(request)
    assert not context["site_logo"]


@override_settings(
    UNFOLD={
        **CONFIG_DEFAULTS,
        **{
            "SITE_FAVICONS": [
                {
                    "rel": "icon",
                    "sizes": "32x32",
                    "type": "image/svg+xml",
                    "href": lambda request: static("favicon.svg"),
                }
            ]
        },
    }
)
def test_site_branding_favicons():
    admin_site = UnfoldAdminSite()
    request = RequestFactory().get("/rand")
    request.user = AnonymousUser()
    context = admin_site.each_context(request)

    assert context["site_favicons"][0].rel == "icon"
    assert context["site_favicons"][0].sizes == "32x32"
    assert context["site_favicons"][0].type == "image/svg+xml"
    assert context["site_favicons"][0].href == static("favicon.svg")
