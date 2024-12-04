---
title: Nonrelated inlines
order: 2
description: Nonrelated inlines for changeform.
---

# Nonrelated inlines

To display inlines which are not related (no foreign key pointing at the main model) to the model instance in changeform, you can use nonrelated inlines which are included in `unfold.contrib.inlines` module. Make sure this module is included in `INSTALLED_APPS` in settings.py.

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
