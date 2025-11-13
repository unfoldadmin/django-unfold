import json
from collections.abc import Iterable, Mapping
from typing import Any

from django import template
from django.contrib.admin.helpers import AdminForm, Fieldset
from django.contrib.admin.views.main import PAGE_VAR, ChangeList
from django.contrib.admin.widgets import RelatedFieldWidgetWrapper
from django.core.paginator import Paginator
from django.db.models import Model
from django.db.models.options import Options
from django.forms import BoundField, CheckboxSelectMultiple, Field
from django.http import HttpRequest, QueryDict
from django.template import Context, Library, Node, RequestContext, TemplateSyntaxError
from django.template.base import NodeList, Parser, Token, token_kwargs
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.utils.safestring import SafeText, mark_safe
from django.utils.translation import gettext_lazy as _

from unfold.components import ComponentRegistry
from unfold.dataclasses import UnfoldAction
from unfold.enums import ActionVariant
from unfold.widgets import (
    UnfoldAdminMoneyWidget,
    UnfoldAdminSelect2Widget,
    UnfoldAdminSplitDateTimeWidget,
)

register = Library()


def _get_tabs_list(
    context: RequestContext, page: str, opts: Options | None = None
) -> list:
    tabs_list = []
    page_id = None

    if page not in ["changeform", "changelist"]:
        page_id = page

    for tab in context.get("tab_list", []):
        if page_id:
            if tab.get("page") == page_id:
                tabs_list = tab["items"]
                break

            continue

        if "models" not in tab:
            continue

        for tab_model in tab["models"]:
            if isinstance(tab_model, str):
                if str(opts) == tab_model and page == "changelist":
                    tabs_list = tab["items"]
                    break
            elif isinstance(tab_model, dict) and str(opts) == tab_model["name"]:
                is_detail = tab_model.get("detail", False)

                if (page == "changeform" and is_detail) or (
                    page == "changelist" and not is_detail
                ):
                    tabs_list = tab["items"]
                    break
    return tabs_list


@register.simple_tag(name="action_list", takes_context=True)
def action_list(context: RequestContext) -> str:
    data = {
        "nav_global": context.get("nav_global"),
        "actions_detail": context.get("actions_detail"),
        "actions_detail_hide_default": context.get("actions_detail_hide_default"),
        "actions_list": context.get("actions_list"),
        "actions_list_hide_default": context.get("actions_list_hide_default"),
        "actions_items": context.get("actions_items"),
    }

    return render_to_string(
        "unfold/helpers/tab_actions.html",
        request=context["request"],
        context=data,
    )


@register.simple_tag(name="tab_list", takes_context=True)
def tab_list(context: RequestContext, page: str, opts: Options | None = None) -> str:
    inlines_list = []
    datasets_list = []
    data = {
        "actions_items": context.get("actions_items"),
        "is_popup": context.get("is_popup"),
        "tabs_list": _get_tabs_list(context, page, opts),
    }

    # If the changeform is rendered and there are no custom tab navigation
    # specified, check for inlines to put into tabs
    if page == "changeform" and len(data["tabs_list"]) == 0:
        for inline in context.get("inline_admin_formsets", []):
            if opts and hasattr(inline.opts, "tab"):
                inlines_list.append(inline)

        if len(inlines_list) > 0:
            data["inlines_list"] = inlines_list

        for dataset in context.get("datasets", []):
            if dataset and hasattr(dataset, "tab"):
                datasets_list.append(dataset)

        if len(datasets_list) > 0:
            data["datasets_list"] = datasets_list

    return render_to_string(
        "unfold/helpers/tab_list.html",
        request=context["request"],
        context=data,
    )


@register.simple_tag(name="render_section", takes_context=True)
def render_section(context: Context, section_class, instance: Model) -> str:
    return section_class(context.request, instance).render()


@register.simple_tag(name="has_nav_item_active")
def has_nav_item_active(items: list) -> bool:
    for item in items:
        if "active" in item and item["active"]:
            return True

    return False


@register.filter
def class_name(value: Any) -> str:
    return value.__class__.__name__


@register.filter
def is_list(value: Any) -> str:
    return isinstance(value, list)


