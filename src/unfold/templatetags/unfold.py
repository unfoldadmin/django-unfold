from django.template import Library, Node, TemplateSyntaxError
from django.template.loader import render_to_string

register = Library()


@register.simple_tag(name="tab_list", takes_context=True)
def tab_list(context, opts):
    tabs = None

    for tab in context.get("tab_list"):
        if str(opts) in tab["models"]:
            tabs = tab["items"]
            break

    return render_to_string(
        "unfold/helpers/tab_list.html",
        request=context.request,
        context={
            "tab_list": tabs,
            "actions_list": context.get("actions_list"),
            "is_popup": context.get("is_popup"),
        },
    )


@register.filter
def class_name(value):
    return value.__class__.__name__


@register.filter
def index(indexable, i):
    return indexable[i]


@register.tag(name="capture")
def do_capture(parser, token):
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


class CaptureNode(Node):
    def __init__(self, nodelist, varname, silent):
        self.nodelist = nodelist
        self.varname = varname
        self.silent = silent

    def render(self, context):
        output = self.nodelist.render(context)
        context[self.varname] = output
        if self.silent:
            return ""
        else:
            return output
