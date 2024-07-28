import datetime
from typing import Any, Dict, Optional, Union

from django.contrib.admin.templatetags.admin_list import (
    ResultList,
    _coerce_field_name,
    result_hidden_fields,
)
from django.contrib.admin.templatetags.admin_urls import add_preserved_filters
from django.contrib.admin.templatetags.base import InclusionAdminNode
from django.contrib.admin.utils import label_for_field, lookup_field
from django.contrib.admin.views.main import (
    ORDER_VAR,
    PAGE_VAR,
    ChangeList,
)
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.forms import Form
from django.http import HttpRequest
from django.template import Library
from django.template.base import Parser, Token
from django.template.loader import render_to_string
from django.urls import NoReverseMatch
from django.utils.html import format_html
from django.utils.safestring import SafeText, mark_safe
from django.utils.translation import gettext_lazy as _

from ..utils import (
    display_for_field,
    display_for_header,
    display_for_label,
    display_for_value,
)
from ..widgets import UnfoldBooleanWidget

register = Library()

LINK_CLASSES = [
    "truncate",
]

ROW_CLASSES = [
    "align-middle",
    "flex",
    "border-t",
    "border-gray-200",
    "font-normal",
    "gap-4",
    "min-w-0",
    "overflow-hidden",
    "px-3",
    "py-2",
    "text-left",
    "text-sm",
    "before:flex",
    "before:capitalize",
    "before:content-[attr(data-label)]",
    "before:items-center",
    "before:font-semibold",
    "before:mr-auto",
    "before:text-gray-900",
    "first:border-t-0",
    "dark:text-gray-300",
    "dark:before:text-gray-100",
    "lg:before:hidden",
    "lg:first:border-t",
    "lg:py-3",
    "lg:table-cell",
    "dark:border-gray-800",
]

CHECKBOX_CLASSES = [
    "action-checkbox",
    "align-middle",
    "flex",
    "items-center",
    "px-3",
    "py-2",
    "text-left",
    "text-sm",
    "before:block",
    "before:capitalize",
    "before:content-[attr(data-label)]",
    "before:font-semibold",
    "before:mr-auto",
    "before:text-gray-100",
    "lg:before:hidden",
    "lg:border-t",
    "lg:border-gray-200",
    "lg:table-cell",
    "dark:before:text-gray-100",
    "dark:lg:border-gray-800",
]


def result_headers(cl):
    """
    Generate the list column headers.
    """
    ordering_field_columns = cl.get_ordering_field_columns()
    for i, field_name in enumerate(cl.list_display):
        text, attr = label_for_field(
            field_name, cl.model, model_admin=cl.model_admin, return_attr=True
        )
        is_field_sortable = cl.sortable_by is None or field_name in cl.sortable_by
        if attr:
            field_name = _coerce_field_name(field_name, i)
            # Potentially not sortable

            # if the field is the action checkbox: no sorting and special class
            if field_name == "action_checkbox":
                yield {
                    "text": UnfoldBooleanWidget(
                        {
                            "id": "action-toggle",
                            "aria-label": _(
                                "Select all objects on this page for an action"
                            ),
                        }
                    ).render("action-toggle", False),
                    "class_attrib": mark_safe("action-checkbox-column"),
                    "sortable": False,
                }
                continue

            admin_order_field = getattr(attr, "admin_order_field", None)
            # Set ordering for attr that is a property, if defined.
            if isinstance(attr, property) and hasattr(attr, "fget"):
                admin_order_field = getattr(attr.fget, "admin_order_field", None)
            if not admin_order_field:
                is_field_sortable = False

        if not is_field_sortable:
            # Not sortable
            yield {
                "text": text,
                "class_attrib": format_html("column-{}", field_name),
                "sortable": False,
            }
            continue

        # OK, it is sortable if we got this far
        th_classes = ["sortable", f"column-{field_name}"]
        order_type = ""
        new_order_type = "asc"
        sort_priority = 0
        # Is it currently being sorted on?
        is_sorted = i in ordering_field_columns
        if is_sorted:
            order_type = ordering_field_columns.get(i).lower()
            sort_priority = list(ordering_field_columns).index(i) + 1
            th_classes.append(f"sorted {order_type}ending")
            new_order_type = {"asc": "desc", "desc": "asc"}[order_type]

        # build new ordering param
        o_list_primary = []  # URL for making this field the primary sort
        o_list_remove = []  # URL for removing this field from sort
        o_list_toggle = []  # URL for toggling order type for this field

        def make_qs_param(t, n):
            return ("-" if t == "desc" else "") + str(n)

        for j, ot in ordering_field_columns.items():
            if j == i:  # Same column
                param = make_qs_param(new_order_type, j)
                # We want clicking on this header to bring the ordering to the
                # front
                o_list_primary.insert(0, param)
                o_list_toggle.append(param)
                # o_list_remove - omit
            else:
                param = make_qs_param(ot, j)
                o_list_primary.append(param)
                o_list_toggle.append(param)
                o_list_remove.append(param)

        if i not in ordering_field_columns:
            o_list_primary.insert(0, make_qs_param(new_order_type, i))

        yield {
            "text": text,
            "sortable": True,
            "sorted": is_sorted,
            "ascending": order_type == "asc",
            "sort_priority": sort_priority,
            "url_primary": cl.get_query_string({ORDER_VAR: ".".join(o_list_primary)}),
            "url_remove": cl.get_query_string({ORDER_VAR: ".".join(o_list_remove)}),
            "url_toggle": cl.get_query_string({ORDER_VAR: ".".join(o_list_toggle)}),
            "class_attrib": format_html("{}", " ".join(th_classes))
            if th_classes
            else "",
        }


