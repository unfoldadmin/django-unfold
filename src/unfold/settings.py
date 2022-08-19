from functools import lru_cache

from django.conf import settings

CONFIG_DEFAULTS = {
    "SITE_TITLE": None,
    "SITE_HEADER": None,
    "SITE_URL": "/",
    "SITE_ICON": None,
    "COLORS": {},
    "DASHBOARD_CALLBACK": None,
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


@lru_cache
def get_config():
    return {**CONFIG_DEFAULTS, **getattr(settings, "UNFOLD", {})}
