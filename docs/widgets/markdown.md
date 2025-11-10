---
title: MarkdownWidget
order: 3
description: Integrate Django Unfold's MarkdownWidget, a powerful Markdown editor powered by EasyMDE, to enhance text fields in your Django admin interface with Markdown formatting capabilities and live preview.
---

# Unfold widget MarkdownWidget

To enhance your Django admin interface with Markdown editing capabilities, you'll need to integrate the MarkdownWidget component. This requires adding `unfold.contrib.forms` to your project's `INSTALLED_APPS` setting as a mandatory dependency. The MarkdownWidget leverages the powerful [EasyMDE editor](https://github.com/Ionaru/easy-markdown-editor), an elegant open-source Markdown editor that provides a clean and intuitive interface for content creation. EasyMDE offers essential Markdown formatting options, live preview, side-by-side editing mode, and full support for tables, making it an excellent choice for managing Markdown content in your Django admin interface.

[![Markdown widget](/static/docs/widgets/markdown.webp)](/static/docs/widgets/markdown.webp)

```python
# settings.py

INSTALLED_APPS = [
    "unfold",
    "unfold.contrib.forms",
]
```

## Basic usage

The following example demonstrates how to enhance all `TextField` fields in your admin interface by replacing them with the `MarkdownWidget`. This is achieved by using the `formfield_overrides` setting in your ModelAdmin class, which automatically applies the Markdown editor to every text field. The widget stores pure Markdown text in the database, which can be later rendered to HTML using Python Markdown libraries like `markdown` or `mistune`.

```python
# admin.py

from django.db import models
from unfold.admin import ModelAdmin
from unfold.contrib.forms.widgets import MarkdownWidget


@admin.register(MyModel)
class CustomAdminClass(ModelAdmin):
    formfield_overrides = {
        models.TextField: {
            "widget": MarkdownWidget,
        }
    }
```

## Field-specific usage

If you want to use the Markdown editor only for specific fields, you can use a custom form:

```python
# admin.py

from django import forms
from unfold.admin import ModelAdmin
from unfold.contrib.forms.widgets import MarkdownWidget


class MyModelForm(forms.ModelForm):
    content = forms.CharField(widget=MarkdownWidget())
    description = forms.CharField(widget=MarkdownWidget())
    
    class Meta:
        model = MyModel
        fields = '__all__'


@admin.register(MyModel)
class MyModelAdmin(ModelAdmin):
    form = MyModelForm
```

## Features

The MarkdownWidget includes the following features:

- **Markdown syntax**: Full Markdown support with standard syntax
- **Toolbar**: Rich toolbar with formatting buttons (bold, italic, strikethrough, headings, lists, links, images, tables, horizontal rules)
- **Live preview**: Side-by-side preview mode to see rendered Markdown in real-time
- **Dark theme**: Automatic dark/light theme switching based on Unfold's theme
- **Tables**: Built-in support for creating and editing Markdown tables
- **Horizontal rules**: Easy insertion of horizontal dividers
- **Image insertion**: Support for inserting images via URL
- **Fullscreen mode**: Distraction-free fullscreen editing
- **Material Icons**: Integrated Material Symbols icons matching Unfold's design
- **Responsive**: Mobile-friendly interface

## Storage and rendering

The MarkdownWidget stores pure Markdown text in your database TextField. To render this Markdown as HTML in your templates or frontend, you can use Python Markdown libraries:

### Using Python-Markdown

```python
# Install: pip install markdown

from markdown import markdown

# In your view or template context
html_content = markdown(your_model.content)
```

### Using Mistune

```python
# Install: pip install mistune

import mistune

# In your view or template context
html_content = mistune.html(your_model.content)
```

### In Django templates

```django
{% load markdown_extras %}

{{ object.content|markdown }}
```

You'll need to create a custom template filter:

```python
# yourapp/templatetags/markdown_extras.py

from django import template
from markdown import markdown as md

register = template.Library()

@register.filter(name='markdown')
def markdown_filter(text):
    return md(text, extensions=['extra', 'codehilite'])
```

## Toolbar customization

The MarkdownWidget comes with a predefined toolbar that includes all essential Markdown formatting options. The toolbar is optimized for the most common use cases and includes:

- Text formatting: Bold, Italic, Strikethrough
- Headings: H1, H2, H3
- Block elements: Quote, Code block
- Lists: Unordered and ordered lists
- Links and Images
- Tables and horizontal rules
- Preview modes: Preview, Side-by-side, Fullscreen
- Help guide

## Theme integration

The MarkdownWidget is fully integrated with Unfold's theme system:

- **Light theme**: Uses Unfold's light color palette with proper contrast
- **Dark theme**: Automatically switches to dark mode colors when Unfold's dark theme is active
- **CSS variables**: All colors use Unfold's CSS custom properties for consistency
- **Tailwind classes**: Styled using Tailwind CSS utilities matching Unfold's design system

## No autosave

Unlike some other Markdown editors, the MarkdownWidget does not include automatic saving to localStorage. This is intentional to prevent conflicts with Django's form handling and to give you full control over the save behavior. Content is only saved when you submit the form through Django's standard form submission.

## Browser compatibility

The MarkdownWidget works in all modern browsers:

- Chrome/Edge (latest)
- Firefox (latest)
- Safari (latest)
- Mobile browsers (iOS Safari, Chrome Mobile)

## Differences from WysiwygWidget

| Feature | MarkdownWidget | WysiwygWidget |
|---------|---------------|---------------|
| Format | Markdown syntax | HTML |
| Storage | Plain text Markdown | HTML |
| Editor | EasyMDE | Trix |
| Tables | ✅ Built-in | ❌ Not supported |
| Horizontal rules | ✅ Built-in | ❌ Not supported |
| Preview | ✅ Side-by-side | ❌ WYSIWYG only |
| Use case | Documentation, blogs, technical content | Rich text, simple formatting |

## Example model

Here's a complete example of using the MarkdownWidget with a blog post model:

```python
# models.py

from django.db import models


class BlogPost(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField(help_text="Write your post in Markdown format")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


# admin.py

from django.db import models
from unfold.admin import ModelAdmin
from unfold.contrib.forms.widgets import MarkdownWidget

from .models import BlogPost


@admin.register(BlogPost)
class BlogPostAdmin(ModelAdmin):
    list_display = ['title', 'created_at', 'updated_at']
    formfield_overrides = {
        models.TextField: {
            "widget": MarkdownWidget,
        }
    }
```

## License

The MarkdownWidget uses EasyMDE, which is licensed under the [MIT License](https://github.com/Ionaru/easy-markdown-editor/blob/master/LICENSE).