@register.filter
def has_active_item(items: list[dict]) -> bool:
    for item in items:
        if "active" in item and item["active"]:
            return True

    return False


@register.filter
def index(indexable: Mapping[int, Any], i: int) -> Any:
    try:
        return indexable[i]
    except (KeyError, TypeError):
        return None


@register.filter
def tabs(adminform: AdminForm) -> list[Fieldset]:
    result = []

    for fieldset in adminform:
        if "tab" in fieldset.classes and fieldset.name:
            result.append(fieldset)

    return result


class RenderComponentNode(template.Node):
    def __init__(
        self,
        template_name: str,
        nodelist: NodeList,
        extra_context: dict | None = None,
        include_context: bool = False,
        *args,
        **kwargs,
    ):
        self.template_name = template_name
        self.nodelist = nodelist
        self.extra_context = extra_context or {}
        self.include_context = include_context
        super().__init__(*args, **kwargs)

    def render(self, context: RequestContext) -> str:
        values = {
            name: var.resolve(context) for name, var in self.extra_context.items()
        }

        if "component_class" in values:
            values = ComponentRegistry.create_instance(
                values["component_class"],
                request=context.request if hasattr(context, "request") else None,
            ).get_context_data(**values)

        context_copy = context.new()
        context_copy.update(context.flatten())
        context_copy.update(values)
        children = self.nodelist.render(context_copy)

        if len(children) > 0:
            values.update(
                {
                    "children": children,
                }
            )

        if self.include_context:
            values.update(context.flatten())

        return render_to_string(
            self.template_name,
            request=context.request if hasattr(context, "request") else None,
            context=values,
        )


@register.tag("component")
def do_component(parser: Parser, token: Token) -> str:
    bits = token.split_contents()

    if len(bits) < 2:
        raise TemplateSyntaxError(
            f"{bits[0]} tag takes at least one argument: the name of the template to be included."
        )

    options = {}
    remaining_bits = bits[2:]

    while remaining_bits:
        option = remaining_bits.pop(0)

        if option in options:
            raise TemplateSyntaxError(
                f"The {option} option was specified more than once."
            )

        if option == "with":
            value = token_kwargs(remaining_bits, parser, support_legacy=False)

            if not value:
                raise TemplateSyntaxError(
                    '"with" in {bits[0]} tag needs at least one keyword argument.'
                )
        elif option == "include_context":
            value = True
        else:
            raise TemplateSyntaxError(f"Unknown argument for {bits[0]} tag: {option}.")

        options[option] = value

    include_context = options.get("include_context", False)
    nodelist = parser.parse(("endcomponent",))
    template_name = bits[1][1:-1]

    extra_context = options.get("with", {})
    parser.next_token()

    return RenderComponentNode(template_name, nodelist, extra_context, include_context)


@register.filter
def add_css_class(field: Field, classes: list | tuple) -> Field:
    if type(classes) in (list, tuple):
        classes = " ".join(classes)

    if "class" in field.field.widget.attrs:
        field.field.widget.attrs["class"] += f" {classes}"
    else:
        field.field.widget.attrs["class"] = classes

    return field


@register.inclusion_tag(
    "unfold/templatetags/preserve_changelist_filters.html",
    takes_context=True,
    name="preserve_filters",
)
def preserve_changelist_filters(context: Context) -> dict[str, dict[str, str]]:
    """
    Generate hidden input fields to preserve filters for POST forms.
    """
    request: HttpRequest | None = context.get("request")
    changelist: ChangeList | None = context.get("cl")

    if not request or not changelist:
        return {"params": {}}

    used_params: set[str] = {
        param for spec in changelist.filter_specs for param in spec.used_parameters
    }
    preserved_params: dict[str, str] = {
        param: value for param, value in request.GET.items() if param not in used_params
    }

    return {"params": preserved_params}


@register.simple_tag(takes_context=True)
def element_classes(context: Context, key: str) -> str:
    if key in context.get("element_classes", {}):
        if isinstance(context["element_classes"][key], list | tuple):
            return " ".join(context["element_classes"][key])

        return context["element_classes"][key]

    return ""


