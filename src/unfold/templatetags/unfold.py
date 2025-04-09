import json
from collections.abc import Mapping
from typing import Any, Optional, Union

from django import template
from django.contrib.admin.helpers import AdminForm, Fieldset
from django.contrib.admin.views.main import ChangeList
from django.contrib.admin.widgets import RelatedFieldWidgetWrapper
from django.db.models import Model
from django.db.models.options import Options
from django.forms import BoundField, CheckboxSelectMultiple, Field
from django.http import HttpRequest
from django.template import Context, Library, Node, RequestContext, TemplateSyntaxError
from django.template.base import NodeList, Parser, Token, token_kwargs
from django.template.loader import render_to_string
from django.utils.safestring import SafeText, mark_safe

from unfold.components import ComponentRegistry
from unfold.dataclasses import UnfoldAction
from unfold.enums import ActionVariant
from unfold.widgets import UnfoldAdminMoneyWidget, UnfoldAdminSplitDateTimeWidget

register = Library()


def _get_tabs_list(
    context: RequestContext, page: str, opts: Optional[Options] = None
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


@register.simple_tag(name="tab_list", takes_context=True)
def tab_list(context: RequestContext, page: str, opts: Optional[Options] = None) -> str:
    inlines_list = []

    data = {
        "nav_global": context.get("nav_global"),
        "actions_detail": context.get("actions_detail"),
        "actions_list": context.get("actions_list"),
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


class CaptureNode(Node):
    def __init__(self, nodelist: NodeList, varname: str, silent: bool) -> None:
        self.nodelist = nodelist
        self.varname = varname
        self.silent = silent

    def render(self, context: dict[str, Any]) -> Union[str, SafeText]:
        output = self.nodelist.render(context)
        context[self.varname] = output
        if self.silent:
            return ""
        else:
            return output


@register.tag(name="capture")
def do_capture(parser: Parser, token: Token) -> CaptureNode:
    """
    Capture the contents of a tag output.
    Usage:
    .. code-block:: html+django
        {% capture %}..{% endcapture %}                    # output in {{ capture }}
        {% capture silent %}..{% endcapture %}             # output in {{ capture }} only
        {% capture as varname %}..{% endcapture %}         # output in {{ varname }}
        {% capture as varname silent %}..{% endcapture %}  # output in {{ varname }} only
    For example:
    .. code-block:: html+django
        {# Allow templates to override the page title/description #}
        <meta name="description" content="{% capture as meta_description %}
            {% block meta-description %}{% endblock %}{% endcapture %}" />
        <title>{% capture as meta_title %}{% block meta-title %}Untitled{% endblock %}{% endcapture %}</title>
        {# copy the values to the Social Media meta tags #}
        <meta property="og:description" content="{% block og-description %}{{ meta_description }}{% endblock %}" />
        <meta name="twitter:title" content="{% block twitter-title %}{{ meta_title }}{% endblock %}" />
    """
    bits = token.split_contents()

    # tokens
    t_as = "as"
    t_silent = "silent"
    var = "capture"
    silent = False

    num_bits = len(bits)
    if len(bits) > 4:
        raise TemplateSyntaxError(
            "'capture' node supports '[as variable] [silent]' parameters."
        )
    elif num_bits == 4:
        t_name, t_as, var, t_silent = bits
        silent = True
    elif num_bits == 3:
        t_name, t_as, var = bits
    elif num_bits == 2:
        t_name, t_silent = bits
        silent = True
    else:
        var = "capture"
        silent = False

    if t_silent != "silent" or t_as != "as":
        raise TemplateSyntaxError(
            "'capture' node expects 'as variable' or 'silent' syntax."
        )

    nodelist = parser.parse(("endcapture",))
    parser.delete_first_token()
    return CaptureNode(nodelist, var, silent)


class RenderComponentNode(template.Node):
    def __init__(
        self,
        template_name: str,
        nodelist: NodeList,
        extra_context: Optional[dict] = None,
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

        values.update(
            {
                "children": self.nodelist.render(context),
            }
        )

        if "component_class" in values:
            values = ComponentRegistry.create_instance(
                values["component_class"],
                request=context.request if hasattr(context, "request") else None,
            ).get_context_data(**values)

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
def add_css_class(field: Field, classes: Union[list, tuple]) -> Field:
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
    request: Optional[HttpRequest] = context.get("request")
    changelist: Optional[ChangeList] = context.get("cl")

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
def fieldset_rows_classes(context: Context) -> str:
    classes = [
        "aligned",
    ]

    if not context.get("stacked"):
        classes.extend(
            [
                "border",
                "border-base-200",
                "mb-8",
                "rounded",
                "shadow-sm",
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
            and field.field.name == formset.opts.ordering_field
            and formset.opts.hide_ordering_field
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
        "flex-grow",
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
                "first:lg:border-l-0",
            ]
        )

    return " ".join(set(classes))


@register.simple_tag(takes_context=True)
def action_item_classes(context: Context, action: UnfoldAction) -> str:
    classes = [
        "border",
        "-ml-px",
        "max-md:first:rounded-t",
        "max-md:last:rounded-b",
        "md:first:rounded-l",
        "md:last:rounded-r",
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


@register.filter(takes_context=True)
def changeform_condition(field: BoundField) -> BoundField:
    if isinstance(field.field, dict):
        return field

    if isinstance(field.field.field.widget, RelatedFieldWidgetWrapper):
        field.field.field.widget.widget.attrs["x-model.fill"] = field.field.name
        field.field.field.widget.widget.attrs["x-init"] = mark_safe(
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
