---
title: Autocomplete fields
order: 0
description: Guide to adding efficient, AJAX-powered autocomplete fields to Django admin with Unfold.
---

# Autocomplete fields

To add autocomplete functionality to `ModelChoiceField` and `ModelMultipleChoiceField`, use `UnfoldAdminAutocompleteModelChoiceField` and `UnfoldAdminMultipleAutocompleteModelChoiceField`.

**Steps to create autocomplete fields**

- Start by creating a custom view that subclasses `BaseAutocompleteView` and returns a JSON response containing the available select options. Be sure to perform all necessary permission checks within this view to control user access to the data.
- Next, register each custom view as a URL in your `ModelAdmin` class using the `custom_urls` attribute.
- Finally, in your custom form fields, set the `url_path` to the URL pattern name that points to your custom autocomplete view.

```python
from django import forms
from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from unfold.admin import ModelAdmin
from unfold.views import BaseAutocompleteView
from unfold.fields import (
    UnfoldAdminAutocompleteModelChoiceField,
    UnfoldAdminMultipleAutocompleteModelChoiceField,
)

from .models import MyModel

# Custom ListView returning JSON with available select options
class MyAutocompleteView(BaseAutocompleteView):
    model = MyModel

    def dispatch(self, request, *args, **kwargs):
        # Permissions checks here
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        # Search query is available in the request.GET object under the key "term"
        term = self.request.GET.get("term")

        # Additional filters and permissions checks here
        qs = super().get_queryset()

        # No search provided, return all results
        if term == "":
            return qs

        # Search query provided, filter results
        return qs.filter(my_field__icontains=term)


@admin.register(MyModel)
class MyModelAdmin(ModelAdmin):
    # Register custom ListView above
    custom_urls = (
        (
            "autocomplete-url-path",
            "custom_autocomplete_path_name",
            MyAutocompleteView.as_view()
        ),
    )

class MyForm(forms.Form):
    one_object = UnfoldAdminAutocompleteModelChoiceField(
        label=_("Object - Single value"),
        # Important for validation. Make sure it offers same results as the custom view
        queryset=MyModel.objects.all(),
        # Map autocomplete results to the custom view
        url_path="admin:custom_autocomplete_path_name",
    )
    multiple_objects = UnfoldAdminMultipleAutocompleteModelChoiceField(
        label=_("Objects - Multiple values"),
        queryset=MyModel.objects.all(),
        url_path="admin:custon_autocomplete_path_name",
    )
```

## SQL query optimisation

When using `UnfoldAdminAutocompleteModelChoiceField`, the `ModelChoiceField` is initialized with the full queryset on page load, which generates a complete list of choices. This can be problematic if your database table contains a large number of records. To address this, you can override the queryset with an empty queryset during `GET` requests. For `POST` requests, you should update the queryset to include only the selected choices. This approach optimizes performance by loading only the necessary data.

```python
class MyAutocompleteView(BaseAutocompleteView):
    one_object = UnfoldAdminAutocompleteModelChoiceField(
        label=_("Object - Single value"),
        queryset=MyModel.objects.all(),
        url_path="admin:custom_autocomplete_path_name",
    )

    def __init__(self, request, *args, **kwargs):
        # The request argument needs to be manually passed. If you are using
        # `FormView` just use `get_form_kwargs` to pass the request argument.

        if request.method == "GET":
            if "initial" in kwargs:
                # Initial values are present
                self.queryset = MyModel.objects.filter(pk__in=kwargs["initial"]
            else:

                self.queryset = MyModel.objects.none()
        elif request.method == "POST":
            self.queryset = MyModel.objects.filter(pk__in=request.POST.getlist("objects"))

        super().__init__(request, *args, **kwargs)

```
