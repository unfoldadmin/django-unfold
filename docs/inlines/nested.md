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
    inlines = [AnotherInline]
```

There is no limit on how deep the hierarchy goes. Each inline renders the inlines it declares, so the nesting ends where the declarations end.

## Self-referencing inlines

An inline which appears somewhere below itself, a category containing categories being the typical case, describes a hierarchy without an end. Every level also renders a template used for adding new records, so there is always one more level to render. Such a hierarchy needs `nested_inlines_max_depth` on the `ModelAdmin` to define how many levels of nested inlines are rendered.

```python
from unfold.admin import ModelAdmin, TabularInline


class SubcategoryInline(TabularInline):
    model = Category
    fk_name = "parent"


SubcategoryInline.inlines = [SubcategoryInline]


class CategoryAdmin(ModelAdmin):
    inlines = [SubcategoryInline]
    nested_inlines_max_depth = 4
```

Without `nested_inlines_max_depth`, a self-referencing chain declared through `inlines` is reported by a system check (`unfold.E001`) when the application starts. A chain which only appears at request time, through `get_inlines()`, raises `ImproperlyConfigured` when the changeform is opened.

## Nesting through many-to-many relationships

An inline can render the intermediary model of a many-to-many relationship, and inlines nested below it are attached to the model on the other side of that relationship.

```python
from unfold.admin import ModelAdmin, StackedInline, TabularInline


class TagNoteInline(TabularInline):
    model = TagNote  # has a foreign key to Tag


class UserTagInline(StackedInline):
    model = User.tags.through
    inlines = [TagNoteInline]


class UserAdmin(ModelAdmin):
    inlines = [UserTagInline]
```

The relationship to traverse is detected automatically. When more than one relationship would fit, name the field explicitly on the nested inline with `nested_parent_field`.

```python
class TagNoteInline(TabularInline):
    model = TagNote
    nested_parent_field = "tag"
```

## Collapsing the deeper levels

A hierarchy of several levels shows a lot at once. Adding the `collapse` class to a nested inline renders it closed, so each level is opened only when it is needed.

```python
class InvoiceItemPartInline(StackedInline):
    model = InvoiceItemPart
    classes = ["collapse"]
```

A formset which contains errors is always rendered expanded, so nothing that needs attention ends up hidden.

## Performance

Every form of a formset renders the whole hierarchy below it, including the forms `extra` adds and the template form used for adding records. The amount of rendered HTML therefore multiplies with each level, and `extra` is the largest factor in that product because it applies at every level.

Setting `extra = 0` on the inlines of a deep hierarchy is the single most effective thing to do, records are then added through the template form instead. `per_page` on the inlines rendering many records, and `nested_inlines_max_depth` for a self-referencing hierarchy, keep the remaining size in check.