@register.simple_tag(takes_context=True)
def fieldset_rows_classes(context: Context) -> str:
    classes = [
        "aligned",
    ]

    if not context.get("stacked"):
        classes.extend(
            [
                "border",
                "border-base-200",
                "rounded-default",
                "shadow-xs",
                "dark:border-base-800",
            ]
        )

    return " ".join(set(classes))


@register.simple_tag(takes_context=True)
def fieldset_row_classes(context: Context) -> str:
    classes = [
        "form-row",
        "field-row",
        "group/row",
    ]

    formset = context.get("inline_admin_formset", None)
    line = context.get("line")

    # Hide the field in case of ordering field for sorting
    for field in line:
        if (
            formset
            and hasattr(field.field, "name")
            and field.field.name == getattr(formset.opts, "ordering_field", None)
            and getattr(formset.opts, "hide_ordering_field", False)
        ):
            classes.append("hidden")

    if len(line.fields) > 1:
        classes.extend(
            [
                "grid",
                f"lg:grid-cols-{len(line.fields)}",
            ]
        )

    if not line.has_visible_field:
        classes.append("hidden")

    return " ".join(set(classes))


@register.simple_tag(takes_context=True)
def fieldset_line_classes(context: Context) -> str:
    classes = [
        "field-line",
        "flex",
        "flex-col",
        "grow",
        "group",
        "group/line",
        "px-3",
        "py-2.5",
    ]
    field = context.get("field")
    adminform = context.get("adminform")

    if hasattr(field.field, "name") and field.field.name:
        classes.append(f"field-{field.field.name}")

    if hasattr(field, "errors") and field.errors():
        classes.append("errors")

    if (
        adminform
        and hasattr(adminform.model_admin, "compressed_fields")
        and adminform.model_admin.compressed_fields
    ):
        classes.extend(
            [
                "border-b",
                "border-base-200",
                "border-dashed",
                "group-[.last]/row:border-b-0",
                "lg:border-l",
                "lg:flex-row",
                "dark:border-base-800",
                "lg:first:border-l-0",
            ]
        )

    return " ".join(set(classes))


@register.simple_tag(takes_context=True)
def action_item_classes(context: Context, action: UnfoldAction) -> str:
    classes = [
        "border",
        "border-base-200",
        "max-lg:-mt-px",
        "max-lg:first:rounded-t-default",
        "max-lg:last:rounded-b-default",
        "min-lg:-ml-px",
        "min-lg:first:rounded-l-default",
        "min-lg:last:rounded-r-default",
    ]

    if "variant" not in action:
        variant = ActionVariant.DEFAULT
    else:
        variant = action["variant"]

    if variant == ActionVariant.PRIMARY:
        classes.extend(
            [
                "border-primary-700",
                "bg-primary-600",
                "text-white",
                "dark:border-primary-500",
            ]
        )
    elif variant == ActionVariant.DANGER:
        classes.extend(
            [
                "border-red-700",
                "bg-red-600",
                "text-white",
                "dark:border-red-500",
            ]
        )
    elif variant == ActionVariant.SUCCESS:
        classes.extend(
            [
                "border-green-700",
                "bg-green-600",
                "text-white",
                "dark:border-green-500",
            ]
        )
    elif variant == ActionVariant.INFO:
        classes.extend(
            [
                "border-blue-700",
                "bg-blue-600",
                "text-white",
                "dark:border-blue-500",
            ]
        )
    elif variant == ActionVariant.WARNING:
        classes.extend(
            [
                "border-orange-700",
                "bg-orange-600",
                "text-white",
                "dark:border-orange-500",
            ]
        )
    else:
        classes.extend(
            [
                "border-base-200",
                "hover:text-primary-600",
                "dark:hover:text-primary-500",
                "dark:border-base-700",
            ]
        )

    return " ".join(set(classes))


@register.filter
def changeform_data(adminform: AdminForm) -> str:
    fields = {}

    for fieldset in adminform:
        for line in fieldset:
            for field in line:
                if isinstance(field.field, dict):
                    continue

                if isinstance(
                    field.field.field.widget, UnfoldAdminSplitDateTimeWidget
                ) or isinstance(field.field.field.widget, UnfoldAdminMoneyWidget):
                    for index, _widget in enumerate(field.field.field.widget.widgets):
                        fields[
                            f"{field.field.name}{field.field.field.widget.widgets_names[index]}"
                        ] = None
                elif isinstance(field.field.field.widget, CheckboxSelectMultiple):
                    fields[field.field.name] = []
                else:
                    fields[field.field.name] = None

    return mark_safe(json.dumps(fields))


