from functools import partial
from typing import Any, Optional

from django import forms
from django.contrib.admin.utils import NestedObjects, flatten_fieldsets
from django.core.exceptions import ValidationError
from django.db import router
from django.db.models import Model
from django.forms.formsets import DELETION_FIELD_NAME
from django.forms.models import modelform_defines_fields
from django.http import HttpRequest
from django.utils.text import get_text_list
from django.utils.translation import gettext_lazy as _
from unfold.admin import StackedInline, TabularInline

from .checks import NonrelatedModelAdminChecks
from .forms import NonrelatedInlineModelFormSet, nonrelated_inline_formset_factory


class NonrelatedInlineMixin:
    checks_class = NonrelatedModelAdminChecks
    formset = NonrelatedInlineModelFormSet

    def get_formset(
        self, request: HttpRequest, obj: Optional[Model] = None, **kwargs: Any
    ):
        defaults = self._get_formset_defaults(request, obj, **kwargs)

        defaults["queryset"] = (
            self.get_form_queryset(obj) if obj else self.model.objects.none()
        )

        return nonrelated_inline_formset_factory(
            self.model, save_new_instance=self.save_new_instance, **defaults
        )

    def _get_formset_defaults(
        self, request: HttpRequest, obj: Optional[Model] = None, **kwargs: Any
    ):
        """Return a BaseInlineFormSet class for use in admin add/change views."""
        if "fields" in kwargs:
            fields = kwargs.pop("fields")
        else:
            fields = flatten_fieldsets(self.get_fieldsets(request, obj))
        excluded = self.get_exclude(request, obj)
        exclude = [] if excluded is None else list(excluded)
        exclude.extend(self.get_readonly_fields(request, obj))
        if excluded is None and hasattr(self.form, "_meta") and self.form._meta.exclude:
            # Take the custom ModelForm's Meta.exclude into account only if the
            # InlineModelAdmin doesn't define its own.
            exclude.extend(self.form._meta.exclude)
        # If exclude is an empty list we use None, since that's the actual
        # default.
        exclude = exclude or None
        can_delete = self.can_delete and self.has_delete_permission(request, obj)
        defaults = {
            "form": self.form,
            "formset": self.formset,
            # "fk_name": self.fk_name,
            "fields": fields,
            "exclude": exclude,
            "formfield_callback": partial(self.formfield_for_dbfield, request=request),
            "extra": self.get_extra(request, obj, **kwargs),
            "min_num": self.get_min_num(request, obj, **kwargs),
            "max_num": self.get_max_num(request, obj, **kwargs),
            "can_delete": can_delete,
            **kwargs,
        }

        base_model_form = defaults["form"]
        can_change = self.has_change_permission(request, obj) if request else True
        can_add = self.has_add_permission(request, obj) if request else True

        class DeleteProtectedModelForm(base_model_form):
            def hand_clean_DELETE(self):
                """
                We don't validate the 'DELETE' field itself because on
                templates it's not rendered using the field information, but
                just using a generic "deletion_field" of the InlineModelAdmin.
                """
                if self.cleaned_data.get(DELETION_FIELD_NAME, False):
                    using = router.db_for_write(self._meta.model)
                    collector = NestedObjects(using=using)
                    if self.instance._state.adding:
                        return
                    collector.collect([self.instance])
                    if collector.protected:
                        objs = []
                        for p in collector.protected:
                            objs.append(
                                # Translators: Model verbose name and instance representation,
                                # suitable to be an item in a list.
                                _("%(class_name)s %(instance)s")
                                % {
                                    "class_name": p._meta.verbose_name,
                                    "instance": p,
                                }
                            )
                        params = {
                            "class_name": self._meta.model._meta.verbose_name,
                            "instance": self.instance,
                            "related_objects": get_text_list(objs, _("and")),
                        }
                        msg = _(
                            "Deleting %(class_name)s %(instance)s would require "
                            "deleting the following protected related objects: "
                            "%(related_objects)s"
                        )
                        raise ValidationError(
                            msg, code="deleting_protected", params=params
                        )

            def is_valid(self):
                result = super().is_valid()
                self.hand_clean_DELETE()
                return result

            def has_changed(self):
                # Protect against unauthorized edits.
                if not can_change and not self.instance._state.adding:
                    return False
                if not can_add and self.instance._state.adding:
                    return False
                return super().has_changed()

        defaults["form"] = DeleteProtectedModelForm

        if defaults["fields"] is None and not modelform_defines_fields(
            defaults["form"]
        ):
            defaults["fields"] = forms.ALL_FIELDS

        return defaults


class NonrelatedStackedInline(NonrelatedInlineMixin, StackedInline):
    pass


class NonrelatedTabularInline(NonrelatedInlineMixin, TabularInline):
    pass
