---
title: Datasets
order: 20
description: Discover how to display Django admin changelists within changeform pages using Datasets. Understand key features like list display, search, sorting and pagination to show related data alongside model forms.
---

Datasets allow you to display Django admin changelists within changeform pages. This is useful when you want to show related data alongside a model's edit form. A Dataset is essentially a specialized ModelAdmin that is not registered with the standard `@admin.register` decorator and displays as a changelist table within another model's changeform page. It can optionally be shown in a tab interface.

Datasets support core changelist functionality including list display fields and links, search, sorting, and pagination. You can also customize the queryset to filter the displayed objects. However, some changelist features as `list_filters` are not supported.

When implementing a Dataset, you need to handle permissions explicitly in your queryset. Use the `get_queryset()` method to filter objects based on the current user's permissions, restrict data based on the parent object being edited, and handle the case when creating a new object (no parent exists yet).

```python
# admin.py

from unfold.admin import ModelAdmin
from unfold.datasets import BaseDataset


class SomeDatasetAdmin(ModelAdmin):
    search_fields = ["name"]
    list_display = ["name", "city", "country", "custom_field"]
    list_display_links = ["name", "city"]
    list_per_page = 20  # Default: 10
    actions = [
        "custom_action",
    ]
    # list_filter = []  # Warning: this is not supported

    def custom_action(self, request, queryset):
        # You can do something with selected queryset
        pass

    def get_queryset(self, request):
        # `extra_context` contains current changeform object
        obj_id = self.extra_context.get("object")

        # If we are on create object page display no results
        if not obj_id:
            return super().get_queryset(request).none()

        # If there is a permission requirement, make sure that
        # everything is properly handled here
        return super().get_queryset(request).filter(
            related_field__pk=obj_id
        )


class SomeDataset(BaseDataset):
    model = SomeModel
    model_admin = SomeDatasetAdmin
    tab = True # Displays this dataset as tab


class UserAdmin(ModelAdmin):
    change_form_datasets = [
        SomeDataset,
    ]
```
