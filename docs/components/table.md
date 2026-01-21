---
title: Component - Table
order: 3
description: Comprehensive guide to Unfold's responsive Table component for displaying tabular data with features like striped rows, scrollable content, and mobile-friendly layouts. Includes examples of data structure, implementation in templates, and available parameters.
---

# Table component

The Table component is a versatile element for displaying tabular data in the Unfold theme. It features responsive design that adapts to different screen sizes while maintaining consistent styling with the Unfold design system. The component supports table headers and rows with a mobile-friendly layout that includes data labels for smaller screens. Users can enable optional features such as striped rows and scrollable content with height limitations. The table component integrates seamlessly with the Card component and handles empty states gracefully when no data is available. It also includes full dark mode support with appropriate color adjustments to maintain readability and visual harmony in both light and dark environments.

## Table component data

The table component requires a dictionary with the following structure:

- **headers**: A list of strings representing the column titles that will be displayed in the table header.
- **rows**: A list of lists, where each inner list represents a row of data. Each element in the inner list corresponds to a cell value that will be displayed in the respective column.

```python
def dashboard_callback(request):
    return {
        "table_data": {
            "collapsible": True,
            "headers": ["col 1", "col 2"],
            "rows": [
                ["a", "b"],
                ["c", "d"],
            ]
        }
    }
```

## Table component in HTML template

```html
{% load unfold %}

{% component "unfold/components/card.html" with title="Card title" %}
    {% component "unfold/components/table.html" with table=table_data card_included=1 striped=1 %}{% endcomponent %}
{% endcomponent %}
```

## Nested tables data structure

```python
data = {
    "headers": ["col1", "col 2"],
    "rows": [
        # Classic row
        ["a", "b"],
        # Row with nested table
        {
            "cols": ["c", "d"], # Cols in row
            "table": {
                "headers": ["col2", "col3"],
                "rows": [
                    ["g", "h"]
                ]
            }
        }
    ]
}
```

## Table component parameters

| Parameter                         | Description                                |
| --------------------------------- | ------------------------------------------ |
| table                             | Table data: headers, rows                  |
| title                             | Custom table title                         |
| striped                           | Stripes for odd rows                       |
| card_included                     | Special styling when in "card" component   |
| height                            | Max height, displays scroolbar             |