def items_for_result(cl: ChangeList, result: HttpRequest, form) -> SafeText:
    """
    Generate the actual list of data.
    """

    def link_in_col(is_first: bool, field_name: str, cl: ChangeList) -> bool:
        if cl.list_display_links is None:
            return False
        if is_first and not cl.list_display_links:
            return True
        return field_name in cl.list_display_links

    first = True
    pk = cl.lookup_opts.pk.attname
    headers = list(result_headers(cl))

    for field_index, field_name in enumerate(cl.list_display):
        empty_value_display = cl.model_admin.get_empty_value_display()
        row_classes = [
            f"field-{_coerce_field_name(field_name, field_index)}",
            *ROW_CLASSES,
        ]

        try:
            f, attr, value = lookup_field(field_name, result, cl.model_admin)
        except ObjectDoesNotExist:
            result_repr = empty_value_display
        else:
            empty_value_display = getattr(
                attr, "empty_value_display", empty_value_display
            )
            if f is None or f.auto_created:
                if field_name == "action_checkbox":
                    row_classes = CHECKBOX_CLASSES
                boolean = getattr(attr, "boolean", False)
                label = getattr(attr, "label", False)
                header = getattr(attr, "header", False)

                if label:
                    result_repr = display_for_label(value, empty_value_display, label)
                elif header:
                    result_repr = display_for_header(value, empty_value_display)
                else:
                    result_repr = display_for_value(value, empty_value_display, boolean)

                if isinstance(value, (datetime.date, datetime.time)):
                    row_classes.append("nowrap")
            else:
                if isinstance(f.remote_field, models.ManyToOneRel):
                    field_val = getattr(result, f.name)
                    if field_val is None:
                        result_repr = empty_value_display
                    else:
                        result_repr = field_val
                else:
                    result_repr = display_for_field(value, f, empty_value_display)
                if isinstance(
                    f, (models.DateField, models.TimeField, models.ForeignKey)
                ):
                    row_classes.append("nowrap")

        # If list_display_links not defined, add the link tag to the first field

        if link_in_col(first, field_name, cl):
            table_tag = "th" if first else "td"
            first = False

            # Display link to the result's change_view if the url exists, else
            # display just the result's representation.
            try:
                url = cl.url_for_result(result)
            except NoReverseMatch:
                link_or_text = result_repr
            else:
                url = add_preserved_filters(
                    {"preserved_filters": cl.preserved_filters, "opts": cl.opts}, url
                )
                # Convert the pk to something that can be used in Javascript.
                # Problem cases are non-ASCII strings.
                if cl.to_field:
                    attr = str(cl.to_field)
                else:
                    attr = pk
                value = result.serializable_value(attr)
                link_or_text = format_html(
                    '<a href="{}" class="{}" {}>{}</a>',
                    url,
                    " ".join(LINK_CLASSES),
                    format_html(' data-popup-opener="{}"', value)
                    if cl.is_popup
                    else "",
                    result_repr,
                )
            row_class = mark_safe(f' class="{" ".join(row_classes)}"')
            yield format_html(
                '<{}{} data-label="{}">{}</{}>',
                table_tag,
                row_class,
                headers[field_index]["text"],
                link_or_text,
                table_tag,
            )
        else:
            # By default the fields come from ModelAdmin.list_editable, but if we pull
            # the fields out of the form instead of list_editable custom admins
            # can provide fields on a per request basis
            if (
                form
                and field_name in form.fields
                and not (
                    field_name == cl.model._meta.pk.name
                    and form[cl.model._meta.pk.name].is_hidden
                )
            ):
                bf = form[field_name]
                result_repr = mark_safe(
                    str(bf)
                    + render_to_string(
                        "unfold/helpers/form_errors.html", {"errors": bf.errors}
                    )
                )

                if bf.errors:
                    row_classes += ["group", "errors"]

            row_class = mark_safe(f' class="{" ".join(row_classes)}"')

            if field_index != 0:
                yield format_html(
                    '<td{} data-label="{}">{}</td>',
                    row_class,
                    headers[field_index]["text"],
                    result_repr,
                )
            else:
                yield format_html(
                    '<td{} data-label="{}">{}</td>',
                    row_class,
                    _("Select record"),
                    result_repr,
                )

    if form and not form[cl.model._meta.pk.name].is_hidden:
        yield format_html("<td>{}</td>", form[cl.model._meta.pk.name])


