---
title: Action with form example
description: Actions containing custom form example.
order: 7
---

# Action with form example

Below is an example of an action that will display a form after clicking on the action button on the detail object page.

```python
# admin.py

from django import forms
from django.contrib.auth.models import User
from django.http import HttpRequest
from django.shortcuts import render
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _

from unfold.admin import ModelAdmin
from unfold.decorators import action
from unfold.widgets import UnfoldAdminTextInputWidget, UnfoldAdminSplitDateTimeWidget


class SomeForm(forms.Form):
    # It is important to set a widget coming from Unfold
    date_start = forms.SplitDateTimeField(label=_("Start"), widget=UnfoldAdminSplitDateTimeWidget)
    date_end = forms.SplitDateTimeField(label=_("End"), widget=UnfoldAdminSplitDateTimeWidget)
    note = forms.CharField(label=_("Note"), widget=UnfoldAdminTextInputWidget)

    # Loads date widget required JS files
    class Media:
        js = [
            "admin/js/vendor/jquery/jquery.js",
            "admin/js/jquery.init.js",
            "admin/js/calendar.js",
            "admin/js/admin/DateTimeShortcuts.js",
            "admin/js/core.js",
        ]


@register(User)
class UserAdmin(ModelAdmin):
    actions_detail = ["change_detail_action"]

    @action(description=_("Change detail action"), url_path="change-detail-action")
    def change_detail_action(self, request: HttpRequest, object_id: int) -> str:
        # Check if object already exists, otherwise returs 404
        obj = get_object_or_404(User, pk=object_id)
        form = SomeForm(request.POST or None)

        if request.method == "POST" and form.is_valid():
            # Process form data
            # form.cleaned_data["note"]
            # form.cleaned_data["date_from"]
            # form.cleaned_data["date_to"]

            messages.success(request, _("Change detail action has been successful."))

            return redirect(
                reverse_lazy("admin:app_model_change", args=[object_id])
            )

        return render(
            request,
            "some/action.html",
            {
                "form": form,
                "object": obj,
                "title": _("Change detail action for {}").format(obj),
                **self.admin_site.each_context(request),
            },
        )
```

Template displaying the form. Please note that breadcrumbs are empty in this case but if you want, you can configure your own breadcrumbs path.

```html
{% extends "admin/base_site.html" %}

{% load i18n unfold %}

{% block breadcrumbs %}{% endblock %}

{% block extrahead %}
    {{ block.super }}
    <script src="{% url 'admin:jsi18n' %}"></script>
    {{ form.media }}
{% endblock %}

{% block content %}
    <form action="" method="post" novalidate>
        <div class="aligned border border-base-200 mb-8 rounded pt-3 px-3 shadow-sm dark:border-base-800">
            {% csrf_token %}

            {% for field in form %}
                {% include "unfold/helpers/field.html" with field=field %}
            {% endfor %}
        </div>

        <div class="flex justify-end">
            {% component "unfold/components/button.html" with submit=1 %}
                {% trans "Submit form" %}
            {% endcomponent %}
        </div>
    </form>
{% endblock %}
```
