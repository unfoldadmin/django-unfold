<p align="center">
    <a href="https://unfoldadmin.com/">
        <img width="100" height="100" alt="Unfold" src="https://github.com/user-attachments/assets/32d2c3a3-8882-4ee7-9183-1059f7f006cc" />
    </a>
    <h1 align="center">Unfold - Modern Django Admin</h1>
</p>

<p align="center">
    A modern Django admin theme for building dashboards, internal tools, and business applications
</p>

<p align="center">
    <a href="https://demo.unfoldadmin.com/">Live demo</a> ·
    <a href="https://unfoldadmin.com/docs/">Documentation</a> ·
    <a href="https://unfoldadmin.com/studio/">Studio</a> ·
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

<a href="https://demo.unfoldadmin.com">
    <img width="2560" height="1936" alt="Unfold dashboard" src="https://github.com/user-attachments/assets/3529be8e-c318-46cd-b986-575419927ad6" />
</a>


## Quickstart

**Install the package**

```sh
pip install django-unfold
```

**Change INSTALLED_APPS in settings.py**

```python
INSTALLED_APPS = [
    "unfold",  # First in the list
]
```

**Use Unfold ModelAdmin**

```python
from unfold.admin import ModelAdmin


@admin.register(MyModel)
class MyModelAdmin(ModelAdmin):
    pass
```

## Why Unfold?

- Built on `django.contrib.admin`: Enhances the existing admin without replacing it.
- Provides a modern interface and improved workflows.
- Designed for real internal tools and backoffice apps.
- Incremental adoption for existing projects.

## Features

* **Modern interface** - Responsive Tailwind CSS design with dark mode, customizable colors, layout options, and other visual settings.
* **Dashboards and components** - Build custom dashboards and admin pages using reusable cards, charts, buttons, and other UI components.
* **Advanced filtering** - Dropdown, autocomplete, text, numeric, date range, checkbox, radio, and facet filters for changelists.
* **Flexible actions** - Add global, row-level, detail, submit, and dropdown actions with custom permissions and styles.
* **Navigation and tabs** - Customize the sidebar and organize models, fieldsets, and inlines using flexible tab navigation.
* **Enhanced forms and inlines** - Conditional fields, sortable and paginated inlines, WYSIWYG editing, ArrayField widgets, and django-crispy-forms support.
* **Built on Django admin** - Extend `django.contrib.admin` incrementally while keeping existing Django admin concepts, permissions, and workflows.
* **Third-party integrations** - Built-in support for popular Django packages including django-import-export, django-guardian, django-simple-history, django-constance, and more.

[Explore all features →](https://unfoldadmin.com/features/)


## Professional services

- **Consulting**: Guidance on Django architecture, performance, features, and Unfold integration. [Learn more](https://unfoldadmin.com/consulting/?utm_medium=github&utm_source=unfold)
- **Support**: Help with setup or customization, live calls, and review. [Learn more](https://unfoldadmin.com/support/?utm_medium=github&utm_source=unfold)
- **Studio**: Extend Unfold with advanced dashboards, customization, and admin tooling. [Learn more](https://unfoldadmin.com/studio?utm_medium=github&utm_source=unfold)

[![dashboards](https://github.com/user-attachments/assets/7c3124ab-2f59-4254-9222-8a57970f51a6)](https://unfoldadmin.com/studio?utm_medium=github&utm_source=unfold)

## Third-party package support

- [django-guardian](https://github.com/django-guardian/django-guardian) - [Integration guide](https://unfoldadmin.com/docs/integrations/django-guardian/)
- [django-import-export](https://github.com/django-import-export/django-import-export) - [Integration guide](https://unfoldadmin.com/docs/integrations/django-import-export/)
- [django-simple-history](https://github.com/jazzband/django-simple-history) - [Integration guide](https://unfoldadmin.com/docs/integrations/django-simple-history/)
- [django-constance](https://github.com/jazzband/django-constance) - [Integration guide](https://unfoldadmin.com/docs/integrations/django-constance/)
- [django-celery-beat](https://github.com/celery/django-celery-beat) - [Integration guide](https://unfoldadmin.com/docs/integrations/django-celery-beat/)
- [django-money](https://github.com/django-money/django-money) - [Integration guide](https://unfoldadmin.com/docs/integrations/django-money/)
- [django-location-field](https://github.com/caioariede/django-location-field) - [Integration guide](https://unfoldadmin.com/docs/integrations/django-location-field/)
- [djangoql](https://github.com/ivelum/djangoql) - [Integration guide](https://unfoldadmin.com/docs/integrations/djangoql/)
- [django-json-widget](https://github.com/jmrivas86/django-json-widget) - [Integration guide](https://unfoldadmin.com/docs/integrations/django-json-widget/)
- [django-hijack](https://github.com/django-hijack/django-hijack) - [Integration guide](https://unfoldadmin.com/docs/integrations/django-hijack/)
- [django-waffle](https://github.com/django-waffle/django-waffle) - [Integration guide](https://unfoldadmin.com/docs/integrations/django-waffle/)

## Credits

- [Tailwind CSS](https://github.com/tailwindlabs/tailwindcss) - Licensed under the [MIT License](https://opensource.org/licenses/MIT).
- [Material Symbols](https://github.com/google/material-design-icons) - Licensed under the [Apache License 2.0](https://www.apache.org/licenses/LICENSE-2.0).
- [Inter](https://github.com/rsms/inter) - Licensed under the [SIL Open Font License 1.1](https://scripts.sil.org/OFL).
- [Chart.js](https://github.com/chartjs/Chart.js) - Licensed under the [MIT License](https://opensource.org/licenses/MIT).
- [Alpine.js](https://github.com/alpinejs/alpine) - Licensed under the [MIT License](https://opensource.org/licenses/MIT).
- [HTMX](https://htmx.org/) - Licensed under the [BSD 2-Clause License](https://opensource.org/licenses/BSD-2-Clause).
- [Trix](https://github.com/basecamp/trix) - Licensed under the [MIT License](https://opensource.org/licenses/MIT).
