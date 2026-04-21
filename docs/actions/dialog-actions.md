---
title: Actions with dialog
description: Enhance your Django admin with dialog actions, offering customizable confirmation pop-ups for actions.
order: 1
---

# Actions with dialog

When an action is triggered, a confirmation modal window appears before the action is processed. The user is then prompted to either confirm the action to proceed or cancel it.

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

When using a dialog action, a custom confirmation form is displayed before the action is processed. This form must be valid for the action to proceed. By default, this form is present even if no visible fields are defined.

To customize this dialog form, always inherit from `BaseDialogForm` rather than `forms.Form`. The `BaseDialogForm` provides essential features and hooks required for dialog actions to function correctly.

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

# Form before/after templates

Custom HTML templates can be rendered before or after the dialog form by specifying the `form_before_template` and `form_after_template` attributes on your form class. You can add new template variables to the context by defining the `get_before_template_context` and `get_after_template_context` methods.

For detail actions, the context methods `get_before_template_context` and `get_after_template_context` receive an `object_id` parameter, which you can use to access additional data related to the current object.

```python
from unfold.forms import BaseDialogForm


class SomeForm(BaseDialogForm):
    form_before_template = "some/form_before.html"
    form_after_template = "some/form_after.html"

    # If it is not a detail action, remove object_id parameter
    def get_before_template_context(self, request, object_id):
        return {
            "sample": "example1"
        }

    def get_after_template_context(self, request, object_id):
        return {
            "sample": sample2,
        }
```
