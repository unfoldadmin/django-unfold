from typing import Any, Dict

from django.conf import settings

CONFIG_DEFAULTS = {
    "SITE_TITLE": None,
    "SITE_HEADER": None,
    "SITE_URL": "/",
    "SITE_ICON": None,
    "SITE_SYMBOL": None,
    "SITE_LOGO": None,
    "SITE_FAVICONS": [],
    "SHOW_HISTORY": True,
    "SHOW_VIEW_ON_SITE": True,
    "COLORS": {
        "font": {
            "subtle-light": "107 114 128",  # text-gray-500
            "subtle-dark": "156 163 175",  # text-gray-400
            "default-light": "75 85 99",  # text-gray-600
            "default-dark": "209 213 219",  # text-gray-300
            "important-light": "17 24 39",  # text-gray-900
            "important-dark": "243 244 246",  # text-gray-100
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
    },
    "DASHBOARD_CALLBACK": None,
    "ENVIRONMENT": None,
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

    def merge_dicts(dict1: Dict[str, Any], dict2: Dict[str, Any]) -> Dict[str, Any]:
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
