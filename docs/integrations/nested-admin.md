---
title: Nested parent-child admin
order: 9
description:
---

# Nested parent-child admin

`unfold.contrib.nested_admin` adds optional parent-child admin routing for cases where a child model should be managed from a nested URL under its parent object.

This feature is separate from Unfold's nested inline support:

- nested inlines edit related objects inside a parent change form
- nested admin routes expose a dedicated child changelist, add view, change view, history view, and delete view under the parent admin

## Installation

Add the contrib app to `INSTALLED_APPS`:

```python
INSTALLED_APPS = [
    "unfold",
    "unfold.contrib.nested_admin",
    "django.contrib.admin",
    # ...
]
```

## Usage

```python
from django.contrib import admin

from example.models import Project, Task
from unfold.admin import ModelAdmin
from unfold.contrib.nested_admin.admin import (
    NestedChildAdminMixin,
    NestedParentAdminMixin,
)


@admin.register(Project)
class ProjectAdmin(NestedParentAdminMixin, ModelAdmin):
    nested_child_model = Task
    nested_child_fk_name = "project"


@admin.register(Task)
class TaskAdmin(NestedChildAdminMixin, ModelAdmin):
    nested_parent_fk = "project"
```

This adds nested URLs like:

- `/admin/example/project/<parent_id>/task/`
- `/admin/example/project/<parent_id>/task/add/`
- `/admin/example/project/<parent_id>/task/<object_id>/change/`
- `/admin/example/project/<parent_id>/task/<object_id>/history/`
- `/admin/example/project/<parent_id>/task/<object_id>/delete/`

## Notes

- One child model is supported per parent admin.
- The child admin must be registered on the same `AdminSite`.
- Nested child history, delete, and custom detail actions stay inside the nested surface.
- Nested child action proxy URLs are available at:
  - `/admin/<app>/<parent>/<parent_id>/<segment>/<object_id>/actions/<action_path>`
