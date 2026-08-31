from collections.abc import Iterable, Iterator
from typing import Any

from django.contrib.admin import options
from django.contrib.admin.helpers import InlineAdminFormSet
from django.contrib.admin.options import InlineModelAdmin
from django.core.exceptions import ImproperlyConfigured, ObjectDoesNotExist
from django.db.models import ForeignKey, Model
from django.forms import BaseInlineFormSet, ModelForm
from django.http import HttpRequest, HttpResponse
from django.utils.translation import gettext_lazy as _


def iter_nested_formsets(
    formsets: Iterable[BaseInlineFormSet],
) -> Iterator[InlineAdminFormSet]:
    """
    Walk the whole tree of nested formsets below the given formsets and yield
    every one of them, no matter how deep it is.
    """
    for formset in formsets:
        groups = [getattr(form, "nested_formsets", ()) for form in formset.forms]

        # The template form used for adding records carries its own nested
        # formsets on the form class. A formset without any row, `extra` being
        # zero and nothing saved yet, has them and nothing else.
        groups.append(getattr(formset.form, "nested_formsets", ()))

        for group in groups:
            for nested_formset in group:
                yield nested_formset

                yield from iter_nested_formsets([nested_formset.formset])


def nested_all_valid(formsets: list[BaseInlineFormSet]) -> bool:
    # Mirrors `django.contrib.admin.options.all_valid()` by validating every
    # formset instead of stopping at the first invalid one, otherwise the
    # formsets after it would never report their own errors.
    validation_result = True

    for formset in formsets:
        if not formset.is_valid():
            validation_result = False

    for formset in formsets:
        for form in formset.forms:
            nested_formsets = getattr(form, "nested_formsets", None)

            if not nested_formsets:
                continue

            for nested_formset in nested_formsets:
                if not nested_all_valid([nested_formset.formset]):
                    validation_result = False

                if (
                    nested_formset.formset.has_changed()
                    and hasattr(form, "cleaned_data")
                    and len(form.cleaned_data) == 0
                    and form.instance.pk is None
                ):
                    form.add_error(
                        None, _("You can not create nested object without parent")
                    )
                    validation_result = False

    return validation_result


