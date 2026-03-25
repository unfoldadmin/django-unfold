from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from django.test.client import RequestFactory
from django.test.utils import override_settings

from unfold.settings import CONFIG_DEFAULTS, get_config
from unfold.sites import UnfoldAdminSite


def global_callback_wrong_return_type(request):
    return None


def global_callback_correct_return_type(request):
    return {
        "global_callback_key": "global_callback_value",
    }


def test_settings_default_config():
    assert get_config() == CONFIG_DEFAULTS


def test_settings_default_config_with_custom_settings_name():
    assert get_config("CUSTOM_SETTINGS_NAME") == CONFIG_DEFAULTS


@override_settings(UNFOLD={**CONFIG_DEFAULTS, **{"SITE_TITLE": "Test site title"}})
def test_settings_extended_config():
    assert settings.UNFOLD["SITE_TITLE"] == "Test site title"


@override_settings(
    UNFOLD={
        **CONFIG_DEFAULTS,
        **{
            "GLOBAL_CALLBACK": "tests.test_settings.global_callback_wrong_return_type",
        },
    }
)
def test_settings_global_callback(mocker):
    mock = mocker.patch("tests.test_settings.global_callback_wrong_return_type")
    admin_site = UnfoldAdminSite()
    request = RequestFactory().get("/rand")
    request.user = AnonymousUser()
    admin_site.each_context(request)
    mock.assert_called_once_with(request)


@override_settings(
    UNFOLD={
        **CONFIG_DEFAULTS,
        **{
            "GLOBAL_CALLBACK": "tests.test_settings.global_callback_wrong_return_type",
        },
    }
)
def test_settings_global_callback_wrong_return_type():
    admin_site = UnfoldAdminSite()
    request = RequestFactory().get("/rand")
    request.user = AnonymousUser()
    result = admin_site.each_context(request)
    assert isinstance(result, dict)


@override_settings(
    UNFOLD={
        **CONFIG_DEFAULTS,
        **{
            "GLOBAL_CALLBACK": "tests.test_settings.global_callback_correct_return_type",
        },
    }
)
def test_settings_global_callback_correct_return_type():
    admin_site = UnfoldAdminSite()
    request = RequestFactory().get("/rand")
    request.user = AnonymousUser()
    result = admin_site.each_context(request)

    assert "global_callback_key" in result
    assert result["global_callback_key"] == "global_callback_value"
