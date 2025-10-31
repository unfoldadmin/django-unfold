from typing import Any

from django.contrib.admin import options
from django.contrib.admin.helpers import InlineAdminFormSet
from django.contrib.admin.options import InlineModelAdmin
from django.db.models import Model
from django.forms import BaseInlineFormSet, Media, ModelForm
from django.http import HttpRequest, HttpResponse
from django.utils.translation import gettext_lazy as _


def nested_all_valid(formsets: list[BaseInlineFormSet]) -> bool:
    validation_result = all(formset.is_valid() for formset in formsets)

    for formset in formsets:
        for form in formset:
            if not hasattr(form, "nested_formsets"):
                continue

            for nested_formset in form.nested_formsets:
                if not nested_formset.formset.is_valid():
                    return False

                if (
                    nested_formset.formset.has_changed()
                    and hasattr(form, "cleaned_data")
                    and len(form.cleaned_data) == 0
                    and form.instance.pk is None
                ):
                    form.add_error(
                        None, _("You can not create nested object without parent")
                    )
                    return False

    return validation_result


class NestedInlinesModelAdminMixin:
    # Build custom media for all nested formsets and process it
    # later in media property in ModelAdmin
    nested_formset_media = Media()

    def _create_formsets(
        self, request: HttpRequest, obj: Model | None = None, change: bool = False
    ) -> tuple[list[BaseInlineFormSet], list[InlineModelAdmin]]:
        formsets, inline_instances = super()._create_formsets(request, obj, change)

        self._build_nested_formsets(request, obj, formsets, inline_instances, change)

        return formsets, inline_instances

    def changeform_view(
        self,
        request: HttpRequest,
        object_id: str | None = None,
        form_url: str = "",
        extra_context: dict[str, Any] | None = None,
    ) -> HttpResponse:
        # Monkey patch all_valid to do nested formsets validation. Applied because
        # we don't want to completely override `BaseModelAdmin._changeform_view()`
        options.all_valid = nested_all_valid
        return super().changeform_view(request, object_id, form_url, extra_context)

    def save_formset(
        self,
        request: HttpRequest,
        form: ModelForm,
        formset: BaseInlineFormSet,
        change: bool,
    ) -> None:
        super().save_formset(request, form, formset, change)

        for form in formset.forms:
            if not hasattr(form, "nested_formsets"):
                continue

            if form in formset.deleted_forms:
                continue

            for nested_formset in form.nested_formsets:
                self.save_formset(request, form, nested_formset.formset, change)

    def _build_nested_formsets(
        self,
        request: HttpRequest,
        obj: Model,
        formsets: list[BaseInlineFormSet],
        inline_instances: list[InlineModelAdmin],
        change: bool,
    ) -> None:
        from unfold.admin import StackedInline, TabularInline

        for formset, inline in zip(formsets, inline_instances):
            # Existing forms in formset
            for form in formset.forms:
                nested_formsets = []

                if not hasattr(inline, "inlines"):
                    continue

                for inline_class in inline.inlines:
                    inline_formset = self._get_nested_formset(
                        request, obj, form, inline, inline_class, change
                    )

                    if not inline_formset:
                        continue

                    if issubclass(inline_class, StackedInline):
                        inline_formset.inline_type = "stacked"
                    elif issubclass(inline_class, TabularInline):
                        inline_formset.inline_type = "tabular"

                    nested_formsets.append(inline_formset)
                    self.nested_formset_media += inline_formset.media

                form.nested_formsets = nested_formsets

            # Add nested forms to template form in formsets
            if (
                hasattr(formset, "empty_form")
                and hasattr(inline, "inlines")
                and inline.has_add_permission(request, obj)
            ):
                formset.form.nested_formsets = []

                for inline_class in inline.inlines:
                    inline_formset = self._get_nested_formset(
                        request, obj, formset.empty_form, inline, inline_class, change
                    )

                    if not inline_formset:
                        continue

                    if issubclass(inline_class, StackedInline):
                        inline_formset.inline_type = "stacked"
                    elif issubclass(inline_class, TabularInline):
                        inline_formset.inline_type = "tabular"

                    formset.form.nested_formsets.append(inline_formset)
                    self.nested_formset_media += inline_formset.media

    def _get_nested_formset(
        self,
        request: HttpRequest,
        obj: Model,
        form: ModelForm,
        parent_inline: InlineModelAdmin,
        inline_class: type[InlineModelAdmin],
        change: bool,
    ) -> InlineAdminFormSet | None:
        inline = inline_class(parent_inline.model, self.admin_site)

        if not self._check_nested_inline_permissions(request, inline, obj):
            return None

        if not inline.has_add_permission(request, obj):
            inline.max_num = 0

        InlineFormSet = inline.get_formset(request, form.instance)

        prefix = f"{form.prefix}-{InlineFormSet.get_default_prefix()}"
        formset_params = self.get_formset_kwargs(request, obj, inline, prefix)

        formset_params.update(
            {
                "instance": form.instance,
                "prefix": prefix,
            }
        )
        inline_formset = InlineFormSet(**formset_params)

        # Bypass validation of each view-only inline form (since the form's
        # data won't be in request.POST), unless the form was deleted.
        if not inline.has_change_permission(request, obj if change else None):
            for index, form in enumerate(inline_formset.initial_forms):
                if self._user_deleted_form(prefix, request, inline, obj, index):
                    continue
                form._errors = {}
                form.cleaned_data = form.initial

        return InlineAdminFormSet(
            inline=inline,
            formset=inline_formset,
            model_admin=self.opts,
            fieldsets=list(inline.get_fieldsets(request, obj)),
            prepopulated_fields=dict(inline.get_prepopulated_fields(request, obj)),
            readonly_fields=list(inline.get_readonly_fields(request, obj)),
            **self._nested_inline_permissions(request, inline, inline_formset, obj),
        )

    def _check_nested_inline_permissions(
        self,
        request: HttpRequest,
        inline: InlineModelAdmin,
        obj: Model | None = None,
    ) -> bool:
        if not (
            inline.has_view_or_change_permission(request, obj)
            or inline.has_add_permission(request, obj)
            or inline.has_delete_permission(request, obj)
        ):
            return False

        return True

    def _user_deleted_form(
        self,
        prefix: str,
        request: HttpRequest,
        inline: InlineModelAdmin,
        obj: Model,
        index: int,
    ) -> bool:
        return (
            inline.has_delete_permission(request, obj)
            and f"{prefix}-{index}-DELETE" in request.POST
        )

    def _nested_inline_permissions(
        self,
        request: HttpRequest,
        inline: InlineModelAdmin,
        inline_formset: BaseInlineFormSet,
        obj: Model,
    ) -> dict[str, bool]:
        can_edit_parent = (
            self.has_change_permission(request, obj)
            if obj
            else self.has_add_permission(request)
        )

        if can_edit_parent:
            has_add_permission = inline.has_add_permission(request, obj)
            has_change_permission = inline.has_change_permission(request, obj)
            has_delete_permission = inline.has_delete_permission(request, obj)
        else:
            has_add_permission = has_change_permission = has_delete_permission = False
            inline_formset.extra = inline_formset.max_num = 0

        has_view_permission = inline.has_view_permission(request, obj)

        return {
            "has_add_permission": has_add_permission,
            "has_change_permission": has_change_permission,
            "has_delete_permission": has_delete_permission,
            "has_view_permission": has_view_permission,
        }