@register.filter
def changeform_condition(field: BoundField) -> BoundField:
    if isinstance(field.field, dict):
        return field

    if isinstance(field.field.field.widget, RelatedFieldWidgetWrapper):
        field.field.field.widget.widget.attrs["x-model.fill"] = field.field.name
        field.field.field.widget.widget.attrs["x-init"] = mark_safe(
            f"const $ = django.jQuery; $(function () {{ const select = $('#{field.field.auto_id}'); select.on('change', (ev) => {{ {field.field.name} = select.val(); }}); }});"
        )
    elif isinstance(field.field.field.widget, UnfoldAdminSelect2Widget):
        field.field.field.widget.attrs["x-model.fill"] = field.field.name
        field.field.field.widget.attrs["x-init"] = mark_safe(
            f"const $ = django.jQuery; $(function () {{ const select = $('#{field.field.auto_id}'); select.on('change', (ev) => {{ {field.field.name} = select.val(); }}); }});"
        )
    elif isinstance(
        field.field.field.widget, UnfoldAdminSplitDateTimeWidget
    ) or isinstance(field.field.field.widget, UnfoldAdminMoneyWidget):
        for index, widget in enumerate(field.field.field.widget.widgets):
            field_name = (
                f"{field.field.name}{field.field.field.widget.widgets_names[index]}"
            )

            widget.attrs["x-model.fill"] = field_name
    else:
        field.field.field.widget.attrs["x-model.fill"] = field.field.name

    return field


@register.simple_tag
def infinite_paginator_url(cl, i):
    return cl.get_query_string({PAGE_VAR: i})


@register.simple_tag
def elided_page_range(paginator: Paginator, number: int) -> list[int | str] | None:
    if not paginator or not number:
        return None

    return paginator.get_elided_page_range(number=number)


@register.simple_tag(takes_context=True)
def querystring_params(
    context: RequestContext, query_key: str, query_value: str
) -> str:
    request = context.get("request")
    result = QueryDict(mutable=True)

    for key, values in request.GET.lists():
        if key == query_key:
            continue

        for value in values:
            result[key] = value

    result[query_key] = query_value

    return result.urlencode()


@register.simple_tag(name="unfold_querystring", takes_context=True)
def unfold_querystring(context, *args, **kwargs):
    """
    Duplicated querystring template tag from Django core to allow
    it using in Django 4.x. Once 4.x is not supported, remove it.
    """
    if not args:
        args = [context.request.GET]
    params = QueryDict(mutable=True)
    for d in [*args, kwargs]:
        if not isinstance(d, Mapping):
            raise TemplateSyntaxError(
                "querystring requires mappings for positional arguments (got "
                f"{d!r} instead)."
            )
        for key, value in d.items():
            if not isinstance(key, str):
                raise TemplateSyntaxError(
                    f"querystring requires strings for mapping keys (got {key!r} "
                    "instead)."
                )
            if value is None:
                params.pop(key, None)
            elif isinstance(value, Iterable) and not isinstance(value, str):
                params.setlist(key, value)
            else:
                params[key] = value
    query_string = params.urlencode() if params else ""
    return f"?{query_string}"


