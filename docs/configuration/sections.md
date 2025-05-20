---
title: Sections (Expandable rows)
order: 8
description: Learn how to implement expandable rows in Django Unfold admin changelists using sections. Configure TableSection and TemplateSection to display related data and custom content with optimized database queries.
---

# Sections - expandable changelist rows

Unfold implements special functionality for handling expandable rows in changelists called sections. Once the `list_sections` attribute is configured, rows in the changelist will display an arrow button at the beginning of the row which can be used to show additional content.

[![Unfold Sections](/static/docs/configuration/unfold-sections.webp)](/static/docs/configuration/unfold-sections.webp)

The `list_sections` attribute consists of Python classes inheriting from `TableSection` or `TemplateSection` defined in `unfold.sections`. These classes are responsible for rendering the content in the expandable area.

```python
from unfold.admin import ModelAdmin
from unfold.sections import TableSection, TemplateSection

from .models import SomeModel

# Table for related records
class CustomTableSection(TableSection):
    verbose_name = _("Table title")  # Displays custom table title
    height = 300  # Force the table height. Ideal for large amount of records
    related_name = "related_name_set"  # Related model field name
    fields = ["pk", "title", "custom_field"]  # Fields from related model

    # Custom field
    def custom_field(self, instance):
        return instance.pk

# Simple template with custom content
class CardSection(TemplateSection):
    template_name = "your_app/some_template.html"


@admin.register(SomeModel)
class SomeAdmin(ModelAdmin):
    list_sections = [
        CardSection,
        CustomTableSection,
    ]
```

## Query optimisation

When it comes to classes inheriting from `TableSection`, you may find a problem with an extraordinary amount of queries executed on changelist pages. This problem has two parts:

1. `TableSection` works with related fields so another query is required to obtain data from the related table
2. The default page size for changelist is configured to 100 - which is a pretty large number of records per page

The easiest solution for this issue is to configure pagination to a smaller amount of records by setting `list_per_page = 20`. While this solution might work for you, it is not optimal.

The optimal solution is using [`prefetch_related`](https://docs.djangoproject.com/en/5.1/ref/models/querysets/#prefetch-related):

1. Install [django-debug-toolbar](https://github.com/django-commons/django-debug-toolbar) and check all SQL queries that are duplicating for each record in the changelist
2. Override `get_queryset` and use `prefetch_related` on all related rows until you don't have any duplicated SQL queries in django-debug-toolbar output

```python
from unfold.admin import ModelAdmin

from .models import SomeModel


@admin.register(SomeModel)
class SomeAdmin(ModelAdmin):
    list_per_page = 20  # Quick solution
    list_sections = [CustomTableSection]

    # Custom queryset prefetching related records
    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .prefetch_related(
                "related_field_set",
                "related_field__another_related_field",
                "related_field__another_related_field__even_more_related_field",
            )
        )
```

## Multiple related tables

Unfold supports multiple related tables in expandable rows. Specify a section class for each related field and put them into `list_sections`. For each class, you can add a `verbose_name` to display a custom title right above the table to distinguish between different related fields.

```python
from unfold.admin import ModelAdmin

from .models import SomeModel


@admin.register(SomeModel)
class SomeAdmin(ModelAdmin):
    list_sections = [
         CustomTableSection, OtherCustomTable
    ]
```
