import pytest
from django.template import Context, Template
from django.test import RequestFactory, override_settings
from django.utils.translation import gettext_lazy as _

from unfold.settings import CONFIG_DEFAULTS
from unfold.sites import UnfoldAdminSite


def tabs_callback(request):
    return [
        {
            "items": [
                {
                    "title": _("Import string"),
                    "link": "https://example.com/import-string",
                },
            ],
        },
    ]


@override_settings(
    UNFOLD={
        **CONFIG_DEFAULTS,
        **{
            "TABS": [
                {
                    "models": [
                        "app_label.model_name_in_lowercase",
                    ],
                    "items": [
                        {
                            "title": _("Your custom title"),
                            "link": "https://example.com",
                        },
                    ],
                },
            ],
        },
    }
)
@pytest.mark.django_db
def test_tabs_context_variables(admin_user):
    admin_site = UnfoldAdminSite()
    request = RequestFactory().get("/rand")
    request.user = admin_user
    context = admin_site.each_context(request)

    assert context["tab_list"][0]["items"][0]["title"] == "Your custom title"
    assert context["tab_list"][0]["items"][0]["link"] == "https://example.com"


@override_settings(
    UNFOLD={
        **CONFIG_DEFAULTS,
        **{
            "TABS": "tests.test_tabs.tabs_callback",
        },
    }
)
@pytest.mark.django_db
def test_tabs_import_string(admin_user):
    admin_site = UnfoldAdminSite()
    request = RequestFactory().get("/rand")
    request.user = admin_user
    context = admin_site.each_context(request)

    assert context["tab_list"][0]["items"][0]["title"] == "Import string"
    assert (
        context["tab_list"][0]["items"][0]["link"]
        == "https://example.com/import-string"
    )


@override_settings(
    UNFOLD={
        **CONFIG_DEFAULTS,
        **{
            "TABS": [
                {
                    "models": [
                        "example.user",
                    ],
                    "items": [
                        {
                            "title": _("User model tab"),
                            "link": "https://example.com/user-model-tab",
                        },
                    ],
                },
            ],
        },
    }
)
@pytest.mark.django_db
def test_tabs_changelist(admin_request, user_model_admin):
    changelist = user_model_admin.changelist_view(admin_request)
    changelist.render()

    assert b"User model tab" in changelist.content
    assert b"https://example.com/user-model-tab" in changelist.content


@override_settings(
    UNFOLD={
        **CONFIG_DEFAULTS,
        **{
            "TABS": [
                {
                    "models": [
                        {
                            "name": "example.user",
                            "detail": True,
                        },
                    ],
                    "items": [
                        {
                            "title": _("User detail model tab"),
                            "link": "https://example.com/user-detail-model-tab",
                        },
                    ],
                },
            ],
        },
    }
)
@pytest.mark.django_db
def test_tabs_changeform(admin_request, user_model_admin, user_changelist):
    changelist = user_model_admin.changeform_view(
        request=admin_request, object_id=str(admin_request.user.pk)
    )
    changelist.render()

    assert b"User detail model tab" in changelist.content
    assert b"https://example.com/user-detail-model-tab" in changelist.content


@override_settings(
    UNFOLD={
        **CONFIG_DEFAULTS,
        **{
            "TABS": [
                {
                    "page": "sample_page",
                    "items": [
                        {
                            "title": _("Your custom title"),
                            "link": "https://example.com",
                        },
                    ],
                },
            ],
        },
    }
)
@pytest.mark.django_db
def test_tabs_custom_page_templatetag(admin_user):
    admin_site = UnfoldAdminSite()
    request = RequestFactory().get("/rand")
    request.user = admin_user
    context = admin_site.each_context(request)

    template = Template('{% load unfold %}{% tab_list "sample_page" %}')
    rendered = template.render(
        Context(
            {
                "request": request,
                "tab_list": context["tab_list"],
                "is_popup": False,
            }
        )
    )
    assert "Your custom title" in rendered
    assert "https://example.com" in rendered
