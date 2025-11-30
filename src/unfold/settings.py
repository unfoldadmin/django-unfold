from typing import Any

from django.conf import settings

CONFIG_DEFAULTS = {
    "SITE_TITLE": None,
    "SITE_HEADER": None,
    "SITE_SUBHEADER": None,
    "SITE_DROPDOWN": None,
    "SITE_URL": "/",
    "SITE_ICON": None,
    "SITE_SYMBOL": None,
    "SITE_LOGO": None,
    "SITE_FAVICONS": [],
    "SHOW_HISTORY": True,
    "SHOW_VIEW_ON_SITE": True,
    "SHOW_LANGUAGES": False,
    "LANGUAGE_FLAGS": {},
    "SHOW_BACK_BUTTON": False,
    "COLORS": {
        "base": {
            "50": "oklch(98.5% .002 247.839)",
            "100": "oklch(96.7% .003 264.542)",
            "200": "oklch(92.8% .006 264.531)",
            "300": "oklch(87.2% .01 258.338)",
            "400": "oklch(70.7% .022 261.325)",
            "500": "oklch(55.1% .027 264.364)",
            "600": "oklch(44.6% .03 256.802)",
            "700": "oklch(37.3% .034 259.733)",
            "800": "oklch(27.8% .033 256.848)",
            "900": "oklch(21% .034 264.665)",
            "950": "oklch(13% .028 261.692)",
        },
        "primary": {
            "50": "oklch(97.7% .014 308.299)",
            "100": "oklch(94.6% .033 307.174)",
            "200": "oklch(90.2% .063 306.703)",
            "300": "oklch(82.7% .119 306.383)",
            "400": "oklch(71.4% .203 305.504)",
            "500": "oklch(62.7% .265 303.9)",
            "600": "oklch(55.8% .288 302.321)",
            "700": "oklch(49.6% .265 301.924)",
            "800": "oklch(43.8% .218 303.724)",
            "900": "oklch(38.1% .176 304.987)",
            "950": "oklch(29.1% .149 302.717)",
        },
        "font": {
            "subtle-light": "var(--color-base-500)",  # text-base-500
            "subtle-dark": "var(--color-base-400)",  # text-base-400
            "default-light": "var(--color-base-600)",  # text-base-600
            "default-dark": "var(--color-base-300)",  # text-base-300
            "important-light": "var(--color-base-900)",  # text-base-900
            "important-dark": "var(--color-base-100)",  # text-base-100
        },
    },
    "DASHBOARD_CALLBACK": None,
    "ENVIRONMENT": None,
    "ENVIRONMENT_TITLE_PREFIX": None,
    "STYLES": [],
    "SCRIPTS": [],
    "ACCOUNT": {
        "navigation": [],
    },
    "LANGUAGES": {
        "action": None,
        "navigation": [],
    },
    "COMMAND": {
        "search_models": False,  # Enable search in the models
        "show_history": False,  # Enable history in the command search
        "search_callback": None,  # Inject a custom callback to the search form
    },
    "SIDEBAR": {
        "show_search": False,
        "command_search": False,
        "show_all_applications": False,
        "navigation": [],
    },
    "TABS": [],
    "LOGIN": {
        "image": None,
        "redirect_after": None,
        "form": None,
    },
    "EXTENSIONS": {"modeltranslation": {"flags": {}}},
}


def get_config(settings_name=None):
    if settings_name is None:
        settings_name = "UNFOLD"

    def merge_dicts(dict1: dict[str, Any], dict2: dict[str, Any]) -> dict[str, Any]:
        result = dict1.copy()

        for key, value in dict2.items():
            if (
                key in result
                and isinstance(result[key], dict)
                and isinstance(value, dict)
            ):
                result[key] = merge_dicts(result[key], value)
            else:
                result[key] = value

        return result

    return merge_dicts(CONFIG_DEFAULTS, getattr(settings, settings_name, {}))
