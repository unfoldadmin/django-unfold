from django.test import TestCase, override_settings

from ..settings import get_config


class SettingsTestCase(TestCase):
    def test_get_config_when_unfold_do_not_exists_get_default_config(self):
        self.assertIsNone(get_config("DEFAULT_SETTING")["SITE_TITLE"])

    @override_settings(UNFOLD={"SITE_TITLE": "Unfold"})
    def test_get_config_when_unfold_exists_get_config(self):
        self.assertEqual(get_config("UNFOLD")["SITE_TITLE"], "Unfold")
