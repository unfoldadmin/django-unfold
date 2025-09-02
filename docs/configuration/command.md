---
title: Command
order: 3
description: A guide to using the command in Django Unfold admin interface for quick navigation and search functionality. Configure model search capabilities and customize search fields for enhanced admin experience.
---

# Command

The command can be activated by pressing `cmd + K` on Mac or `ctrl + K` on Windows/Linux. By default, the search functionality is limited to application and model names only.

[![Command results](/static/docs/command/command-results.webp)](/static/docs/command/command-results.webp)

To enable searching through model data, you need to set `UNFOLD["COMMAND"]["search_models"] = True` in your configuration. However, be aware that searching through all models can be a database-intensive operation since it queries across all model data.

For a model to be searchable, you must define the `search_fields` attribute on its admin class. This attribute specifies which fields will be used when searching through the model's data.

```python
UNFOLD = {
    # ...
    "COMMAND": {
        "search_models": True,  # Default: False
        "search_callback": "utils.search_callback",
        "show_history": True,  # Enable history
    },
    # ...
}
```

Command results use infinite scrolling with a default page size of 100 results. When the last item becomes visible in the viewport, a new page of results is automatically loaded and appended to the existing list, allowing continuous browsing through search results.

## Custom search callback

The search callback feature provides a way to define a custom hook that can inject additional content into search results. This is particularly useful when you want to search for results from external sources or services beyond the Django admin interface.

When implementing a search callback, keep in mind that you'll need to handle permissions manually to ensure users only see results they have access to.

```python
# utils.py
from unfold.dataclasses import SearchResult


def search_callback(request, search_term):
    # Do custom search, e.g. third party service

    return [
        SearchResult(
            "title": "Some title",
            "description": "Extra content",
            "link": "https://example.com",
            "icon": "database",
        )
    ]
```

## Command history

The command history feature can be enabled by setting `show_history` to `True` in the configuration. By default, this setting is disabled (`False`). When enabled, users can view their previous search queries.

[![Command history](/static/docs/command/command-history.webp)](/static/docs/command/command-history.webp)

Search history is stored in the browser's `localStorage`. Before enabling this feature, carefully consider any potential security implications of storing search queries client-side, as sensitive information could be exposed if the `localStorage` is compromised.
