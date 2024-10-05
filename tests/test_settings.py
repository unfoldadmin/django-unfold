from django.conf import settings
from django.test.utils import override_settings

from unfold.settings import CONFIG_DEFAULTS, get_config


def test_settings_default_config():
    assert get_config() == CONFIG_DEFAULTS


def test_settings_default_config_with_custom_settings_name():
    assert get_config("CUSTOM_SETTINGS_NAME") == CONFIG_DEFAULTS


@override_settings(UNFOLD={**CONFIG_DEFAULTS, **{"SITE_TITLE": "Test site title"}})
def test_settings_extended_config():
    assert settings.UNFOLD["SITE_TITLE"] == "Test site title"