@register.simple_tag(takes_context=True)
def header_title(context: RequestContext) -> str:
    parts = []
    opts = context.get("opts")
    current_app = (
        context.request.current_app
        if hasattr(context.request, "current_app")
        else "admin"
    )

    if opts:
        parts.append(
            {
                "link": reverse_lazy(f"{current_app}:app_list", args=[opts.app_label]),
                "title": opts.app_config.verbose_name,
            }
        )

        if (original := context.get("original")) and not isinstance(original, str):
            parts.append(
                {
                    "link": reverse_lazy(
                        f"{current_app}:{original._meta.app_label}_{original._meta.model_name}_changelist"
                    ),
                    "title": original._meta.verbose_name_plural,
                }
            )

            parts.append(
                {
                    "link": reverse_lazy(
                        f"{current_app}:{original._meta.app_label}_{original._meta.model_name}_change",
                        args=[original.pk],
                    ),
                    "title": original,
                }
            )
        elif object := context.get("object"):
            parts.append(
                {
                    "link": reverse_lazy(
                        f"{current_app}:{object._meta.app_label}_{object._meta.model_name}_changelist"
                    ),
                    "title": object._meta.verbose_name_plural,
                }
            )

            parts.append(
                {
                    "link": reverse_lazy(
                        f"{current_app}:{object._meta.app_label}_{object._meta.model_name}_change",
                        args=[object.pk],
                    ),
                    "title": object,
                }
            )
        else:
            parts.append(
                {
                    "link": reverse_lazy(
                        f"{current_app}:{opts.app_label}_{opts.model_name}_changelist"
                    ),
                    "title": opts.verbose_name_plural,
                }
            )
    elif object := context.get("object"):
        parts.append(
            {
                "link": reverse_lazy(
                    f"{current_app}:app_list", args=[object._meta.app_label]
                ),
                "title": object._meta.app_label,
            }
        )

        parts.append(
            {
                "link": reverse_lazy(
                    f"{current_app}:{object._meta.app_label}_{object._meta.model_name}_changelist",
                ),
                "title": object._meta.verbose_name_plural,
            }
        )

        parts.append(
            {
                "link": reverse_lazy(
                    f"{current_app}:{object._meta.app_label}_{object._meta.model_name}_change",
                    args=[object.pk],
                ),
                "title": object,
            }
        )
    elif (model_admin := context.get("model_admin")) and hasattr(model_admin, "model"):
        parts.append(
            {
                "link": reverse_lazy(
                    f"{current_app}:app_list", args=[model_admin.model._meta.app_label]
                ),
                "title": model_admin.model._meta.app_label,
            }
        )

        parts.append(
            {
                "link": reverse_lazy(
                    f"{current_app}:{model_admin.model._meta.app_label}_{model_admin.model._meta.model_name}_changelist",
                ),
                "title": model_admin.model._meta.verbose_name_plural,
            }
        )

    if not opts and (content_title := context.get("content_title")):
        parts.append(
            {
                "title": content_title,
            }
        )

    if len(parts) == 0:
        username = (
            context.request.user.get_short_name() or context.request.user.get_username()
        )
        parts.append({"title": f"{_('Welcome')} {username}"})

    return render_to_string(
        "unfold/helpers/header_title.html",
        request=context.request,
        context={
            "parts": parts,
        },
    )


@register.simple_tag(takes_context=True)
def admin_object_app_url(context: RequestContext, object: Model, arg: str) -> str:
    current_app = (
        context.request.current_app
        if hasattr(context.request, "current_app")
        else "admin"
    )

    return f"{current_app}:{object._meta.app_label}_{object._meta.model_name}_{arg}"


@register.filter
def has_nested_tables(table: dict) -> bool:
    return any(
        isinstance(row, dict) and "table" in row for row in table.get("rows", [])
    )


class RenderCaptureNode(Node):
    def __init__(self, nodelist: NodeList, variable_name: str, silent: bool) -> None:
        self.nodelist = nodelist
        self.variable_name = variable_name
        self.silent = silent

    def render(self, context: dict[str, Any]) -> str | SafeText:
        content = self.nodelist.render(context)

        if not self.silent:
            return content

        context.update(
            {
                self.variable_name: content,
            }
        )

        return ""


@register.tag(name="capture")
def do_capture(parser: Parser, token: Token) -> RenderCaptureNode:
    parts = token.split_contents()
    variable_name = ""
    silent = False

    if len(parts) > 4:
        raise TemplateSyntaxError("Too many arguments for 'capture' tag.")

    if len(parts) >= 3:
        if parts[1] != "as":
            raise TemplateSyntaxError("'as' is required for 'capture' tag.")

        variable_name = parts[2]

    if len(parts) == 4:
        if parts[3] != "silent":
            raise TemplateSyntaxError("'silent' is required for 'capture' tag.")

        silent = True

    nodelist = parser.parse(("endcapture",))
    parser.delete_first_token()
    return RenderCaptureNode(nodelist, variable_name, silent)
