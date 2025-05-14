---
title: Multi-language
order: 14
description: Learn how to configure multi-language support in Django Unfold admin panel with language switching, URL patterns, middleware setup, and internationalization settings for a fully localized admin interface.
---

# Multi-language support

To enable multi-language support in your Django admin interface, you'll need to make several configuration changes in your settings. First, add the `django.middleware.locale.LocaleMiddleware` to your `MIDDLEWARE` setting - this middleware handles language selection based on user preferences. Next, enable internationalization by setting `USE_I18N = True`. You'll also need to specify your default language using `LANGUAGE_CODE` and define the available languages in the `LANGUAGES` setting. Once you've made these configuration changes, your Django admin site will be fully prepared to handle multiple languages and provide language-switching capabilities to your users.

[![Unfold site dropdown](/static/docs/configuration/unfold-multilanguage.webp)](/static/docs/configuration/unfold-multilanguage.webp)

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
