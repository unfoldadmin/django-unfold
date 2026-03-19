---
title: Nested inlines
order: 5
description:
---

# Nested inlines

Nested inlines provide a way to display hierarchical relationships between related objects within the inlines sections of the changeform page. This feature allows you to visualize and manage parent-child relationships directly in the Django admin interface.

To implement nested inlines, simply use the `inlines` property which takes a list of inline classes as its value. You have the flexibility to use either the standard `TabularInline` or `StackedInline` classes without any additional configuration requirements.

Within the nested hierarchy, you can freely combine both `StackedInline` and `TabularInline` components to create a mixed layout structure.

```python
from unfold.admin import ModelAdmin, TabularInline, StackedInline


class ProjectAdmin(ModelAdmin):
    inlines = [TaskInline]


class TaskInline(TabularInline):
    inlines = [SubTaskInline]


class SubTaskInline(TabularInline):
    inlines = [AnotherInline] # This is not going to work
```


## Limitations

- Nested inlines support only one level of nesting. You cannot create more than two levels of nested inlines.
- Nesting through many-to-many (M2M) relationships is not supported.
