![screenshot](https://github.com/unfoldadmin/django-unfold/assets/10785882/daef6e7e-e8a1-4142-8e4c-fa2a287978d2)

## Unfold Django Admin Theme

[![Build](https://img.shields.io/github/actions/workflow/status/unfoldadmin/django-unfold/release.yml?style=for-the-badge)](https://github.com/unfoldadmin/django-unfold/actions?query=workflow%3Arelease)
[![PyPI - Version](https://img.shields.io/pypi/v/django-unfold.svg?style=for-the-badge)](https://pypi.org/project/django-unfold/)
![Code Style - Black](https://img.shields.io/badge/code%20style-black-000000.svg?style=for-the-badge)
![Pre Commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white&style=for-the-badge)

Unfold is theme for Django admin incorporating most common practises for building full-fledged admin areas. It is designed to work at the top of default administration provided by Django.

Demo is available at [unfoldadmin.com](https://unfoldadmin.com).

## Features

- **Visual**: provides new user interface based on Tailwind CSS framework
- **Sidebar:** simplifies definition of custom sidebar navigation with icons
- **Dark mode:** supports both light and dark mode versions
- **Configuration:** most of the basic options can be changed in settings.py
- **Dependencies:** completely based only on `django.contrib.admin`
- **Actions:** multiple ways how to define actions within different parts of admin
- **WYSIWYG:** built-in support for WYSIWYG (Trix)
- **Numeric filters:** widgets for filtering number values
- **Datetime filters:** widgets for filtering datetime values
- **Dashboard:** helpers to bootstrap custom dashboard
- **Tabs:** define custom tab navigations for models
- **Colors:** possibility to override default color scheme
- **Django import / export:** default support for this popular application

## Table of Contents

- [Installation](#installation)
- [Configuration](#configuration)
  - [Available settings.py options](#available-settingspy-options)
  - [Available unfold.admin.ModelAdmin options](#available-unfoldadminmodeladmin-options)
- [Decorators](#decorators)
  - [@display](#display)
- [Actions](#actions)
  - [Actions overview](#actions-overview)
  - [Custom unfold @action decorator](#custom-unfold-action-decorator)
  - [Action handler functions](#action-handler-functions)
    - [For submit row action](#for-submit-row-action)
    - [For global, row and detail action](#for-global-row-and-detail-action)
  - [Action examples](#action-examples)
- [Filters](#filters)
- [Third party packages](#third-party-packages)
  - [django-import-export](#django-import-export)
- [User Admin Form](#user-admin-form)
- [Adding Custom Styles and Scripts](#adding-custom-styles-and-scripts)
- [Project Level Tailwind Stylesheet](#project-level-tailwind-stylesheet)
- [Custom Admin Dashboard](#custom-admin-dashboard)
- [Unfold Development](#unfold-development)
  - [Pre-commit](#pre-commit)
  - [Poetry Configuration](#poetry-configuration)
  - [Compiling Tailwind](#compiling-tailwind)
- [Credits](#credits)

## Installation

The installation process is minimal. Everything what is needed after installation is to put new application at the beginning of **INSTALLED_APPS**. Default admin configuration in urls.py can stay as it is and there are no changes required.

```python
# settings.py

INSTALLED_APPS = [
    "unfold",  # before django.contrib.admin
    "unfold.contrib.filters",  # optional, if special filters are needed
    "unfold.contrib.forms",  # optional, if special form elements are needed
    "unfold.contrib.import_export",  # optional, if django-import-export package is used
    "django.contrib.admin",  # required
]
```

In case you need installation command below are the versions for `pip` and `poetry` which needs to be executed in shell.

```bash
pip install django-unfold
poetry add django-unfold
```

Just for an example below is the minimal admin configuration in terms of adding Unfold into URL paths.

```python
# urls.py

from django.contrib import admin
from django.urls import path

urlpatterns = [
    path("admin/", admin.site.urls),
    # Other URL paths
]
```

After installation, it is required that admin classes are going to inherit from custom `ModelAdmin` available in `unfold.admin`.

```python
# admin.py

from django.contrib import admin
from unfold.admin import ModelAdmin


@admin.register(MyModel)
class CustomAdminClass(ModelAdmin):
    pass
```

**Note:** Registered admin models coming from third party packages are not going to properly work with Unfold because of parent class. By default, these models are registered by using `django.contrib.admin.ModelAdmin` but it is needed to use `unfold.admin.ModelAdmin`. Solution for this problem is to unregister model and then again register it back by using `unfold.admin.ModelAdmin`.

```python
# admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User

from unfold.admin import ModelAdmin


admin.site.unregister(User)


@admin.register(User)
class UserAdmin(BaseUserAdmin, ModelAdmin):
    pass
```

## Configuration

### Available settings.py options

```python
# settings.py

from django.templatetags.static import static
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _

UNFOLD = {
    "SITE_TITLE": None,
    "SITE_HEADER": None,
    "SITE_URL": "/",
    "SITE_ICON": lambda request: static("logo.svg"),
    "SITE_SYMBOL": "speed",  # symbol from icon set
    "DASHBOARD_CALLBACK": "sample_app.dashboard_callback",
    "LOGIN": {
        "image": lambda r: static("sample/login-bg.jpg"),
        "redirect_after": lambda r: reverse_lazy("admin:APP_MODEL_changelist"),
    },
    "STYLES": [
        lambda request: static("css/style.css"),
    ],
    "SCRIPTS": [
        lambda request: static("js/script.js"),
    ],
    "COLORS": {
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
        },
    },
    "EXTENSIONS": {
        "modeltranslation": {
            "flags": {
                "en": "🇬🇧",
                "fr": "🇫🇷",
                "nl": "🇧🇪",
            },
        },
    },
    "SIDEBAR": {
        "show_search": False,  # Search in applications and models names
        "show_all_applications": False,  # Dropdown with all applications and models
        "navigation": [
            {
                "title": _("Navigation"),
                "separator": True,  # Top border
                "items": [
                    {
                        "title": _("Dashboard"),
                        "icon": "dashboard",  # Supported icon set: https://fonts.google.com/icons
                        "link": reverse_lazy("admin:index"),
                        "badge": "sample_app.badge_callback",
                    },
                    {
                        "title": _("Users"),
                        "icon": "people",
                        "link": reverse_lazy("admin:users_user_changelist"),
                    },
                ],
            },
        ],
    },
    "TABS": [
        {
            "models": [
                "app_label.model_name_in_lowercase",
            ],
            "items": [
                {
                    "title": _("Your custom title"),
                    "link": reverse_lazy("admin:app_label_model_name_changelist"),
                },
            ],
        },
    ],
}


def dashboard_callback(request, context):
    """
    Callback to prepare custom variables for index template which is used as dashboard
    template. It can be overridden in application by creating custom admin/index.html.
    """
    context.update(
        {
            "sample": "example",  # this will be injected into templates/admin/index.html
        }
    )
    return context


def badge_callback(request):
    return 3
```

### Available unfold.admin.ModelAdmin options

```python
from django import models
from django.contrib import admin
from django.db import models
from unfold.admin import ModelAdmin
from unfold.contrib.forms.widgets import WysiwygWidget


@admin.register(MyModel)
class CustomAdminClass(ModelAdmin):
    # Preprocess content of readonly fields before render
    readonly_preprocess_fields = {
        "model_field_name": "html.unescape",
        "other_field_name": lambda content: content.strip(),
    }

    # Display submit button in filters
    list_filter_submit = False

    # Custom actions
    actions_list = []  # Displayed above the results list
    actions_row = []  # Displayed in a table row in results list
    actions_detail = []  # Displayed at the top of for in object detail
    actions_submit_line = []  # Displayed near save in object detail

    formfield_overrides = {
        models.TextField: {
            "widget": WysiwygWidget,
        }
    }
```

## Decorators

### @display

Unfold introduces it's own `unfold.decorators.display` decorator. By default it has exactly same behavior as native `django.contrib.admin.decorators.display` but it adds same customizations which helps to extends default logic.

`@display(label=True)`, `@display(label={"value1": "success"})` displays a result as a label. This option fits for different types of statuses. Label can be either boolean indicating we want to use label with default color or dict where the dict is responsible for displaying labels in different colors. At the moment these color combinations are supported: success(green), info(blue), danger(red) and warning(orange).

`@display(header=True)` displays in results list two information in one table cell. Good example is when we want to display customer information, first line is going to be customer's name and right below the name display corresponding email address. Method with such a decorator is supposed to return a list with two elements `return "Full name", "E-mail address"`.

```python
# models.py

from django.db.models import TextChoices
from django.utils.translation import gettext_lazy as _

from unfold.admin import ModelAdmin
from unfold.decorators import display


class UserStatus(TextChoices):
    ACTIVE = "ACTIVE", _("Active")
    PENDING = "PENDING", _("Pending")
    INACTIVE = "INACTIVE", _("Inactive")
    CANCELLED = "CANCELLED", _("Cancelled")


class UserAdmin(ModelAdmin):
    list_display = [
        "display_as_two_line_heading",
        "show_status",
        "show_status_with_custom_label",
    ]

    @display(
        description=_("Status"),
        ordering="status",
        label=True
    )
    def show_status_default_color(self, obj):
        return obj.status


    @display(
        description=_("Status"),
        ordering="status",
        label={
            UserStatus.ACTIVE: "success",  # green
            UserStatus.PENDING: "info",  # blue
            UserStatus.INACTIVE: "warning",  # orange
            UserStatus.CANCELLED: "danger",  # red
        },
    )
    def show_status_customized_color(self, obj)
        return obj.status

    @display(description=_("Status with label"), ordering="status", label=True)
    def show_status_with_custom_label(self, obj):
        return obj.status, obj.get_status_display()

    @display(header=True)
    def display_as_two_line_heading(self, obj):
        return "First main heading", "Smaller additional description"
```

## Actions

It is highly recommended to read the base [Django actions documentation](https://docs.djangoproject.com/en/4.2/ref/contrib/admin/actions/) before reading this section, since Unfold actions are derived from Django actions.

### Actions overview

Besides traditional actions selected from dropdown, Unfold supports several other types of actions. Following table
gives overview of all available actions together with their recommended usage:

| Type of action | Appearance                               | Usage                                                                                      | Examples of usage                      |
| -------------- | ---------------------------------------- | ------------------------------------------------------------------------------------------ | -------------------------------------- |
| Default        | List view - top of listing (in dropdown) | Actions, where you want to select specific subset of instances to perform this action upon | Bulk deleting, bulk activation         |
| Global         | List view - top of listing (as buttons)  | General actions for model, without selecting specific instances                            | Import, export                         |
| Row            | List view - in each row                  | Action for one specific instance, executable from listing                                  | Activation, sync with external service |
| Detail         | Detail view - top of detail              | Action for one specific instance, executable from detail                                   | Activation, sync with external service |
| Submit line    | Detail view - near submit button         | Action performed during form submit (instance save)                                        | Publishing article together with save  |

### Custom unfold @action decorator

Unfold also uses custom `@action` decorator, supporting 2 more parameters in comparison to base `@action` decorator:

- `url_path`: Action path name, used to override the path under which the action will be available
  (if not provided, URL path will be generated by Unfold)
- `attrs`: Dictionary of the additional attributes added to the `<a>` element, used for e.g. opening action in new tab (`{"target": "_blank"}`)

### Action handler functions

This section provides explanation of how the action handler functions should be constructed for Unfold actions.
For default actions, follow official Django admin documentation.

#### For submit row action

Submit row actions work a bit differently when compared to other custom Unfold actions.
These actions first invoke form save (same as if you hit `Save` button) and then lets you
perform additional logic on already saved instance.

#### For global, row and detail action

All these actions are based on custom URLs generated for each of them. Handler function for these views is
basically function based view.

For actions without intermediate steps, you can write all the logic inside handler directly. Request and object ID
are both passed to these action handler functions, so you are free to fetch the instance from database and perform any
operations with it. In the end, it is recommended to return redirect back to either detail or listing, based on where
the action was triggered from.

For actions with intermediate steps, it is recommended to use handler function only to redirect to custom URL with custom
view. This view can be extended from base Unfold view, to have unified experience.

If that's confusing, there are examples for both these actions in next section.

### Action examples

```python
# admin.py

from django.db.models import Model
from django.contrib.admin import register
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.http import HttpRequest
from unfold.admin import ModelAdmin
from unfold.decorators import action


class User(Model):
    pass


@register(User)
class UserAdmin(ModelAdmin):
    actions_list = ["changelist_global_action_import"]
    actions_row = ["changelist_row_action_view_on_website"]
    actions_detail = ["change_detail_action_block"]
    actions_submit_line = ["submit_line_action_activate"]

    @action(description=_("Save & Activate"))
    def submit_line_action_activate(self, request: HttpRequest, obj: User):
        """
        If instance is modified in any way, it also needs to be saved,
        since this handler is invoked after instance is saved.
        :param request:
        :param obj: Model instance that was manipulated, with changes already saved to database
        :return: None, this handler should not return anything
        """
        obj.is_active = True
        obj.save()

    @action(description=_("Import"), url_path="import")
    def changelist_global_action_import(self, request: HttpRequest):
        """
        Handler for global actions does not receive any queryset or object ids, because it is
        meant to be used for general actions for given model.
        :param request:
        :return: View, as described in section above
        """
        # This is example of action redirecting to custom page, where the action will be handled
        # (with intermediate steps)
        return redirect(
          reverse_lazy("view-where-import-will-be-handled")
        )

    @action(description=_("Row"), url_path="row-action", attrs={"target": "_blank"})
    def changelist_row_action_view_on_website(self, request: HttpRequest, object_id: int):
        """
        Handler for list row action.
        :param request:
        :param object_id: ID of instance that this action was invoked for
        :return: View, as described in section above
        """
        return redirect(f"https://example.com/{object_id}")

    @action(description=_("Detail"), url_path="detail-action", attrs={"target": "_blank"})
    def change_detail_action_block(self, request: HttpRequest, object_id: int):
        """
        Handler for detail action.
        :param request:
        :param object_id: ID of instance that this action was invoked for
        :return: View, as described in section above
        """
        # This is example of action that handled whole logic inside handler
        # function and redirects back to object detail
        user = User.objects.get(pk=object_id)
        user.block()
        return redirect(
            reverse_lazy("admin:users_user_change", args=(object_id,))
        )
```

## Filters

By default, Django admin handles all filters as regular HTML links pointing at the same URL with different query parameters. This approach is for basic filtering more than enough. In the case of more advanced filtering by incorporating input fields, it is not going to work.

Currently, Unfold implements numeric filters inside `unfold.contrib.filters` application. In order to use these filters, it is required to add this application into `INSTALLED_APPS` in `settings.py` right after `unfold` application.

```python
# admin.py

from django.contrib import admin
from django.contrib.auth.models import User

from unfold.admin import ModelAdmin
from unfold.contrib.filters.admin import (
    RangeNumericListFilter,
    RangeNumericFilter,
    SingleNumericFilter,
    SliderNumericFilter,
    RangeDateFilter,
    RangeDateTimeFilter,
)


class CustomSliderNumericFilter(SliderNumericFilter):
    MAX_DECIMALS = 2
    STEP = 10


class CustomRangeNumericListFilter(RangeNumericListFilter):
    parameter_name = "items_count"
    title = "items"


@admin.register(User)
class YourModelAdmin(ModelAdmin):
    list_filter_submit = True  # Submit button at the bottom of the filter
    list_filter = (
        ("field_A", SingleNumericFilter),  # Numeric single field search, __gte lookup
        ("field_B", RangeNumericFilter),  # Numeric range search, __gte and __lte lookup
        ("field_C", SliderNumericFilter),  # Numeric range filter but with slider
        ("field_D", CustomSliderNumericFilter),  # Numeric filter with custom attributes
        ("field_E", RangeDateFilter),  # Date filter
        ("field_F", RangeDateTimeFilter),  # Datetime filter
        CustomRangeNumericListFilter,  # Numeric range search not restricted to a model field
    )

    def get_queryset(self, request):
        return super().get_queryset().annotate(items_count=Count("item", distinct=True))
```

## Third party packages

### django-import-export

To get proper visual appearance for django-import-export, two things are needed

1. Add `unfold.contrib.import_export` to `INSTALLED_APPS` at the begging of the file. This action will override all templates coming from the plugin.
2. Change `import_form_class` and `export_form_class` in ModelAdmin which is inheriting from `ImportExportModelAdmin`. This chunk of code is responsible for adding proper styling to form elements.

```python
from unfold.admin import ModelAdmin
from unfold.contrib.import_export.forms import ExportForm, ImportForm

class ExampleAdmin(ModelAdmin, ImportExportModelAdmin):
    import_form_class = ImportForm
    export_form_class = ExportForm
```

## User Admin Form

User's admin in Django is specific as it contains several forms which are requiring custom styling. All of these forms has been inherited and accordingly adjusted. In user admin class it is needed to use these inherited form classes to enable custom styling matching rest of the website.

```python
# models.py

from django.contrib.admin import register
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from unfold.admin import ModelAdmin
from unfold.forms import AdminPasswordChangeForm, UserChangeForm, UserCreationForm


@register(User)
class UserAdmin(BaseUserAdmin, ModelAdmin):
    form = UserChangeForm
    add_form = UserCreationForm
    change_password_form = AdminPasswordChangeForm
```

## Adding Custom Styles and Scripts

To add new custom styles, for example for custom dashboard, it is possible to load them via **STYLES** key in **UNFOLD** dict. This key accepts a list of strings or lambda functions which will be loaded on all pages. JavaScript files can be loaded by using similar apprach, but **SCRIPTS** is used.

```python
# settings.py

from django.templatetags.static import static

UNFOLD = {
    "STYLES": [
        lambda request: static("css/style.css"),
    ],
    "SCRIPTS": [
        lambda request: static("js/script.js"),
    ],
}
```

## Project Level Tailwind Stylesheet

When creating custom dashboard or adding custom components, it is needed to add own styles. Adding custom styles is described above. Most of the time, it is supposed that new elements are going to match with the rest of the administration panel. First of all, create tailwind.config.js in your application. Below is located minimal configuration for this file.

```javascript
// tailwind.config.js

module.exports = {
  content: ["./your_project/**/*.{html,py,js}"],
  // In case custom colors are defined in UNFOLD["COLORS"]
  colors: {
    primary: {
      50: "rgb(var(--color-primary-50) / <alpha-value>)",
      100: "rgb(var(--color-primary-100) / <alpha-value>)",
      200: "rgb(var(--color-primary-200) / <alpha-value>)",
      300: "rgb(var(--color-primary-300) / <alpha-value>)",
      400: "rgb(var(--color-primary-400) / <alpha-value>)",
      500: "rgb(var(--color-primary-500) / <alpha-value>)",
      600: "rgb(var(--color-primary-600) / <alpha-value>)",
      700: "rgb(var(--color-primary-700) / <alpha-value>)",
      800: "rgb(var(--color-primary-800) / <alpha-value>)",
      900: "rgb(var(--color-primary-900) / <alpha-value>)",
    },
  },
};
```

Once the configuration file is set, it is possible to compile new styles which can be loaded into admin by using **STYLES** key in **UNFOLD** dict.

```bash
npx tailwindcss -o your_project/static/css/styles.css --watch --minify
```

## Custom Admin Dashboard

The most common thing which needs to be adjusted for each project in admin is the dashboard. By default Unfold does not provide any dashboard components. The default dashboard experience with list of all applications and models is kept with proper styling matching rest of the components but thats it. Anyway, Unfold was created that creation of custom dashboard will be streamlined.

Create `templates/admin/index.html` in your project and paste the base template below into it. By default, all your custom styles here are not compiled because CSS classes are located in your specific project. Here it is needed to set up the Tailwind for your project and all requried instructions are located in [Project Level Tailwind Stylesheet](#project-level-tailwind-stylesheet) chapter.

```
{% extends 'unfold/layouts/base_simple.html' %}

{% load cache humanize i18n %}

{% block breadcrumbs %}{% endblock %}

{% block title %}{% if subtitle %}{{ subtitle }} | {% endif %}{{ title }} | {{ site_title|default:_('Django site admin') }}{% endblock %}

{% block branding %}
    <h1 id="site-name"><a href="{% url 'admin:index' %}">{{ site_header|default:_('Django administration') }}</a></h1>
{% endblock %}

{% block content %}
    Start creating your own Tailwind components here
{% endblock %}
```

Note: In case that it is needed to pass custom variables into dashboard tamplate, check **DASHOARD_CALLBACK** in **UNFOLD** dict.

## Unfold Development

### Pre-commit

Before adding any source code, it is recommended to have pre-commit installed on your local computer to check for all potential issues when comitting the code.

```bash
pip install pre-commit
pre-commit install
pre-commit install --hook-type commit-msg
```

### Poetry Configuration

To add a new feature or fix the easiest approach is to use django-unfold in combination with Poetry. The process looks like:

- Install django-unfold via `poetry add django-unfold`
- After that it is needed to git clone the repository somewhere on local computer.
- Edit _pyproject.toml_ and update django-unfold line `django-unfold = { path = "../django-unfold", develop = true}`
- Lock and update via `poetry lock && poetry update`

### Compiling Tailwind

At the moment project contains package.json with all dependencies required to compile new CSS file. Tailwind configuration file is set to check all html, js and py files for Tailwind's classeses occurrences.

```bash
npm install
npx tailwindcss -i src/unfold/styles.css -o src/unfold/static/unfold/css/styles.css --watch --minify

npm run tailwind:watch # run after each change in code
npm run tailwind:build # run once
```

Some components like datepickers, calendars or selectors in admin was not possible to style by overriding html templates so their default styles are overriden in **styles.css**.

None: most of the custom styles localted in style.css are created via `@apply some-tailwind-class;`.

# Credits

- [TailwindCSS](https://tailwindcss.com/) - CSS framework
- [HTMX](https://htmx.org/) - AJAX communication with backend
- [Material Icons](https://fonts.google.com/icons) - Icons from Google Fonts
- [Trix](https://trix-editor.org/) - WYSIWYG editor
- [Alpine.js](https://alpinejs.dev/) - JavaScript interactions
