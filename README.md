[![screenshot](https://github.com/user-attachments/assets/8c2dc5c1-480b-49ad-bd2e-57369ca4e306)](https://unfoldadmin.com)

## Unfold - Modern Django **Admin**

[![PyPI - Version](https://img.shields.io/pypi/v/django-unfold.svg?style=for-the-badge)](https://pypi.org/project/django-unfold/)
[![Discord](https://img.shields.io/discord/1297493955231088650?style=for-the-badge&logo=discord&logoColor=%23ffffff&color=7289da)](https://discord.gg/9sQj9MEbNz)
[![Build](https://img.shields.io/github/actions/workflow/status/unfoldadmin/django-unfold/release.yml?style=for-the-badge)](https://github.com/unfoldadmin/django-unfold/actions?query=workflow%3Arelease)
![Monthly downloads](https://img.shields.io/pypi/dm/django-unfold?style=for-the-badge)

Enhance Django Admin with a modern interface and powerful tools to build internal applications.

- **Documentation:** The full documentation is available at [unfoldadmin.com](https://unfoldadmin.com?utm_medium=github&utm_source=unfold).
- **Live demo:** The demo site is available at [unfoldadmin.com](https://unfoldadmin.com?utm_medium=github&utm_source=unfold).
- **Formula:** A repository with a demo implementation is available at [github.com/unfoldadmin/formula](https://github.com/unfoldadmin/formula?utm_medium=github&utm_source=unfold).
- **Turbo:** A Django & Next.js boilerplate implementing Unfold is available at [github.com/unfoldadmin/turbo](https://github.com/unfoldadmin/turbo?utm_medium=github&utm_source=unfold).
- **Discord:** Join our Unfold community on [Discord](https://discord.gg/9sQj9MEbNz).

## Quickstart

### Install the package

```sh
pip install django-unfold
```

### Change INSTALLED_APPS in settings.py

```python
INSTALLED_APPS = [
    "unfold",
    # Rest of the apps
]
```

### Use Unfold ModelAdmin

```python
from unfold.admin import ModelAdmin

@admin.register(MyModel)
class MyModelAdmin(ModelAdmin):
    pass
```

*Unfold works alongside the default Django admin and requires no migration of existing models or workflows. Unfold is actively developed and continuously evolving as new use cases and edge cases are discovered.*

## Why Unfold?

- Built on `django.contrib.admin`: Enhances the existing admin without replacing it.
- Provides a modern interface and improved workflows.
- Designed for real internal tools and backoffice apps.
- Incremental adoption for existing projects.

## Features

- **Visual interface**: Provides a modern user interface based on the Tailwind CSS framework.
- **Sidebar navigation**: Simplifies the creation of sidebar menus with icons, collapsible sections, and more.
- **Dark mode support**: Includes both light and dark mode themes.
- **Flexible actions**: Provides multiple ways to define actions throughout the admin interface.
- **Advanced filters**: Features custom dropdowns, autocomplete, numeric, datetime, and text field filters.
- **Dashboard tools**: Includes helpers for building custom dashboard pages.
- **UI components**: Offers reusable interface components such as cards, buttons, and charts.
- **Crispy forms**: Custom template pack for django-crispy-forms to style forms with Unfold's design system.
- **WYSIWYG editor**: Built-in support for WYSIWYG editing through Trix.
- **Array widget:** Support for `django.contrib.postgres.fields.ArrayField`.
- **Inline tabs:** Group inlines into tab navigation in the change form.
- **Conditional fields:** Show or hide fields dynamically based on the values of other fields in the form.
- **Model tabs:** Allow defining custom tab navigation for models.
- **Fieldset tabs:** Merge multiple fieldsets into tabs in the change form.
- **Sortable inlines:** Allow sorting inlines by dragging and dropping.
- **Command palette**: Quickly search across models and custom data.
- **Datasets**: Custom changelists `ModelAdmin` displayed on change form detail pages.
- **Environment label:** Distinguish between environments by displaying a label.
- **Nonrelated inlines:** Display nonrelated models as inlines in the change form.
- **Paginated inlines:** Break down large record sets into pages within inlines for better admin performance.
- **Favicons:** Built-in support for configuring various site favicons.
- **Theming:** Customize color schemes, backgrounds, border radius, and more.
- **Font colors:** Adjust font colors for better readability.
- **Changeform modes:** Display fields in compressed mode in the change form.
- **Language switcher:** Allow changing language directly from the admin area.
- **Infinite paginator:** Efficiently handle large datasets with seamless pagination that reduces server load.
- **Parallel admin:** Supports [running the default admin](https://unfoldadmin.com/blog/migrating-django-admin-unfold/?utm_medium=github&utm_source=unfold) alongside Unfold.
- **Third-party packages:** Provides default support for multiple popular applications.
- **Configuration:** Allows basic options to be changed in `settings.py`.
- **Dependencies:** Built entirely on `django.contrib.admin`.

## Third-party package support

- [django-guardian](https://github.com/django-guardian/django-guardian) - [Integration guide](https://unfoldadmin.com/docs/integrations/django-guardian/)
- [django-import-export](https://github.com/django-import-export/django-import-export) - [Integration guide](https://unfoldadmin.com/docs/integrations/django-import-export/)
- [django-simple-history](https://github.com/jazzband/django-simple-history) - [Integration guide](https://unfoldadmin.com/docs/integrations/django-simple-history/)
- [django-constance](https://github.com/jazzband/django-constance) - [Integration guide](https://unfoldadmin.com/docs/integrations/django-constance/)
- [django-celery-beat](https://github.com/celery/django-celery-beat) - [Integration guide](https://unfoldadmin.com/docs/integrations/django-celery-beat/)
- [django-modeltranslation](https://github.com/deschler/django-modeltranslation) - [Integration guide](https://unfoldadmin.com/docs/integrations/django-modeltranslation/)
- [django-money](https://github.com/django-money/django-money) - [Integration guide](https://unfoldadmin.com/docs/integrations/django-money/)
- [django-location-field](https://github.com/caioariede/django-location-field) - [Integration guide](https://unfoldadmin.com/docs/integrations/django-location-field/)
- [djangoql](https://github.com/ivelum/djangoql) - [Integration guide](https://unfoldadmin.com/docs/integrations/djangoql/)
- [django-json-widget](https://github.com/jmrivas86/django-json-widget) - [Integration guide](https://unfoldadmin.com/docs/integrations/django-json-widget/)

## Professional services

Need help integrating, customizing, or scaling Django Admin with Unfold?

- **Consulting**: Expert guidance on Django architecture, performance, feature development, and Unfold integration. [Learn more](https://unfoldadmin.com/consulting/?utm_medium=github&utm_source=unfold)
- **Support**: Assistance with integrating or customizing Unfold, including live 1:1 calls and implementation review. Fixed price, no ongoing commitment. [Learn more](https://unfoldadmin.com/support/?utm_medium=github&utm_source=unfold)
- **Studio**: Extend Unfold with advanced dashboards, visual customization, and additional admin tooling. [Learn more](https://unfoldadmin.com/studio?utm_medium=github&utm_source=unfold)

[![dashboards](https://github.com/user-attachments/assets/7c3124ab-2f59-4254-9222-8a57970f51a6)](https://unfoldadmin.com/studio?utm_medium=github&utm_source=unfold)

## Credits

- **Tailwind**: [Tailwind CSS](https://github.com/tailwindlabs/tailwindcss) - Licensed under the [MIT License](https://opensource.org/licenses/MIT).
- **Icons**: [Material Symbols](https://github.com/google/material-design-icons) - Licensed under the [Apache License 2.0](https://www.apache.org/licenses/LICENSE-2.0).
- **Font**: [Inter](https://github.com/rsms/inter) - Licensed under the [SIL Open Font License 1.1](https://scripts.sil.org/OFL).
- **Charts**: [Chart.js](https://github.com/chartjs/Chart.js) - Licensed under the [MIT License](https://opensource.org/licenses/MIT).
- **JavaScript Framework**: [Alpine.js](https://github.com/alpinejs/alpine) - Licensed under the [MIT License](https://opensource.org/licenses/MIT).
- **AJAX calls**: [HTMX](https://htmx.org/) - Licensed under the [BSD 2-Clause License](https://opensource.org/licenses/BSD-2-Clause).
- **Custom Scrollbars**: [SimpleBar](https://github.com/Grsmto/simplebar) - Licensed under the [MIT License](https://opensource.org/licenses/MIT).
- **Range Slider**: [noUiSlider](https://github.com/leongersen/noUiSlider) - Licensed under the [MIT License](https://opensource.org/licenses/MIT).
- **Number Formatting**: [wNumb](https://github.com/leongersen/wnumb) - Licensed under the [MIT License](https://opensource.org/licenses/MIT).
