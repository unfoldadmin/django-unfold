[![screenshot-light](https://github.com/unfoldadmin/django-unfold/assets/10785882/291e69c9-abdd-4f7e-a0d6-2af210a9013a#gh-light-mode-only)](https://github.com/unfoldadmin/django-unfold/assets/10785882/291e69c9-abdd-4f7e-a0d6-2af210a9013a#gh-light-mode-only)

[![screenshot-dark](https://github.com/unfoldadmin/django-unfold/assets/10785882/94a2e90f-924a-4aaf-b6d9-cb1592000c55#gh-dark-mode-only)](https://github.com/unfoldadmin/django-unfold/assets/10785882/94a2e90f-924a-4aaf-b6d9-cb1592000c55#gh-dark-mode-only)

## Unfold Django Admin Theme <!-- omit from toc -->

[![Build](https://img.shields.io/github/actions/workflow/status/unfoldadmin/django-unfold/release.yml?style=for-the-badge)](https://github.com/unfoldadmin/django-unfold/actions?query=workflow%3Arelease)
[![PyPI - Version](https://img.shields.io/pypi/v/django-unfold.svg?style=for-the-badge)](https://pypi.org/project/django-unfold/)
![Code Style - Black](https://img.shields.io/badge/code%20style-black-000000.svg?style=for-the-badge)
![Pre Commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white&style=for-the-badge)

Unfold is theme for Django admin incorporating most common practises for building full-fledged admin areas. It is designed to work at the top of default administration provided by Django.

- **Unfold:** demo site is available at [unfoldadmin.com](https://unfoldadmin.com)
- **Formula:** repository with demo implementation at [github.com/unfoldadmin/formula](https://github.com/unfoldadmin/formula)
- **Turbo:** Django & Next.js boilerplate implementing Unfold at [github.com/unfoldadmin/turbo](https://github.com/unfoldadmin/turbo)

## Are you using Unfold and need a help?<!-- omit from toc -->

Did you decide to start using Unfold but you don't have time to make the switch from native Django admin? [Get in touch with us](https://unfoldadmin.com/) and let's supercharge development by using our know-how.

## Features <!-- omit from toc -->

- **Visual**: provides new user interface based on Tailwind CSS framework
- **Sidebar:** simplifies definition of custom sidebar navigation with icons
- **Dark mode:** supports both light and dark mode versions
- **Configuration:** most of the basic options can be changed in settings.py
- **Dependencies:** completely based only on `django.contrib.admin`
- **Actions:** multiple ways how to define actions within different parts of admin
- **WYSIWYG:** built-in support for WYSIWYG (Trix)
- **Custom filters:** widgets for filtering number & datetime values
- **Dashboard:** custom components for rapid dashboard development
- **Model tabs:** define custom tab navigations for models
- **Fieldset tabs:** merge several fielsets into tabs in change form
- **Colors:** possibility to override default color scheme
- **Third party packages:** default support for multiple popular applications
- **Environment label**: distinguish between environments by displaying a label

## Table of contents <!-- omit from toc -->

- [Installation](#installation)
- [Configuration](#configuration)
  - [Available settings.py options](#available-settingspy-options)
  - [Available unfold.admin.ModelAdmin options](#available-unfoldadminmodeladmin-options)
- [Actions](#actions)
  - [Actions overview](#actions-overview)
  - [Custom unfold @action decorator](#custom-unfold-action-decorator)
  - [Action handler functions](#action-handler-functions)
  - [Action examples](#action-examples)
- [Filters](#filters)
  - [Numeric filters](#numeric-filters)
  - [Date/time filters](#datetime-filters)
- [Display decorator](#display-decorator)
- [Change form tabs](#change-form-tabs)
- [Third party packages](#third-party-packages)
  - [django-celery-beat](#django-celery-beat)
  - [django-guardian](#django-guardian)
  - [django-import-export](#django-import-export)
  - [django-modeltranslation](#django-modeltranslation)
  - [django-money](#django-money)
  - [django-simple-history](#django-simple-history)
- [User Admin Form](#user-admin-form)
- [Adding custom styles and scripts](#adding-custom-styles-and-scripts)
- [Project level Tailwind stylesheet](#project-level-tailwind-stylesheet)
- [Admin dashboard](#admin-dashboard)
  - [Overriding template](#overriding-template)
  - [Custom variables](#custom-variables)
  - [Unfold components](#unfold-components)
- [Unfold development](#unfold-development)
  - [Pre-commit](#pre-commit)
  - [Poetry configuration](#poetry-configuration)
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
    "unfold.contrib.guardian",  # optional, if django-guardian package is used
    "unfold.contrib.simple_history",  # optional, if django-simple-history package is used
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
    # "SITE_ICON": lambda request: static("icon.svg"),  # both modes, optimise for 32px height
    "SITE_ICON": {
        "light": lambda request: static("icon-light.svg"),  # light mode
        "dark": lambda request: static("icon-dark.svg"),  # dark mode
    },
    # "SITE_LOGO": lambda request: static("logo.svg"),  # both modes, optimise for 32px height
    "SITE_LOGO": {
        "light": lambda request: static("logo-light.svg"),  # light mode
        "dark": lambda request: static("logo-dark.svg"),  # dark mode
    },
    "SITE_SYMBOL": "speed",  # symbol from icon set
    "SHOW_HISTORY": True, # show/hide "History" button, default: True
    "SHOW_VIEW_ON_SITE": True, # show/hide "View on site" button, default: True
    "ENVIRONMENT": "sample_app.environment_callback",
    "DASHBOARD_CALLBACK": "sample_app.dashboard_callback",
    "LOGIN": {
        "image": lambda request: static("sample/login-bg.jpg"),
        "redirect_after": lambda request: reverse_lazy("admin:APP_MODEL_changelist"),
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
            "950": "59 7 100",
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
                        "permission": lambda request: request.user.is_superuser,
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
                    "permission": "sample_app.permission_callback",
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


def environment_callback(request):
    """
    Callback has to return a list of two values represeting text value and the color
    type of the label displayed in top right corner.
    """
    return ["Production", "danger"] # info, danger, warning, success


def badge_callback(request):
    return 3

def permission_callback(request):
    return request.user.has_perm("sample_app.change_model")

```

### Available unfold.admin.ModelAdmin options

```python
# admin.py

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

#### For submit row action <!-- omit from toc -->

Submit row actions work a bit differently when compared to other custom Unfold actions.
These actions first invoke form save (same as if you hit `Save` button) and then lets you
perform additional logic on already saved instance.

#### For global, row and detail action <!-- omit from toc -->

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

**Note:** when implementing a filter which contains input fields, there is a no way that user can submit the values, because default filters does not contain submit button. To implement submit button, `unfold.admin.ModelAdmin` contains boolean `list_filter_submit` flag which enables submit button in filter form.

### Numeric filters

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
        CustomRangeNumericListFilter,  # Numeric range search not restricted to a model field
    )

    def get_queryset(self, request):
        return super().get_queryset().annotate(items_count=Count("item", distinct=True))
```

### Date/time filters

```python
# admin.py

from django.contrib import admin
from django.contrib.auth.models import User

from unfold.admin import ModelAdmin
from unfold.contrib.filters.admin import (
    RangeDateFilter,
    RangeDateTimeFilter,
)


@admin.register(User)
class YourModelAdmin(ModelAdmin):
    list_filter_submit = True  # Submit button at the bottom of the filter
    list_filter = (
        ("field_E", RangeDateFilter),  # Date filter
        ("field_F", RangeDateTimeFilter),  # Datetime filter
    )
```

## Display decorator

Unfold introduces it's own `unfold.decorators.display` decorator. By default it has exactly same behavior as native `django.contrib.admin.decorators.display` but it adds same customizations which helps to extends default logic.

`@display(label=True)`, `@display(label={"value1": "success"})` displays a result as a label. This option fits for different types of statuses. Label can be either boolean indicating we want to use label with default color or dict where the dict is responsible for displaying labels in different colors. At the moment these color combinations are supported: success(green), info(blue), danger(red) and warning(orange).

`@display(header=True)` displays in results list two information in one table cell. Good example is when we want to display customer information, first line is going to be customer's name and right below the name display corresponding email address. Method with such a decorator is supposed to return a list with two elements `return "Full name", "E-mail address"`. There is a third optional argument, which is type of the string and its value is displayed in a circle before first two values on the front end. Its optimal usage is for displaying initials.

```python
# admin.py

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
    def show_status_customized_color(self, obj):
        return obj.status

    @display(description=_("Status with label"), ordering="status", label=True)
    def show_status_with_custom_label(self, obj):
        return obj.status, obj.get_status_display()

    @display(header=True)
    def display_as_two_line_heading(self, obj):
        """
        Third argument is short text which will appear as prefix in circle
        """
        return "First main heading", "Smaller additional description", "AB"
```

## Change form tabs

When the change form contains a lot of fieldsets, sometimes it is better to group them into tabs so it will not be needed to scroll. To mark a fieldset for tab navigation it is required to add a `tab` CSS class to the fieldset. Once the fieldset contains `tab` class it will be recognized in a template and grouped into tab navigation. Each tab must contain its name. If the name is not available, it will be not included in the tab navigation.

```python
# admin.py

from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from unfold.admin import ModelAdmin

from .models import MyModel


@admin.register(MyModel)
class MyModelAdmin(ModelAdmin):
    fieldsets = (
        (
            None,
            {
                "fields": [
                    "field_1",
                    "field_2",
                ],
            },
        ),
        (
            _("Tab 1"),
            {
                "classes": ["tab"],
                "fields": [
                    "field_3",
                    "field_4",
                ],
            },
        ),
        (
            _("Tab 2"),
            {
                "classes": ["tab"],
                "fields": [
                    "field_5",
                    "field_6",
                ],
            },
        ),
    )
```

## Third party packages

### django-celery-beat

In general, django-celery-beat does not have any components that require special styling. The default changelist templates are not inheriting from Unfold's `ModelAdmin` but they are using default `ModelAdmin` coming from `django.contrib.admin` which is causing some design discrepancies in the changelist.

In the source code below you can find a short code snippet to unregister all `django-celery-beat` admin classes and register them with the proper parent `ModelAdmin` class.

```python
# admin.py
from django.contrib import admin
from unfold.admin import ModelAdmin

from django_celery_beat.models import (
    ClockedSchedule,
    CrontabSchedule,
    IntervalSchedule,
    PeriodicTask,
    SolarSchedule,
)


admin.site.unregister(PeriodicTask)
admin.site.unregister(IntervalSchedule)
admin.site.unregister(CrontabSchedule)
admin.site.unregister(SolarSchedule)
admin.site.unregister(ClockedSchedule)

@admin.register(PeriodicTask)
class PeriodicTaskAdmin(ModelAdmin):
    pass


@admin.register(IntervalSchedule)
class IntervalScheduleAdmin(ModelAdmin):
    pass


@admin.register(CrontabSchedule)
class CrontabScheduleAdmin(ModelAdmin):
    pass


@admin.register(SolarSchedule)
class SolarScheduleAdmin(ModelAdmin):
    pass
```

### django-guardian

Adding support for django-guardian is quote straightforward in Unfold, just add `unfold.contrib.guardian` to `INSTALLED_APPS` at the beggining of the file. This action will override all templates coming from the django-guardian. Please note that **Object permissions** link is available in top right dropdown navigation.

### django-import-export

1. Add `unfold.contrib.import_export` to `INSTALLED_APPS` at the beggining of the file. This action will override all templates coming from the application.
2. Change `import_form_class` and `export_form_class` in ModelAdmin which is inheriting from `ImportExportModelAdmin`. This chunk of code is responsible for adding proper styling to form elements.

```python
# admin.py

from unfold.admin import ModelAdmin
from import_export.admin import ImportExportModelAdmin
from unfold.contrib.import_export.forms import ExportForm, ImportForm

class ExampleAdmin(ModelAdmin, ImportExportModelAdmin):
    import_form_class = ImportForm
    export_form_class = ExportForm
```

When implementing `import_export.admin.ExportActionModelAdmin` class in admin panel, import_export plugin adds its own implementation of action form which is not incorporating Unfold CSS classes. For this reason, `unfold.contrib.import_export.admin` contains class with the same name `ExportActionModelAdmin` which inherits behavior of parent form and adds appropriate CSS classes.

```python
admin.py

from unfold.admin import ModelAdmin
from unfold.contrib.import_export import ExportActionModelAdmin

class ExampleAdmin(ModelAdmin, ExportActionModelAdmin):
    pass
```

### django-modeltranslation

By default, Unfold supports django-modeltranslation and `TabbedTranslationAdmin` admin class for the tabbed navigation is implemented with custom styling as well.

```python
from django.contrib import admin

from modeltranslation.admin import TabbedTranslationAdmin
from unfold.admin import ModelAdmin

from .models import MyModel


@admin.register(MyModel)
class MyModelAdmin(ModelAdmin, TabbedTranslationAdmin):
    pass
```

For django-modeltranslation fields for spefic languages, it is possible to define custom flags which will appear as a suffix in field's label. It is recommended to use emojis as suffix.

```python
# settings.py

UNFOLD = {
    "EXTENSIONS": {
        "modeltranslation": {
            "flags": {
                "en": "🇬🇧",
                "fr": "🇫🇷",
                "nl": "🇧🇪",
            },
        },
    },
}
```

### django-money

This application is supported in Unfold by default. It is not needed to add any other applications into `INSTALLED_APPS`. Unfold is recognizing special form widget coming from django-money and applying specific styling.

### django-simple-history

To make this application work, add `unfold.contrib.simple_history` into `settings.py` in `INSTALLED_APPS` variable before right after `unfold`. This app should ensure that templates coming from django-simple-history are overriden by Unfold.

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

## Adding custom styles and scripts

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

## Project level Tailwind stylesheet

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
      950: "rgb(var(--color-primary-950) / <alpha-value>)",
    },
  },
};
```

Once the configuration file is set, it is possible to compile new styles which can be loaded into admin by using **STYLES** key in **UNFOLD** dict.

```bash
npx tailwindcss -o your_project/static/css/styles.css --watch --minify
```

## Admin dashboard

### Overriding template

Create `templates/admin/index.html` in your project and paste the base template below into it. By default, all your custom styles here are not compiled because CSS classes are located in your specific project. Here it is needed to set up the Tailwind for your project and all requried instructions are located in [Project Level Tailwind Stylesheet](#project-level-tailwind-stylesheet) chapter.

```html+django
{% extends 'unfold/layouts/base_simple.html' %}

{% load cache humanize i18n %}

{% block breadcrumbs %}{% endblock %}

{% block title %}
    {% if subtitle %}
        {{ subtitle }} |
    {% endif %}

    {{ title }} | {{ site_title|default:_('Django site admin') }}
{% endblock %}

{% block branding %}
    <h1 id="site-name">
        <a href="{% url 'admin:index' %}">
            {{ site_header|default:_('Django administration') }}
        </a>
    </h1>
{% endblock %}

{% block content %}
    Start creating your own Tailwind components here
{% endblock %}
```

### Custom variables

When you are building a new dashboard, you need to display some data mostly coming from the database. To pass these data to the dashboard template, Unfold contains a special `DASHBOARD_CALLBACK` parameter which allows passing a dictionary of variables to `templates/admin/index.html` template.

```python
# views.py

def dashboard_callback(request, context):
    context.update({
        "custom_variable": "value",
    })

    return context
```

```python
# settings.py

UNFOLD = {
    "DASHBOARD_CALLBACK": "app.views.dashboard_callback",
}
```

### Unfold components

Unfold provides a set of already predefined templates to speed up overall dashboard development. These templates contain predefined design which matches global design style so there is no need to spend any time adjusting styles.

The biggest benefit of Unfold components is the possibility to nest them inside one template file provides an unlimited amount of possible combinations. Then each component includes `children` variable which contains a value specified in the parent component. Except for `children` variable, components can have multiple variables coming from the parent template as component variables. These parameters can be specified in the same as parameters when using `{% include with param1=value1 param2=value2 %}` template tag.

```html+django
{% component "unfold/components/flex.html" with col=1 %}
    {% component "unfold/components/card.html" %}
        {% component "unfold/components/title.html" %}
            Card Title
        {% endcomponent %}
    {% endcomponent %}
{% endcompontent %}
```

Below you can find a more complex example which is using multiple components and processing them based on the passed variables from the `DASHBOARD_CALLBACK`.

```html+django
{% load i18n %}

{% block content %}
    {% component "unfold/components/container.html" %}
        {% component "unfold/components/flex.html" with class="gap-4"%}
            {% component "unfold/components/navigation.html" with items=navigation %}
            {% endcomponent %}

            {% component "unfold/components/navigation.html" with class="ml-auto" items=filters %}
            {% endcomponent %}
        {% endcomponent %}

        {% component "unfold/components/flex.html" with class="gap-8 mb-8 flex-col lg:flex-row" %}
            {% for card in cards %}
                {% trans "Last 7 days" as label %}
                {% component "unfold/components/card.html" with class="lg:w-1/3" %}
                    {% component "unfold/components/text.html" %}
                        {{ card.title }}
                    {% endcomponent %}

                    {% component "unfold/components/title.html" %}
                        {{ card.metric }}
                    {% endcomponent %}
                {% endcomponent %}
            {% endfor %}
        {% endcomponent %}
    {% endcomponent %}
{% endblock %}
```

#### List of available components <!-- omit from toc -->

| Component                         | Description                    | Arguments                        |
| --------------------------------- | ------------------------------ | -------------------------------- |
| unfold/components/chart/bar.html  | Bar chart implementation       | class, data, height, width       |
| unfold/components/chart/line.html | Line chart implementation      | class, data, height, width       |
| unfold/components/card.html       | Card component                 | class, title, footer, label      |
| unfold/components/container.html  | Wrapper for settings max width | class                            |
| unfold/components/flex.html       | Flex items                     | class, col                       |
| unfold/components/navigation.html | List of navigation links       | class, items                     |
| unfold/components/progress.html   | Percentual progress bar        | class, value, title, description |
| unfold/components/separator.html  | Separator, horizontal rule     | class                            |
| unfold/components/text.html       | Paragraph of text              | class                            |
| unfold/components/title.html      | Basic heading element          | class                            |

## Unfold development

### Pre-commit

Before adding any source code, it is recommended to have pre-commit installed on your local computer to check for all potential issues when comitting the code.

```bash
pip install pre-commit
pre-commit install
pre-commit install --hook-type commit-msg
```

### Poetry configuration

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

**Note:** most of the custom styles located in style.css are created via `@apply some-tailwind-class;` as is not possible to manually add CSS class to element which are for example created via jQuery.

## Credits

- [TailwindCSS](https://tailwindcss.com/) - CSS framework
- [HTMX](https://htmx.org/) - AJAX communication with backend
- [Material Icons](https://fonts.google.com/icons) - Icons from Google Fonts
- [Trix](https://trix-editor.org/) - WYSIWYG editor
- [Alpine.js](https://alpinejs.dev/) - JavaScript interactions
