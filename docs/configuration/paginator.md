---
title: Paginator
order: 4
description: Learn how to optimize performance for large datasets in Django Unfold admin using the custom InfinitePaginator that avoids expensive COUNT operations.
---


# Paginator

Django Unfold provides a specialized paginator called `InfinitePaginator` designed specifically for handling large datasets efficiently. When working with tables containing millions of records, standard Django pagination can become slow due to expensive `COUNT` queries that calculate the total number of records.

## InfinitePaginator

The `InfinitePaginator` offers several advantages for large dataset management:

- Eliminates expensive `COUNT` operations on the database
- Displays simplified navigation with only "Previous" and "Next" links
- Removes the upper limit on page numbers
- Significantly improves performance for very large tables

## Implementation

To use the `InfinitePaginator` in your admin interface, simply configure your ModelAdmin class as follows:

```python
from unfold.admin import ModelAdmin
from unfold.paginator import InfinitePaginator


class YourAdmin(ModelAdmin):
    paginator = InfinitePaginator
    show_full_result_count = False
```
