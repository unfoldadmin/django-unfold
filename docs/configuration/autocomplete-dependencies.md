---
title: Autocomplete dependencies
order: 3
description: Limit Django admin autocomplete choices based on another field, such as Country → State → City.
---

# Autocomplete dependencies

`autocomplete_dependencies` extends Django Admin's native `autocomplete_fields`. When a parent field changes, child autocomplete results are limited to related objects. Use it for chains such as Country → State → City.

Requirements:

- Child fields must also be listed in `autocomplete_fields`.
- Child and parent fields must be `ForeignKey`s.
- The related model's `ModelAdmin` must define `search_fields`, as required by Django autocomplete.
- `lookup` must be a direct ForeignKey field name on the autocomplete target model. Relation traversal with `__` is not supported.

The same mapping works on `ModelAdmin` and Unfold inlines. Dependencies resolve on the same form, or on the same inline row.

Changing a parent clears dependent descendants. Existing saved values stay visible until the parent changes.

## Shorthand syntax

When the parent form field name matches the ForeignKey on the related model, map the child field to that name:

```python
# admin.py

from django.contrib import admin
from unfold.admin import ModelAdmin

from .models import City, Country, Location, State


@admin.register(Country)
class CountryAdmin(ModelAdmin):
    search_fields = ["name"]


@admin.register(State)
class StateAdmin(ModelAdmin):
    search_fields = ["name"]


@admin.register(City)
class CityAdmin(ModelAdmin):
    search_fields = ["name"]


@admin.register(Location)
class LocationAdmin(ModelAdmin):
    autocomplete_fields = ["state", "city"]
    autocomplete_dependencies = {
        "state": "country",
        "city": "state",
    }
```

Here `"state": "country"` means the `state` autocomplete depends on the `country` form field, and `State.country` is the lookup used to filter results.

## Explicit syntax

When the form field name differs from the ForeignKey on the target model, set `depends_on` and `lookup` separately:

- `depends_on` is the field on the current admin form.
- `lookup` is the ForeignKey on the autocomplete target model.

```python
# admin.py

from django.contrib import admin
from unfold.admin import ModelAdmin, TabularInline

from .models import Address, PersonLocation


@admin.register(Address)
class AddressAdmin(ModelAdmin):
    autocomplete_fields = ["selected_state", "selected_city"]
    autocomplete_dependencies = {
        "selected_state": {
            "depends_on": "selected_country",
            "lookup": "country",
        },
        "selected_city": {
            "depends_on": "selected_state",
            "lookup": "state",
        },
    }


class PersonLocationInline(TabularInline):
    model = PersonLocation
    extra = 1
    autocomplete_fields = ["selected_state", "selected_city"]
    autocomplete_dependencies = {
        "selected_state": {
            "depends_on": "selected_country",
            "lookup": "country",
        },
        "selected_city": {
            "depends_on": "selected_state",
            "lookup": "state",
        },
    }
```

`selected_city` depends on the `selected_state` form field. Results are filtered with `City.state`, not a field named `selected_state`.
