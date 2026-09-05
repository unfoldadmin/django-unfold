<p align="center">
    <a href="https://unfoldadmin.com/?utm_source=github&utm_medium=readme">
        <img width="100" alt="Unfold" src="https://github.com/user-attachments/assets/32d2c3a3-8882-4ee7-9183-1059f7f006cc" />
    </a>
    <h1 align="center">Unfold - Modern Django Admin</h1>
</p>

<p align="center">
    A modern Django admin theme for building dashboards, internal tools, and business applications
</p>

<p align="center">
    <a href="https://demo.unfoldadmin.com/?utm_source=github&utm_medium=readme">Live demo</a> ·
    <a href="https://unfoldadmin.com/docs/?utm_source=github&utm_medium=readme">Documentation</a> ·
    <a href="https://unfoldadmin.com/studio/?utm_source=github&utm_medium=readme">Studio</a> ·
    <a href="https://discord.gg/9sQj9MEbNz">Discord</a> ·
    <a href="https://pypi.org/project/django-unfold/">PyPI</a>
</p>

<p align="center">
    <a href="https://pypi.org/project/django-unfold/">
        <img src="https://img.shields.io/pypi/v/django-unfold.svg?style=for-the-badge" alt="PyPI - Version" />
    </a>
    <a href="https://discord.gg/9sQj9MEbNz">
        <img src="https://img.shields.io/discord/1297493955231088650?style=for-the-badge&logo=discord&logoColor=%23ffffff&color=7289da" alt="Discord" />
    </a>
    <a href="https://pypi.org/project/django-unfold/">
        <img src="https://img.shields.io/pypi/dm/django-unfold?style=for-the-badge" alt="Monthly downloads" />
    </a>
</p>

<a href="https://demo.unfoldadmin.com?utm_source=github&utm_medium=readme">
    <img alt="Unfold dashboard" src="https://github.com/user-attachments/assets/3529be8e-c318-46cd-b986-575419927ad6" />
</a>


## Quickstart

**Install the package**

```sh
pip install django-unfold
```

**Add Unfold to INSTALLED_APPS**

```python
INSTALLED_APPS = [
    "unfold",  # First in the list
]
```

**Use Unfold's ModelAdmin**

```python
from django.contrib import admin
from unfold.admin import ModelAdmin


@admin.register(MyModel)
class MyModelAdmin(ModelAdmin):
    pass
```

## Why Unfold?

- **Django native** - Built on `django.contrib.admin`, preserving familiar models, permissions, and workflows.
- **Incremental adoption** - Introduce Unfold gradually without rebuilding your existing admin.
- **Built for real applications** - Designed for dashboards, internal tools, backoffice systems, and complex admin interfaces.

## Features

- **Modern interface** - Responsive Tailwind CSS design with dark mode, customizable colors, layout options, and other visual settings for a polished admin experience.
- **Dashboards and components** - Build custom dashboards and admin pages using reusable cards, charts, buttons, and other UI components for internal applications.
- **Advanced filtering** - Dropdown, autocomplete, text, numeric, date range, checkbox, radio, and facet filters for more powerful and flexible changelists.
- **Flexible actions** - Add global, row-level, detail, submit, and dropdown actions with custom permissions, styles, and flexible placement options across the admin.
- **Navigation and tabs** - Customize the sidebar and organize models, fieldsets, and inlines using flexible tab navigation and layout options for complex interfaces.
- **Enhanced forms and inlines** - Conditional fields, sortable and paginated inlines, WYSIWYG editing, ArrayField widgets, and django-crispy-forms support for richer admin forms.
- **Third-party integrations** - Built-in support for popular Django packages including django-import-export, django-guardian, django-simple-history, django-constance, and more.

[Explore all features](https://unfoldadmin.com/features/?utm_source=github&utm_medium=readme)

## Commercial options

- **Consulting**: Guidance on Django architecture, performance, features, and Unfold integration. [Learn more](https://unfoldadmin.com/consulting/?utm_source=github&utm_medium=readme)
- **Support**: Help with setup or customization, live calls, and review. [Learn more](https://unfoldadmin.com/support/?utm_source=github&utm_medium=readme)
- **Studio**: Extend Unfold with advanced dashboards, customization, and admin tooling. [Learn more](https://unfoldadmin.com/studio?utm_source=github&utm_medium=readme)

[![Unfold Studio dashboards](https://github.com/user-attachments/assets/7c3124ab-2f59-4254-9222-8a57970f51a6)](https://unfoldadmin.com/studio?utm_source=github&utm_medium=readme)

## Third-party package support

- [django-guardian](https://github.com/django-guardian/django-guardian) - [Integration guide](https://unfoldadmin.com/docs/integrations/django-guardian/?utm_source=github&utm_medium=readme)
- [django-import-export](https://github.com/django-import-export/django-import-export) - [Integration guide](https://unfoldadmin.com/docs/integrations/django-import-export/?utm_source=github&utm_medium=readme)
- [django-simple-history](https://github.com/jazzband/django-simple-history) - [Integration guide](https://unfoldadmin.com/docs/integrations/django-simple-history/?utm_source=github&utm_medium=readme)
- [django-constance](https://github.com/jazzband/django-constance) - [Integration guide](https://unfoldadmin.com/docs/integrations/django-constance/?utm_source=github&utm_medium=readme)
- [django-celery-beat](https://github.com/celery/django-celery-beat) - [Integration guide](https://unfoldadmin.com/docs/integrations/django-celery-beat/?utm_source=github&utm_medium=readme)
- [django-money](https://github.com/django-money/django-money) - [Integration guide](https://unfoldadmin.com/docs/integrations/django-money/?utm_source=github&utm_medium=readme)
- [django-location-field](https://github.com/caioariede/django-location-field) - [Integration guide](https://unfoldadmin.com/docs/integrations/django-location-field/?utm_source=github&utm_medium=readme)
- [djangoql](https://github.com/ivelum/djangoql) - [Integration guide](https://unfoldadmin.com/docs/integrations/djangoql/?utm_source=github&utm_medium=readme)
- [django-json-widget](https://github.com/jmrivas86/django-json-widget) - [Integration guide](https://unfoldadmin.com/docs/integrations/django-json-widget/?utm_source=github&utm_medium=readme)
- [django-hijack](https://github.com/django-hijack/django-hijack) - [Integration guide](https://unfoldadmin.com/docs/integrations/django-hijack/?utm_source=github&utm_medium=readme)
- [django-waffle](https://github.com/django-waffle/django-waffle) - [Integration guide](https://unfoldadmin.com/docs/integrations/django-waffle/?utm_source=github&utm_medium=readme)

## Credits

- [Tailwind CSS](https://github.com/tailwindlabs/tailwindcss) - Licensed under the [MIT License](https://opensource.org/licenses/MIT).
- [Material Symbols](https://github.com/google/material-design-icons) - Licensed under the [Apache License 2.0](https://www.apache.org/licenses/LICENSE-2.0).
- [Inter](https://github.com/rsms/inter) - Licensed under the [SIL Open Font License 1.1](https://scripts.sil.org/OFL).
- [Chart.js](https://github.com/chartjs/Chart.js) - Licensed under the [MIT License](https://opensource.org/licenses/MIT).
- [Alpine.js](https://github.com/alpinejs/alpine) - Licensed under the [MIT License](https://opensource.org/licenses/MIT).
- [HTMX](https://htmx.org/) - Licensed under the [BSD 2-Clause License](https://opensource.org/licenses/BSD-2-Clause).
- [Trix](https://github.com/basecamp/trix) - Licensed under the [MIT License](https://opensource.org/licenses/MIT).