class NestedInlinesModelAdminMixin:
    # How many levels of nested inlines are rendered. `None` lets the nesting go
    # as deep as the inline declarations themselves, which terminates on its own
    # for any acyclic chain. A chain where an inline is its own descendant never
    # terminates, because every level renders a template form for adding new
    # records, and therefore requires an explicit value.
    nested_inlines_max_depth: int | None = None

    # Detecting the relation to traverse only depends on the pair of models, so
    # the answer is remembered instead of being looked up for every single form.
    _nested_parent_field_names: dict[
        tuple[type[Model], type[InlineModelAdmin]], str | None
    ] = {}

    def get_nested_inlines_max_depth(self) -> int | None:
        return self.nested_inlines_max_depth

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

    def render_change_form(
        self,
        request: HttpRequest,
        context: dict[str, Any],
        add: bool = False,
        change: bool = False,
        form_url: str = "",
        obj: Model | None = None,
    ) -> HttpResponse:
        response = super().render_change_form(
            request, context, add, change, form_url, obj
        )

        # Nested formsets are not part of `inline_admin_formsets`, so Django does
        # not take them into account when it decides if the form has to be
        # multipart. Without this, file fields in nested inlines are silently
        # dropped on save.
        context_data = getattr(response, "context_data", None)

        if context_data is None:
            return response

        if not context_data.get("has_file_field"):
            context_data["has_file_field"] = any(
                nested_formset.formset.is_multipart()
                for nested_formset in iter_nested_formsets(
                    admin_formset.formset
                    for admin_formset in context.get("inline_admin_formsets", [])
                )
            )

        if "media" in context_data:
            for media in getattr(request, "_unfold_nested_formset_media", {}).values():
                context_data["media"] += media

        return response

    def save_formset(
        self,
        request: HttpRequest,
        form: ModelForm,
        formset: BaseInlineFormSet,
        change: bool,
    ) -> None:
        super().save_formset(request, form, formset, change)

        # TODO: fix linting error
        for form in formset.forms:  # noqa: PLR1704
            if not hasattr(form, "nested_formsets"):
                continue

            if form in formset.deleted_forms:
                continue

            for nested_formset in form.nested_formsets:
                self._bind_nested_formset_instance(form, nested_formset.formset)
                self.save_formset(request, form, nested_formset.formset, change)

    def _bind_nested_formset_instance(
        self, form: ModelForm, formset: BaseInlineFormSet
    ) -> None:
        """
        Point a nested formset at the parent the submitted data actually names.

        When the inline is attached through a relation of its parent inline, the
        instance resolved while building the formset is the one the relation had
        before the form was submitted, and is missing entirely for a row which
        was created by this same request. Both are resolved once the form
        holding the relation has been saved.
        """
        field_name = getattr(formset, "nested_parent_field_name", None)

        if field_name is None:
            return

        instance = self._resolve_related(form.instance, field_name)

        if instance is not None:
            formset.instance = instance

    def _build_nested_formsets(
        self,
        request: HttpRequest,
        obj: Model,
        formsets: list[BaseInlineFormSet],
        inline_instances: list[InlineModelAdmin],
        change: bool,
    ) -> None:
        # A ModelAdmin is instantiated once and shared by every request being
        # served, so the media of the nested formsets is collected on the
        # request instead. Keyed by inline class, the media of a class is the
        # same for each of its formsets and adding media is linear in what has
        # been added so far.
        request._unfold_nested_formset_media = {}

        for formset, inline in zip(formsets, inline_instances):
            self._attach_nested_formsets(request, obj, formset, inline, change, ())

    def _attach_nested_formsets(
        self,
        request: HttpRequest,
        obj: Model,
        formset: BaseInlineFormSet,
        inline: InlineModelAdmin,
        change: bool,
        chain: tuple[type[InlineModelAdmin], ...],
        is_template: bool = False,
    ) -> None:
        if not getattr(inline, "inlines", None):
            return

        # Existing forms in formset
        for form in formset.forms:
            form.nested_formsets = self._build_form_nested_formsets(
                request, obj, form, inline, change, chain, is_template
            )

        # Add nested forms to template form in formsets
        if hasattr(formset, "empty_form") and inline.has_add_permission(request, obj):
            formset.form.nested_formsets = self._build_form_nested_formsets(
                request, obj, formset.empty_form, inline, change, chain, True
            )

    def _build_form_nested_formsets(
        self,
        request: HttpRequest,
        obj: Model,
        form: ModelForm,
        parent_inline: InlineModelAdmin,
        change: bool,
        chain: tuple[type[InlineModelAdmin], ...],
        is_template: bool = False,
    ) -> list[InlineAdminFormSet]:
        from unfold.admin import TabularInline

        max_depth = self.get_nested_inlines_max_depth()

        if max_depth is not None and len(chain) >= max_depth:
            return []

        nested_formsets = []

        for inline_class in parent_inline.inlines:
            if max_depth is None and inline_class in chain:
                raise ImproperlyConfigured(
                    f"{inline_class.__name__} is nested within itself "
                    f"({' -> '.join(item.__name__ for item in (*chain, inline_class))}). "
                    "Set 'nested_inlines_max_depth' on "
                    f"{self.__class__.__name__} to limit how many levels are rendered."
                )

            inline_formset = self._get_nested_formset(
                request, obj, form, parent_inline, inline_class, change, is_template
            )

            if not inline_formset:
                continue

            inline_formset.inline_type = "stacked"
            if issubclass(inline_class, TabularInline):
                inline_formset.inline_type = "tabular"

            nested_formsets.append(inline_formset)

            collected = getattr(request, "_unfold_nested_formset_media", None)
            if collected is not None and inline_class not in collected:
                collected[inline_class] = inline_formset.media

            self._attach_nested_formsets(
                request,
                obj,
                inline_formset.formset,
                inline_formset.opts,
                change,
                (*chain, inline_class),
                is_template,
            )

        return nested_formsets

    def _get_nested_formset(
        self,
        request: HttpRequest,
        obj: Model,
        form: ModelForm,
        parent_inline: InlineModelAdmin,
        inline_class: type[InlineModelAdmin],
        change: bool,
        is_template: bool = False,
    ) -> InlineAdminFormSet | None:
        parent_model, parent_instance, parent_field_name = self._get_nested_parent(
            form, parent_inline, inline_class
        )

        inline = inline_class(parent_model, self.admin_site)

        if not self._check_nested_inline_permissions(request, inline, obj):
            return None

        if not inline.has_add_permission(request, obj):
            inline.max_num = 0

        InlineFormSet = inline.get_formset(request, parent_instance)

        prefix = f"{form.prefix}-{InlineFormSet.get_default_prefix()}"
        formset_params = self.get_formset_kwargs(request, obj, inline, prefix)

        formset_params.update(
            {
                "instance": parent_instance,
                "prefix": prefix,
            }
        )

        # Nested formsets below an empty form are only client side templates for
        # adding new records. Binding them to the submitted data would make them
        # report errors about management data which is never sent for a prefix
        # still containing the `__prefix__` placeholder.
        if is_template:
            for param in ("data", "files", "save_as_new"):
                formset_params.pop(param, None)

        inline_formset = InlineFormSet(**formset_params)

        # Bypass validation of each view-only inline form (since the form's
        # data won't be in request.POST), unless the form was deleted.
        if not inline.has_change_permission(request, obj if change else None):
            # TODO: fix linting error
            for index, form in enumerate(inline_formset.initial_forms):  # noqa: PLR1704
                if self._user_deleted_form(prefix, request, inline, obj, index):
                    continue
                form._errors = {}
                form.cleaned_data = form.initial

        # Remembered so that saving can resolve the parent again, after the
        # form which holds the relation has been saved itself.
        inline_formset.nested_parent_field_name = parent_field_name

        return InlineAdminFormSet(
            inline=inline,
            formset=inline_formset,
            model_admin=self.opts,
            fieldsets=list(inline.get_fieldsets(request, obj)),
            prepopulated_fields=dict(inline.get_prepopulated_fields(request, obj)),
            readonly_fields=list(inline.get_readonly_fields(request, obj)),
            **self._nested_inline_permissions(request, inline, inline_formset, obj),
        )

    def _get_nested_parent(
        self,
        form: ModelForm,
        parent_inline: InlineModelAdmin,
        inline_class: type[InlineModelAdmin],
    ) -> tuple[type[Model], Model | None, str | None]:
        """
        Resolve the model and the instance a nested inline is attached to.

        Usually those are the model and the instance of the parent inline. When
        the parent inline renders an intermediary model instead, the auto
        created table behind a many-to-many relation being the common case, the
        nested inline is attached to the model on the other side of that
        relation.
        """
        field_name = self._get_nested_parent_field(parent_inline.model, inline_class)

        if field_name is None:
            return parent_inline.model, form.instance, None

        field = parent_inline.model._meta.get_field(field_name)

        return (
            field.related_model,
            self._resolve_related(form.instance, field_name),
            (field_name),
        )

    def _resolve_related(self, instance: Model, field_name: str) -> Model | None:
        try:
            return getattr(instance, field_name)
        except ObjectDoesNotExist:
            return None

    def _get_nested_parent_field(
        self,
        parent_model: type[Model],
        inline_class: type[InlineModelAdmin],
    ) -> str | None:
        """Name the relation of `parent_model` a nested inline is reached through."""
        field_name = getattr(inline_class, "nested_parent_field", None)

        if field_name is not None:
            return field_name

        return self._get_nested_parent_field_name(parent_model, inline_class)

    def _get_nested_parent_field_name(
        self,
        parent_model: type[Model],
        inline_class: type[InlineModelAdmin],
    ) -> str | None:
        if self._get_foreign_keys_to(inline_class.model, parent_model):
            return None

        # Only an intermediary model stands between an inline and the records it
        # is really about. Anywhere else, an inline without a relation to its
        # parent is a mistake and has to keep raising the error Django raises
        # for it, instead of being attached to some other model which happens to
        # be reachable.
        if not parent_model._meta.auto_created:
            return None

        cache_key = (parent_model, inline_class)

        if cache_key in self._nested_parent_field_names:
            return self._nested_parent_field_names[cache_key]

        candidates = [
            field.name
            for field in parent_model._meta.fields
            if isinstance(field, ForeignKey)
            and self._get_foreign_keys_to(inline_class.model, field.remote_field.model)
        ]

        if len(candidates) == 1:
            self._nested_parent_field_names[cache_key] = candidates[0]
            return candidates[0]

        if len(candidates) > 1:
            raise ImproperlyConfigured(
                f"{inline_class.__name__} can be nested under "
                f"{parent_model._meta.label} through more than one relation "
                f"({', '.join(candidates)}). Set 'nested_parent_field' on "
                f"{inline_class.__name__} to pick one."
            )

        self._nested_parent_field_names[cache_key] = None
        return None

    def _get_foreign_keys_to(
        self, model: type[Model], parent_model: type[Model]
    ) -> list[ForeignKey]:
        return [
            field
            for field in model._meta.fields
            if isinstance(field, ForeignKey)
            and (
                field.remote_field.model == parent_model
                or field.remote_field.model in parent_model._meta.get_parent_list()
            )
        ]

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
