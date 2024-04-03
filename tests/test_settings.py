from django.test import SimpleTestCase
from django.test.utils import override_settings
from unfold.settings import (
    BASE_CLASSES,
    BASE_INPUT_CLASSES,
    CHECKBOX_CLASSES,
    CHECKBOX_LABEL_CLASSES,
    COLOR_CLASSES,
    CONFIG_DEFAULTS,
    INPUT_CLASSES,
    INPUT_CLASSES_READONLY,
    LABEL_CLASSES,
    PROSE_CLASSES,
    RADIO_CLASSES,
    SELECT_CLASSES,
    SWITCH_CLASSES,
    TEXTAREA_CLASSES,
    TEXTAREA_EXPANDABLE_CLASSES,
    get_config,
)


class ConfTestCase(SimpleTestCase):
    expected_config = {
        **CONFIG_DEFAULTS,
        "LABEL_CLASSES": LABEL_CLASSES,
        "CHECKBOX_LABEL_CLASSES": CHECKBOX_LABEL_CLASSES,
        "BASE_CLASSES": BASE_CLASSES,
        "BASE_INPUT_CLASSES": BASE_INPUT_CLASSES,
        "INPUT_CLASSES": INPUT_CLASSES,
        "COLOR_CLASSES": COLOR_CLASSES,
        "INPUT_CLASSES_READONLY": INPUT_CLASSES_READONLY,
        "TEXTAREA_CLASSES": TEXTAREA_CLASSES,
        "TEXTAREA_EXPANDABLE_CLASSES": TEXTAREA_EXPANDABLE_CLASSES,
        "SELECT_CLASSES": SELECT_CLASSES,
        "PROSE_CLASSES": PROSE_CLASSES,
        "CHECKBOX_CLASSES": CHECKBOX_CLASSES,
        "RADIO_CLASSES": RADIO_CLASSES,
        "SWITCH_CLASSES": SWITCH_CLASSES,
    }

    def test_default_config(self):
        self.assertDictEqual(get_config(), self.expected_config)

    def test_default_config_with_custom_settings_name(self):
        # Assuming CUSTOM_SETTINGS_NAME will override some default settings.
        # Need to define what CUSTOM_SETTINGS_NAME would change or add.
        custom_settings = {"SITE_TITLE": "Custom Site Title"}
        expected_custom_config = {**self.expected_config, **custom_settings}
        with override_settings(UNFOLD=custom_settings):
            self.assertDictEqual(get_config("UNFOLD"), expected_custom_config)


class SettingsTestCase(SimpleTestCase):
    @override_settings(UNFOLD={**CONFIG_DEFAULTS, **{"SITE_TITLE": "Test site title"}})
    def test_extended_config(self):
        # This test ensures that changes made via the Django settings are reflected in get_config
        config = get_config()
        self.assertEqual(config["SITE_TITLE"], "Test site title")
