---
title: django-celery-beat
order: 0
description: Integration with django-celery-beat, a Django scheduler for periodic tasks. Learn how to properly integrate it with Unfold admin interface to maintain consistent styling and functionality across your admin panel.
---

# django-celery-beat

In general, django-celery-beat does not have any components that require special styling. However, there is an integration issue to be aware of. The default changelist templates in django-celery-beat are not inheriting from Unfold's `ModelAdmin` class but instead are using the default `ModelAdmin` class from `django.contrib.admin`. This inconsistency causes noticeable design discrepancies in the changelist views, breaking the uniform appearance of your admin interface. To maintain a consistent look and feel throughout your admin panel, you'll need to override these admin classes as shown in the code example below.

In the source code below, you can find a short code snippet that demonstrates how to unregister all `django-celery-beat` admin classes and register them with the proper parent `ModelAdmin` class.

```python
# admin.py
from django.contrib import admin
from unfold.admin import ModelAdmin
from unfold.widgets import UnfoldAdminSelectWidget, UnfoldAdminTextInputWidget

from django_celery_beat.models import (
    ClockedSchedule,
    CrontabSchedule,
    IntervalSchedule,
    PeriodicTask,
    SolarSchedule,
)
from django_celery_beat.admin import ClockedScheduleAdmin as BaseClockedScheduleAdmin
from django_celery_beat.admin import CrontabScheduleAdmin as BaseCrontabScheduleAdmin
from django_celery_beat.admin import PeriodicTaskAdmin as BasePeriodicTaskAdmin
from django_celery_beat.admin import PeriodicTaskForm, TaskSelectWidget

admin.site.unregister(PeriodicTask)
admin.site.unregister(IntervalSchedule)
admin.site.unregister(CrontabSchedule)
admin.site.unregister(SolarSchedule)
admin.site.unregister(ClockedSchedule)


class UnfoldTaskSelectWidget(UnfoldAdminSelectWidget, TaskSelectWidget):
    pass


class UnfoldPeriodicTaskForm(PeriodicTaskForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["task"].widget = UnfoldAdminTextInputWidget()
        self.fields["regtask"].widget = UnfoldTaskSelectWidget()


@admin.register(PeriodicTask)
class PeriodicTaskAdmin(BasePeriodicTaskAdmin, ModelAdmin):
    form = UnfoldPeriodicTaskForm


@admin.register(IntervalSchedule)
class IntervalScheduleAdmin(ModelAdmin):
    pass


@admin.register(CrontabSchedule)
class CrontabScheduleAdmin(BaseCrontabScheduleAdmin, ModelAdmin):
    pass


@admin.register(SolarSchedule)
class SolarScheduleAdmin(ModelAdmin):
    pass

@admin.register(ClockedSchedule)
class ClockedScheduleAdmin(BaseClockedScheduleAdmin, ModelAdmin):
    pass
```

For comprehensive information about installation, configuration, and usage of django-celery-beat, please refer to the [official documentation](https://django-celery-beat.readthedocs.io/en/latest/). The documentation covers everything from basic setup to advanced scheduling patterns and task management.

[![Django Celery Beat](/static/docs/integrations/django-celery-beat.webp)](/static/docs/integrations/django-celery-beat.webp)

A live demo of the [django-celery-beat integration with Unfold](https://demo.unfoldadmin.com/en/admin/django_celery_beat/periodictask/) is available. This demo showcases how Unfold seamlessly integrates with django-celery-beat's task scheduling interface, providing an enhanced user experience for managing periodic tasks and schedules.
