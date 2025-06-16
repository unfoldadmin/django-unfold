---
title: Paginated inlines
order: 4
description: Implement paginated inlines in Django Unfold to efficiently manage large datasets by breaking down inline records into manageable pages, with customizable per-page settings and support for multiple paginated inlines.
---

Pagination on inlines can be enabled by providing the `per_page` property in the inline class. This feature is particularly useful when dealing with models that have a large number of related objects, as it helps improve page load times and provides a better user experience by breaking down the data into manageable chunks. The `per_page` property accepts an integer value that determines how many inline records will be displayed on each page.

[![Paginated inlines](/static/docs/inlines/paginated-inlines.webp)](/static/docs/inlines/paginated-inlines.webp)

It is possible to define multiple paginated inlines on the same page without any conflicts. This flexibility allows administrators to work with complex models that have multiple relationships, each potentially containing numerous records. Django Unfold handles the pagination state independently for each inline, ensuring that navigating through one inline's pages doesn't affect the pagination state of other inlines on the same admin page.

Each inline has its own unique query parameter in the URL to maintain its pagination state. This implementation ensures that when users navigate between pages of different inlines, the system can track and maintain the current page for each inline separately. The unique query parameters are automatically generated and managed by Django Unfold, so developers don't need to worry about potential conflicts or parameter naming conventions.

AJAX pagination is not currently supported for inlines. This means that when users click on pagination links, the entire admin page will reload to display the new set of records. While this approach may not be as seamless as AJAX-based pagination, it ensures compatibility with Django's existing admin infrastructure and maintains the reliability of the admin interface functionality.

If inline records fit on only one page, no pagination controls will be displayed to keep the interface clean and uncluttered. Django Unfold automatically detects when the total number of records is less than or equal to the specified `per_page` value and hides the pagination controls accordingly. This intelligent behavior prevents unnecessary UI elements from appearing when they serve no functional purpose.

```python
from unfold.admin import StackedInline, TabularInline, GenericStackedInline, GenericTabularInline
from unfold.contrib.inlines.admin import NonrelatedStackedInline, NonrelatedTabularInline


############################################
# Regular inlines
############################################
class SomeStackedInline(StackedInline):
    model = YourModel
    per_page = 10

class SomeTabularInline(TabularInline):
    model = YourModel
    per_page = 10

############################################
# Generic inlines
############################################
class SomeGenericStackedInline(GenericStackedInline):
    model = YourModel
    per_page = 10

class SomeGenericTabularInline(GenericTabularInline):
    model = YourModel
    per_page = 10

############################################
# Nonrelated inlines
############################################
class SomeNonrelatedStackedInline(NonrelatedStackedInline):
    model = YourModel
    per_page = 10

class SomeNonrelatedTabularInline(NonrelatedTabularInline):
    model = YourModel
    per_page = 10
```
