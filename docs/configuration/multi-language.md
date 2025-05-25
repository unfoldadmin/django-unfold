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

## Overriding language options

By default, Django Unfold will automatically detect and display all available languages configured in your Django project's `LANGUAGES` setting. However, there are scenarios where you might want to customize which languages appear in the language selector or how they are presented to users. Django Unfold provides flexible configuration options that allow you to override the default language detection behavior and provide your own custom list of languages for the navigation interface.

This customization capability is particularly useful when you want to:

- Display only a subset of your configured languages in the admin interface
- Present languages in a specific order that differs from your Django settings
- Use custom language names or translations that better suit your admin users
- Implement dynamic language selection based on user permissions or other criteria
- Integrate with external language management systems or APIs

The language override functionality gives you complete control over both the languages that appear in the selector and how the language switching mechanism behaves within the admin interface.

```python
from django.utils.translation import get_language_info

UNFOLD = {
    "LANGUAGES": {
        # Hardcoded list of languages
        "navigation": [
            {
                'bidi': False,
                'code': 'de',
                'name': 'German',
                'name_local':
                'Deutsch',
                'name_translated': 'German'
            },
        ],

        # Using a callback to generate list of languages
        # "navigation": "your_app.utils.languages_callback",

        # In case you want to have some custom form handling
        # "actions": reverse_lazy("custom_form_submit")
    }
}

# def languages_callback(request):
#     return [get_language_info(lang) for lang in ["en", "de", "fr"]]
```
