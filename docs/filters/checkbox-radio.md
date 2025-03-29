---
title: Checkbox and radio filters
order: 6
description: Enhance your Django admin with checkbox and radio button filters for model fields with choices, boolean fields, and related fields, providing a more intuitive and user-friendly filtering experience.
---

# Checkbox and radio filters

Checkbox and radio filters display all options at once for easier selection, ideal for scenarios with a manageable number of filtering options. Unfold provides radio filters (single selection), checkbox filters (multiple selection), and specialized versions for different field types, making filtering more intuitive and accessible than traditional dropdowns.


## Radio or checkbox filters for fields with choices

Unfold provides specialized filters for model fields that have predefined choices. These filters enhance the user experience by displaying the choices as either radio buttons or checkboxes instead of the default dropdown.

- These filters work with any model field that contains the `choices` property (typically `CharField` with choices)
- The library supports both radio button inputs (`ChoicesRadioFilter`) and checkbox inputs (`ChoicesCheckboxFilter`)
- When using the radio button filter (`ChoicesRadioFilter`), an "All" option is automatically added at the beginning of the list, allowing users to clear their selection
- The checkbox filter (`ChoicesCheckboxFilter`) allows for selecting multiple options simultaneously

These filters are particularly useful when you have a reasonable number of choices that would benefit from being all visible at once, rather than hidden in a dropdown menu.

```python
from unfold.contrib.filters.admin import ChoicesRadioFilter, ChoicesCheckboxFilter

class SampleModelAdmin(ModelAdmin):
    list_filter = [
        ("status", ChoicesCheckboxFilter),
        ("status", ChoicesRadioFilter)
    ]
```

## Radio filter for BooleanField

For boolean fields (`django.db.models.BooleanField`), Unfold provides a specialized filter called `BooleanRadioFilter`. This filter enhances the user experience by displaying the boolean options (Yes/No) as radio inputs, making it more intuitive and visually appealing compared to the default dropdown.

The `BooleanRadioFilter` automatically includes an "All" option, allowing users to clear their selection and view all records regardless of the boolean field value. This is particularly useful when filtering through large datasets where you need to toggle between filtered and unfiltered views.

Here's how to implement the `BooleanRadioFilter` in your admin configuration:

```python
from unfold.contrib.filters.admin import BooleanRadioFilter


class SampleModelAdmin(ModelAdmin):
    list_filter = [
        ("is_active", BooleanRadioFilter)
    ]
```

## Checkbox related field filter

The `RelatedCheckboxFilter` is designed to work with foreign key relationships in your models. This filter displays related objects as a list of checkboxes, allowing users to select multiple values simultaneously. It's particularly useful when filtering by related models where you want to provide a more visual and accessible interface than a standard dropdown.

```python
from unfold.contrib.filters.admin import RelatedCheckboxFilter


class SampleModelAdmin(ModelAdmin):
    list_filter = [
        ("country", RelatedCheckboxFilter)
    ]
```


## Displaying all values in field

The `AllValuesCheckboxFilter` provides a checkbox interface that automatically displays all distinct values found in the database column for the specified field. This filter functions similarly to Django's built-in `AllValuesFieldListFilter`, but enhances the user experience by presenting all available options as checkboxes instead of a dropdown menu. This approach allows users to see all possible values at once and select multiple options simultaneously, making it particularly useful for fields with a moderate number of distinct values that users frequently need to filter by.

```python
from unfold.contrib.filters.admin import AllValuesCheckboxFilter


class SampleModelAdmin(ModelAdmin):
    list_filter = [
        ("option", AllValuesCheckboxFilter)
    ]
```

## Custom checkbox or radio filter

For custom filtering requirements, Unfold allows you to create your own checkbox or radio filters by extending the base filter classes. This gives you complete control over the filter's behavior, appearance, and the underlying query logic.

You can create custom filters by extending either the `RadioFilter` or `CheckboxFilter` base classes, depending on whether you want single or multiple selection capability.

```python
from unfold.contrib.filters.admin import RadioFilter


class CustomRadioFilter(RadioFilter):
    title = _("Custom radio filter")
    parameter_name = "query_param_in_uri"

    def lookups(self, request, model_admin):
        return [
            ["option_1", _("Option 1")],
            ["option_2", _("Option 2")],
        ]

    def queryset(self, request, queryset):
        if self.value() not in EMPTY_VALUES:
            # Here write custom query
            return queryset.filter(your_field=self.value())

        return queryset
```
