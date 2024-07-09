from typing import Any, Dict, List, Mapping, Optional, Union

from django import template
from django.contrib.admin.helpers import AdminForm, Fieldset
from django.forms import Field
from django.template import Library, Node, RequestContext, TemplateSyntaxError
from django.template.base import NodeList, Parser, Token, token_kwargs
from django.template.loader import render_to_string
from django.utils.safestring import SafeText

register = Library()


@register.simple_tag(name="tab_list", takes_context=True)
def tab_list(context, page, opts) -> str:
    tabs_list = []
    inlines_list = []

    data = {
        "nav_global": context.get("nav_global"),
        "actions_detail": context.get("actions_detail"),
        "actions_list": context.get("actions_list"),
        "actions_items": context.get("actions_items"),
        "is_popup": context.get("is_popup"),
    }

    for tab in context.get("tab_list", []):
        if str(opts) in tab["models"]:
            tabs_list = tab["items"]
            break

    if page == "changelist":
        data["tabs_list"] = tabs_list

    for inline in context.get("inline_admin_formsets", []):
        if hasattr(inline.opts, "tab"):
            inlines_list.append(inline)

    if page == "changeform" and len(inlines_list) > 0:
        data["inlines_list"] = inlines_list

    return render_to_string(
        "unfold/helpers/tab_list.html",
        request=context["request"],
        context=data,
    )


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
    return indexable[i]


@register.filter
def tabs(adminform: AdminForm) -> List[Fieldset]:
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

    def render(self, context: Dict[str, Any]) -> Union[str, SafeText]:
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
        extra_context: Optional[Dict] = None,
        *args,
        **kwargs,
    ):
        self.template_name = template_name
        self.nodelist = nodelist
        self.extra_context = extra_context or {}
        super().__init__(*args, **kwargs)

    def render(self, context: RequestContext) -> str:
        result = self.nodelist.render(context)

        ctx = {name: var.resolve(context) for name, var in self.extra_context.items()}
        ctx.update({"children": result})

        return render_to_string(
            self.template_name,
            request=context.request,
            context=ctx,
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
        else:
            raise TemplateSyntaxError(f"Unknown argument for {bits[0]} tag: {option}.")

        options[option] = value

    nodelist = parser.parse(("endcomponent",))
    template_name = bits[1][1:-1]
    extra_context = options.get("with", {})
    parser.next_token()

    return RenderComponentNode(template_name, nodelist, extra_context)


@register.filter
def add_css_class(field: Field, classes: Union[list, tuple]) -> Field:
    if type(classes) in (list, tuple):
        classes = " ".join(classes)

    if "class" in field.field.widget.attrs:
        field.field.widget.attrs["class"] += f" {classes}"
    else:
        field.field.widget.attrs["class"] = classes

    return field