class UnfoldResultList(ResultList):
    def __init__(
        self, instance_pk: Union[int, str], form: Optional[Form], *items: Any
    ) -> None:
        self.instance_pk = instance_pk
        super().__init__(form, *items)


def results(cl: ChangeList):
    if cl.formset:
        for res, form in zip(cl.result_list, cl.formset.forms):
            pk = cl.lookup_opts.pk.attname
            pk_value = getattr(res, pk)
            yield UnfoldResultList(pk_value, form, items_for_result(cl, res, form))
    else:
        for res in cl.result_list:
            pk = cl.lookup_opts.pk.attname
            pk_value = getattr(res, pk)
            yield UnfoldResultList(pk_value, None, items_for_result(cl, res, None))


def result_list(context: Dict[str, Any], cl: ChangeList) -> Dict[str, Any]:
    """
    Display the headers and data list together.
    """
    headers = list(result_headers(cl))
    num_sorted_fields = 0

    for h in headers:
        if h["sortable"] and h["sorted"]:
            num_sorted_fields += 1

    return {
        "cl": cl,
        "result_hidden_fields": list(result_hidden_fields(cl)),
        "result_headers": headers,
        "num_sorted_fields": num_sorted_fields,
        "results": list(results(cl)),
        "actions_row": context.get("actions_row"),
    }


@register.tag(name="unfold_result_list")
def result_list_tag(parser: Parser, token: Token) -> InclusionAdminNode:
    return InclusionAdminNode(
        parser,
        token,
        func=result_list,
        template_name="change_list_results.html",
    )


@register.simple_tag
def paginator_number(cl: ChangeList, i: Union[str, int]) -> Union[str, SafeText]:
    """
    Generate an individual page index link in a paginated list.
    """
    if i == cl.paginator.ELLIPSIS:
        return render_to_string(
            "unfold/helpers/pagination_ellipsis.html",
            {"ellipsis": cl.paginator.ELLIPSIS},
        )
    elif i == cl.page_num:
        return render_to_string(
            "unfold/helpers/pagination_current_item.html", {"number": i}
        )
    else:
        return format_html(
            '<a href="{}"{}>{}</a> ',
            cl.get_query_string({PAGE_VAR: i}),
            mark_safe(' class="end"' if i == cl.paginator.num_pages else ""),
            i,
        )
