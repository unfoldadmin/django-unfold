from django.conf import settings
from django.test import SimpleTestCase
from django.test.utils import override_settings
from unfold.settings import CONFIG_DEFAULTS, get_config


class ConfTestCase(SimpleTestCase):
    def test_default_config(self):
        self.assertDictEqual(get_config(), CONFIG_DEFAULTS)

    def test_default_config_with_custom_settings_name(self):
        self.assertDictEqual(get_config("CUSTOM_SETTINGS_NAME"), CONFIG_DEFAULTS)


class SettingsTestCase(SimpleTestCase):
    @override_settings(UNFOLD={**CONFIG_DEFAULTS, **{"SITE_TITLE": "Test site title"}})
    def test_extended_config(self):
        self.assertEqual(settings.UNFOLD["SITE_TITLE"], "Test site title")
