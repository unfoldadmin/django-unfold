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
    "SHOW_BACK_BUTTON": False,
    "COLORS": {
        "base": {
            "50": "249 250 251",
            "100": "243 244 246",
            "200": "229 231 235",
            "300": "209 213 219",
            "400": "156 163 175",
            "500": "107 114 128",
            "600": "75 85 99",
            "700": "55 65 81",
            "800": "31 41 55",
            "900": "17 24 39",
            "950": "3 7 18",
        },
        "primary": {
            "50": "250 245 255",
            "100": "243 232 255",
            "200": "233 213 255",
            "300": "216 180 254",
            "400": "192 132 252",
            "500": "168 85 247",
            "600": "147 51 234",
            "700": "126 34 206",
            "800": "107 33 168",
            "900": "88 28 135",
            "950": "59 7 100",
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
    "SIDEBAR": {
        "show_search": False,
        "show_all_applications": False,
        "navigation": {},
    },
    "TABS": [],
    "LOGIN": {
        "image": None,
        "redirect_after": None,
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
