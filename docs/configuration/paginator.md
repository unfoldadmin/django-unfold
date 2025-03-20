---
title: Paginator
order: 4
description: Learn how to optimize performance for large datasets in Django Unfold admin using the custom DumbPaginator that avoids expensive COUNT operations.
---


# Paginator

Django Unfold provides a specialized paginator called `DumbPaginator` designed specifically for handling large datasets efficiently. When working with tables containing millions of records, standard Django pagination can become slow due to expensive `COUNT` queries that calculate the total number of records.

## DumbPaginator

The `DumbPaginator` offers several advantages for large dataset management:

- Eliminates expensive `COUNT` operations on the database
- Displays simplified navigation with only "Previous" and "Next" links
- Removes the upper limit on page numbers
- Significantly improves performance for very large tables

## Implementation

To use the `DumbPaginator` in your admin interface, simply configure your ModelAdmin class as follows:

```python
from unfold.admin import ModelAdmin
from unfold.paginator import DumbPaginator


class YourAdmin(ModelAdmin):
    paginator = DumbPaginator
    show_full_result_count = False
```
