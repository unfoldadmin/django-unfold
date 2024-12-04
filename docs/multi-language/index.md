---
title: Multi-language
order: 14
description: Add support for multiple languages in django admin.
---

# Multi-language support

To add support for multiple languages in django admin, you need to add `django.middleware.locale.LocaleMiddleware` to `MIDDLEWARE` and set `USE_I18N` to `True`. Then you need to define `LANGUAGE_CODE` and `LANGUAGES`. After these changes your site will be prepared for multiple languages.

```python
# settings.py

MIDDLEWARE = [
    "django.middleware.locale.LocaleMiddleware",
]

LANGUAGE_CODE = "en"

USE_I18N = True

LANGUAGES = (
    ("de", _("German")),
    ("en", _("English")),
)
```

Below you can find an example of how to add support for multiple languages in Django admin. Once you have this setup, you will be able to access the admin in different languages. In our case we have two languages, English and German so our admin will be available in `/en/admin/` and `/de/admin/`. If you visit `/admin/` you will see the default language which is English and you will be redirected to `/en/admin/`.

The `path("i18n/", include("django.conf.urls.i18n")),` is needed for the language selector to work. This line of code is going to provide a view which will be used to change the language. Make sure that this line is not defined in `i18n_patterns`.

```python
# urls.py

from django.conf.urls.i18n import i18n_patterns
from django.urls import include, path

urlpatterns = (
    [
        path("i18n/", include("django.conf.urls.i18n")),
    ]
    + i18n_patterns(
        path("admin/", admin.site.urls),
    )
)
```

To display the language selector in the admin, you need to add `UNFOLD = {"SHOW_LANGUAGES": True,}` to your `settings.py` file. The language selector will be displayed in the top right corner of the admin.

```python
# settings.py

UNFOLD = {
    "SHOW_LANGUAGES": True,
}
```
