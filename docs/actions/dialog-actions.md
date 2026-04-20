---
title: Actions with dialog
description:
order: 1
---

# Actions with dialog


## Simple dialog

```python
class SomeModelAdmin(ModelAdmin):
    actions_list = [
        "changelist_dialog_action",
    ]
    actions_row = [
        "row_dialog_action",
    ]

    @action(
        description="Changelist dialog action",
        dialog={
            "title": "Changelist dialog action",
            "description": "This is a dialog action",
            "submit_text": "My custom submit button text",  # Default: "Submit"
        },
    )
    def changelist_dialog_action(self, request, form):
        messages.success(request, "Dialog form has been submitted successfully.")

        # Return HttpResponse with HX-Redirect which will be used by
        # HTMX to redirect to success page.
        return HttpResponse(
            headers={
                "HX-Redirect": reverse_lazy("admin:mypapp_somemodel_changelist"),
            }
        )

    @action(
        description="Changelist dialog action",
        dialog={
            "title": "Changelist dialog action",
            "description": "This is a dialog action",
        },
    )
    def row_dialog_action(self, request, form, object_id):
        pass  # Do the same as in the previous example
```

## Custom confirmation form

```python
from unfold.admin import ModelAdmin
from unfold.decorators import action
from unfold.forms import BaseDialogForm


# IMPORTANT: inherit from BaseDialogForm
class SomeForm(BaseDialogForm):
    variable_from_custom_form = forms.CharField(label="Variable from custom form")

    def __init__(self, request, *args, **kwargs):
        # "request" is automatically available as parameter
        super().__init__(request, *args, **kwargs)

    def clean_variable_from_custom_form(self):
        value = self.cleaned_data["variable_from_custom_form"]

        # Write your own validation logic here
        if not value:
            raise forms.ValidationError("This field is required.")

        # You can access the request object like this
        self.request

        return value


class SomeModelAdmin(ModelAdmin):
    actions_list = [
        "changelist_dialog_action",
    ]

    @action(
        description="Changelist dialog action",
        dialog={
            "title": "Changelist dialog action",
            "description": "This is a dialog action",
            "form_class": SomeForm,
        },
    )
    def changelist_dialog_action(self, request, form):
        messages.success(request, "Dialog form has been submitted successfully.")

        # Validated form data is available as function/method parameter
        data = form.cleaned_data
        do_something(data["variable_from_custom_form"])

        # Return HttpResponse with HX-Redirect which will be used by
        # HTMX to redirect to success page.
        return HttpResponse(
            headers={
                "HX-Redirect": reverse_lazy("admin:mypapp_somemodel_changelist"),
            }
        )
```
