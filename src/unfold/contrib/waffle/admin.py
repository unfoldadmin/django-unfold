from typing import Any

from django.db import models
from django.db.models.fields import Field
from django.forms.fields import Field as FormField
from django.http import HttpRequest
from waffle.admin import FlagAdmin as BaseFlagAdmin

from unfold.admin import ModelAdmin
from unfold.widgets import UnfoldAdminExpandableTextareaWidget


class FlagAdmin(BaseFlagAdmin, ModelAdmin):
    autocomplete_fields = ("groups", "users")
    raw_id_fields = ()
    formfield_overrides = {
        models.TextField: {
            "widget": UnfoldAdminExpandableTextareaWidget(),
        },
    }

    def formfield_for_dbfield(
        self, db_field: Field, request: HttpRequest, **kwargs: Any
    ) -> FormField | None:
        # Skip the implementation of the method in the waffle
        return super(ModelAdmin, self).formfield_for_dbfield(
            db_field, request, **kwargs
        )
