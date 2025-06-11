---
title: Nonrelated inlines
order: 2
description: Implement nonrelated inlines in Django Unfold to display and manage data without direct model relationships in the admin interface, using NonrelatedTabularInline and NonrelatedStackedInline.
---

# Nonrelated inlines

Django Unfold provides a powerful feature for displaying inlines that don't have a direct relationship (no foreign key) with the main model in the changeform view. These nonrelated inlines are available through the `unfold.contrib.inlines` module. To use this functionality, ensure that you have included the module in your project's `INSTALLED_APPS` configuration within settings.py. This feature allows you to display and manage related data even when there isn't a traditional database relationship between the models.

[![Nonrelated inlines](/static/docs/inlines/nonrelated-inlines.webp)](/static/docs/inlines/nonrelated-inlines.webp)

```python
from django.contrib.auth.models import User
from unfold.admin import ModelAdmin
from unfold.contrib.inlines.admin import NonrelatedTabularInline
from .models import OtherModel

class OtherNonrelatedInline(NonrelatedTabularInline):  # NonrelatedStackedInline is available as well
    model = OtherModel
    fields = ["field1", "field2"]  # Ignore property to display all fields

    def get_form_queryset(self, obj):
        """
        Gets all nonrelated objects needed for inlines. Method must be implemented.
        """
        return self.model.objects.all()

    def save_new_instance(self, parent, instance):
        """
        Extra save method which can for example update inline instances based on current
        main model object. Method must be implemented.
        """
        pass


@admin.register(User)
class UserAdmin(ModelAdmin):
    inlines = [OtherNonrelatedInline]
```

**NOTE:** credit for this functionality goes to [django-nonrelated-inlines](https://github.com/bhomnick/django-nonrelated-inlines)
