---
title: Crispy Forms
order: 4
description: Integrate Django Crispy Forms with Unfold admin interface for beautiful, DRY form layouts. Configure the unfold_crispy template pack, create custom form layouts, and enhance your admin forms with consistent styling and reduced boilerplate.
---

# Crispy Forms

Django Crispy Forms is a powerful form rendering application that enhances the way forms are displayed in Django projects. It provides a comprehensive solution for controlling form rendering behavior with a clean, DRY (Don't Repeat Yourself) approach.

Key features for creating beautiful forms in Unfold:

- **Template packs**: Support for various template packs. Unfold provides its own template pack called `unfold_crispy`
- **Form layouts**: Define form layouts programmatically with FormHelper
- **Layout objects**: Create complex form layouts using layout objects like Div, Row, Column, and Fieldset
- **Reduced boilerplate**: Eliminate repetitive HTML in templates
- **Consistent styling**: Maintain consistent form styling across your application

## Installation

1. Install django-crispy-forms using pip:

```bash
pip install django-crispy-forms

uv add django-crispy-forms

poetry add django-crispy-forms
```

2. Add `crispy_forms` to your `INSTALLED_APPS` in `settings.py`. Of course, the Unfold dependency is required in `INSTALLED_APPS` for `unfold_crispy` template pack support.

```python
INSTALLED_APPS = [
    "unfold",
    ...
    "crispy_forms",
    ...
]
```

3. Configure Crispy Forms to use the Unfold template pack. Add these settings to your `settings.py`:

```python
CRISPY_TEMPLATE_PACK = "unfold_crispy"

CRISPY_ALLOWED_TEMPLATE_PACKS = ["unfold_crispy"]
```

If you're already using a different template pack for your front-end application, you may want to skip setting `CRISPY_TEMPLATE_PACK` globally as it would override your front-end styling. Instead, you can use Crispy Forms template tags with the explicitly specified template pack parameter `"unfold_crispy"` in your admin views.

## Crispy Forms with custom Unfold admin form

To integrate Crispy Forms with Unfold admin, start by creating a custom form with all necessary field specifications and validation rules. The example below demonstrates a basic implementation using `forms.Form`, though you can also use `forms.ModelForm` for model-based forms. After defining your form, add the FormHelper from crispy_forms.helper to configure your form's layout and behavior. The `FormHelper` allows you to organize your form fields using `Layout` objects for optimal display in the Unfold admin interface.

```python
# forms.py

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout

from django import forms


class CustomForm(forms.Form):
    pass

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.layout = Layout(
            "field1", "field2"
        )
```

Once you've created your form with Crispy Forms, you'll need to integrate it with Django's view system. The recommended approach is to use Django's class-based `FormView` along with Unfold's admin mixins.

Create a view that inherits from both `UnfoldModelAdminViewMixin` and Django's `FormView`. Configure the view with appropriate permissions and templates, and set your custom form as the `form_class`. This integration allows you to maintain Unfold's admin styling and functionality while leveraging Crispy Forms' layout capabilities.

**Note:** This view must be [registered as a custom page](https://unfoldadmin.com/docs/pages/) in your admin configuration.

```python
# views.py

from django.views.generic import FormView

from unfold.views import UnfoldModelAdminViewMixin

from .forms import CustomForm

class MyClassBasedView(UnfoldModelAdminViewMixin, FormView):
    title = "Custom Title"
    form_class = CustomForm
    success_url = reverse_lazy("admin:index")
    permission_required = (
        "app_name.add_model_name",
        "app_name.change_model_name",
    )
    template_name = "app_name/some_template.html"
```

In your template, use the `crispy` template tag to render the form with Unfold's styling. The `crispy` tag automatically applies the form layout defined in your FormHelper.

For consistent styling with the Unfold admin interface, specify the `"unfold_crispy"` template pack as the second parameter to the `crispy` tag. This ensures your form elements will match Unfold's design system.

```html
{% load crispy_forms_tags %}

{% block extrahead %}
    {{ block.super }}
    <script src="{% url 'admin:jsi18n' %}"></script>
    {{ form.media }}
{% endblock %}

{% block content %}
    {% crispy form "unfold_crispy" %}
{% endblock %}
```

[![Django Crispy Form](/static/docs/configuration/django-crispy-forms.webp)](/static/docs/configuration/django-crispy-forms.webp)


To see a live example of Django Crispy Forms integration with Unfold, visit our [interactive demo site](https://demo.unfoldadmin.com/en/admin/formula/driver/crispy-form). This demo showcases a fully functional form implementation using the techniques described above, including custom layouts, widgets, and styling. You can explore the form's behavior, test its validation, and see how it seamlessly integrates with Unfold's admin interface design. The source code for this demo is also available in our [GitHub repository](https://github.com/unfoldadmin/django-unfold), making it easy to reference when building your own forms.

## Creating formsets with django-crispy-forms

[![Django Crispy Form](/static/docs/configuration/django-crispy-formset.webp)](/static/docs/configuration/django-crispy-formset.webp)

For a comprehensive demonstration of django-crispy-forms with formset functionality in Unfold, we've created a [live example](https://demo.unfoldadmin.com/en/admin/formula/driver/crispy-with-formset) that you can explore. This demo showcases how to implement dynamic formsets with proper styling and functionality, including the ability to add/remove rows dynamically while maintaining Unfold's design system. The demo is particularly useful for understanding how formsets integrate with Unfold's admin interface and how to properly configure the FormHelper for optimal formset handling.

Below you can find a complete example demonstrating formset implementation with django-crispy-forms in Unfold. This example shows how to create dynamic formsets with proper styling, form helpers, and view configuration. The code includes all necessary components for a fully functional formset that allows adding and removing rows while maintaining Unfold's design system:

```python
# forms.py

from django import forms
from unfold.layout import Submit
from crispy_forms.layout
from crispy_forms.helper import FormHelper

class YourModelFormHelper(FormHelper):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.template = "unfold_crispy/layout/table_inline_formset.html"
        self.form_id = "your-model-formset" # This is important to add for dynamic rows
        self.form_add = True
        self.attrs = {
            "novalidate": "novalidate",
        }
        self.add_input(Submit("submit", _("Another submit")))
        self.add_input(Submit("submit", _("Submit")))


class YourModelForm(forms.ModelForm):
    class Meta:
        model = YourModel
        fields = [
            "first_name",
            "last_name",
            "code",
        ]
        widgets = {
            "first_name": UnfoldAdminTextInputWidget(),
            "last_name": UnfoldAdminTextInputWidget(),
            "code": UnfoldAdminTextInputWidget(),
        }
```

```python
# views.py

from .forms import YourModelFormHelper

class CrispyFormsetView(UnfoldModelAdminViewMixin, FormView):
    title = _("Crispy form with formset")  # required: custom page header title
    success_url = reverse_lazy("admin:custom_path")
    permission_required = ("app.your_permission", )# required: tuple of permissions
    template_name = "app/formset_template.html"

    def get_form_class(self):
        return modelformset_factory(YourModel, YourModelForm, extra=1, can_delete=True)

    def form_valid(self, form):
        messages.success(self.request, _("Formset submitted successfully"))
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context.update(
            {
                "your_model_formset_helper":  YourModelFormHelper(),
            }
        )
        return context
```

```html
{% extends "admin/base.html" %}

{% load admin_urls crispy_forms_tags i18n unfold %}

{% block extrahead %}
    {{ block.super }}
    <script src="{% url 'admin:jsi18n' %}"></script>
{% endblock %}

{% block content %}
    <div class="flex flex-col gap-8">
        {% crispy form your_model_formset_helper "unfold_crispy" %}
    </div>
{% endblock %}
```
