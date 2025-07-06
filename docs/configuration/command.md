---
title: Command
order: 3
description: A guide to using the command in Django Unfold admin interface for quick navigation and search functionality. Configure model search capabilities and customize search fields for enhanced admin experience.
---

The command can be activated by pressing `cmd + K` on Mac or `ctrl + K` on Windows/Linux. By default, the search functionality is limited to application and model names only.

To enable searching through model data, you need to set `UNFOLD["COMMAND"]["search_models"] = True` in your configuration. However, be aware that searching through all models can be a database-intensive operation since it queries across all model data.

For a model to be searchable, you must define the `search_fields` attribute on its admin class. This attribute specifies which fields will be used when searching through the model's data.

```python
UNFOLD = {
    # ...
    "COMMAND": {
        "search_models": True,  # Default: False
    },
    # ...
}
```
