import importlib
import re
from http import HTTPStatus

import pytest
from django import forms
from django.contrib.admin import options
from django.contrib.admin.helpers import AdminField
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator
from django.forms import Form
from django.template import Context, Template, TemplateSyntaxError
from django.template.context import RequestContext
from django.urls import reverse
from example.admin import ProjectDataset, UserAdmin
from example.models import User

from unfold.components import BaseComponent, register_component
from unfold.enums import ActionVariant
from unfold.fields import UnfoldAdminField, UnfoldAdminReadonlyField
from unfold.sites import UnfoldAdminSite
from unfold.views import ChangeList


@pytest.mark.django_db
def test_tags_action_list(user_factory, rf):
    user = user_factory(username="sample@example.com")
    request = rf.get("/")
    request.user = user

    response = Template("{% load unfold %} {% action_list %}").render(
        RequestContext(
            request,
            {
                "nav_global": "global action",
            },
        )
    )

    assert "global action" in response


@pytest.mark.django_db
def test_tags_tab_list_page_id(user_factory, rf):
    user = user_factory(username="sample@example.com")
    request = rf.get("/")
    request.user = user

    response = Template("{% load unfold %} {% tab_list 'sample' %}").render(
        RequestContext(
            request,
            {
                "tab_list": [
                    {
                        "page": "sample",
                        "items": [
                            {
                                "title": "tab 1",
                                "link": "https://example.com",
                                "has_permission": True,
                            },
                        ],
                    }
                ],
            },
        )
    )
    assert "tab 1" in response


@pytest.mark.django_db
def test_tags_tab_list_wrong_page_id(user_factory, rf):
    user = user_factory(username="sample@example.com")
    request = rf.get("/")
    request.user = user

    response = Template("{% load unfold %} {% tab_list 'sample' %}").render(
        RequestContext(
            request,
            {
                "tab_list": [
                    {
                        "page": "wrong_page_id",
                        "items": [
                            {
                                "title": "tab 1",
                                "link": "https://example.com",
                                "has_permission": True,
                            },
                        ],
                    }
                ],
            },
        )
    )

    assert response.replace("\n", "").strip() == ""


@pytest.mark.django_db
def test_tags_tab_list_no_models(user_factory, rf):
    user = user_factory(username="sample@example.com")
    request = rf.get("/")
    request.user = user

    response = Template("{% load unfold %} {% tab_list 'changelist' %}").render(
        RequestContext(
            request,
            {
                "tab_list": [
                    {
                        "items": [
                            {
                                "title": "tab 1",
                                "link": "https://example.com",
                                "has_permission": True,
                            },
                        ],
                    }
                ],
            },
        )
    )

    assert response.replace("\n", "").strip() == ""


@pytest.mark.django_db
def test_tags_tab_list_changelist(user_factory, rf):
    user = user_factory(username="sample@example.com")
    request = rf.get("/")
    request.user = user

    response = Template("{% load unfold %} {% tab_list 'changelist' opts %}").render(
        RequestContext(
            request,
            {
                "opts": get_user_model()._meta,
                "tab_list": [
                    {
                        "page": "changelist",
                        "models": ["example.user"],
                        "items": [
                            {
                                "title": "tab 1",
                                "link": "https://example.com",
                                "has_permission": True,
                            },
                        ],
                    }
                ],
            },
        )
    )
    assert "tab 1" in response


@pytest.mark.django_db
def test_tags_tab_list_changeform(user_factory, rf):
    user = user_factory(username="sample@example.com")
    request = rf.get("/")
    request.user = user

    response = Template("{% load unfold %} {% tab_list 'changeform' opts %}").render(
        RequestContext(
            request,
            {
                "opts": get_user_model()._meta,
                "tab_list": [
                    {
                        "page": "changeform",
                        "models": [
                            {
                                "name": "example.user",
                                "detail": True,
                            }
                        ],
                        "items": [
                            {
                                "title": "tab 1",
                                "link": "https://example.com",
                                "has_permission": True,
                            },
                        ],
                    }
                ],
            },
        )
    )
    assert "tab 1" in response


@pytest.mark.django_db
def test_tags_tab_list_changeform_inlines(user_factory, rf):
    user = user_factory(username="sample@example.com", is_superuser=True, is_staff=True)
    request = rf.get("/")
    request.user = user

    user_admin = UserAdmin(User, UnfoldAdminSite())
    changeform_view = user_admin.changeform_view(
        request=request, object_id=str(user.pk)
    )

    assert "General" in changeform_view.render().content.decode()
    assert "User-tag relationships" in changeform_view.render().content.decode()
    assert "Projects" in changeform_view.render().content.decode()


@pytest.mark.django_db
def test_tags_render_section(user_factory, rf, tag_factory):
    user = user_factory(username="sample@example.com")
    user.tags.add(tag_factory(name="sample tag title"))

    response = Template(
        "{% load unfold %}{% render_section section_class instance %}"
    ).render(
        RequestContext(
            rf.get("/"),
            {
                "section_class": "example.admin.TagSection",
                "instance": user,
            },
        )
    )
    assert "sample tag title" in response


@pytest.mark.django_db
def test_tags_class_name():
    response = Template("{% load unfold %}{{ value|class_name }}").render(
        Context({"value": "example"})
    )

    assert "str" in response


@pytest.mark.django_db
def test_tags_is_list():
    response = Template(
        "{% load unfold %}{% if value|is_list %}is_list{% endif %}"
    ).render(Context({"value": ["aaa", "bbb"]}))

    assert "is_list" in response


@pytest.mark.django_db
def test_tags_has_nav_item_active():
    response = Template(
        "{% load unfold %}{% has_nav_item_active items as is_active %} {% if is_active %}active item{% else %}inactive{% endif %}"
    ).render(
        Context(
            {
                "items": [
                    {
                        "title": "sample tag title",
                        "link": "https://example.com",
                        "active": True,
                    },
                ],
            },
        )
    )

    assert "active item" in response

    response = Template(
        "{% load unfold %}{% has_nav_item_active items as is_active %} {% if is_active %}active item{% else %}inactive{% endif %}"
    ).render(
        Context(
            {
                "items": [
                    {
                        "title": "sample tag title",
                        "link": "https://example.com",
                    },
                ],
            },
        )
    )

    assert "inactive" in response


@pytest.mark.django_db
def test_tags_has_active_item():
    response = Template(
        "{% load unfold %}{% if items|has_active_item %}active item{% else %}inactive{% endif %}"
    ).render(
        Context(
            {
                "items": [
                    {
                        "title": "sample tag title",
                        "link": "https://example.com",
                        "active": True,
                    },
                ],
            },
        )
    )

    assert "active item" in response

    response = Template(
        "{% load unfold %}{% if items|has_active_item %}active item{% else %}inactive{% endif %}"
    ).render(
        Context(
            {
                "items": [
                    {
                        "title": "sample tag title",
                        "link": "https://example.com",
                    },
                ],
            },
        )
    )

    assert "inactive" in response


@pytest.mark.django_db
def test_tags_index():
    response = Template('{% load unfold %}{{ value|index:"sample" }}').render(
        Context(
            {
                "value": {
                    "sample": "example",
                },
            },
        )
    )

    assert "example" in response


@pytest.mark.django_db
def test_tags_tabs(rf, user_factory):
    user = user_factory(username="sample@example.com", is_superuser=True, is_staff=True)
    request = rf.get("/")
    request.user = user

    user_admin = UserAdmin(User, UnfoldAdminSite())
    changeform_view = user_admin.changeform_view(
        request=request, object_id=str(user.pk)
    )
    context_data = (
        changeform_view.context_data
        if hasattr(changeform_view, "context_data")
        else changeform_view.context
    )

    response = Template(
        "{% load unfold %}{% for tab in adminform|tabs %}{{ tab.name }} {% endfor %}"
    ).render(
        Context(
            {
                "adminform": context_data["adminform"],
            },
        )
    )

    assert "Personal info" in response
    assert "Permissions" in response


@pytest.mark.django_db
def test_tags_do_component():
    response = Template(
        '{% load unfold %} {% component "unfold/components/button.html" include_context %}Sample button title{% endcomponent %}'
    ).render(Context({}))

    assert "Sample button title" in response


@pytest.mark.django_db
def test_tags_do_component_class():
    @register_component
    class ExampleComponent(BaseComponent):
        def get_context_data(self, **kwargs):
            context = super().get_context_data(**kwargs)
            context.update(
                {
                    "children": "Example component data",
                }
            )
            return context

    response = Template(
        '{% load unfold %} {% component "unfold/components/button.html" with component_class="ExampleComponent" %}{% endcomponent %}'
    ).render(Context({}))

    assert "Example component data" in response


@pytest.mark.django_db
def test_tags_do_component_exceptions():
    with pytest.raises(
        TemplateSyntaxError,
        match="component tag takes at least one argument: the name of the template to be included.",
    ):
        Template(
            "{% load unfold %} {% component %}Sample button title{% endcomponent %}"
        ).render(Context({}))

    with pytest.raises(
        TemplateSyntaxError, match="option was specified more than once."
    ):
        Template(
            "{% load unfold %} {% component 'unfold/components/button.html' include_context include_context %}Sample button title{% endcomponent %}"
        ).render(Context({}))

    with pytest.raises(
        TemplateSyntaxError, match="tag needs at least one keyword argument."
    ):
        Template(
            "{% load unfold %} {% component 'unfold/components/button.html' with %}Sample button title{% endcomponent %}"
        ).render(Context({}))

    with pytest.raises(TemplateSyntaxError, match="Unknown argument for"):
        Template(
            "{% load unfold %} {% component 'unfold/components/button.html' aaa %}Sample button title{% endcomponent %}"
        ).render(Context({}))


@pytest.mark.django_db
def test_tags_add_css_class():
    class SampleForm(Form):
        example = forms.CharField()
        sample = forms.CharField(
            widget=forms.TextInput(
                attrs={
                    "class": "sample-css-class",
                }
            )
        )

    form = SampleForm()

    response = Template("{% load unfold %} {{ field|add_css_class:classes }}").render(
        Context(
            {
                "field": form["example"],
                "classes": ["example-css-class"],
            }
        )
    )

    assert "example-css-class" in response

    response = Template("{% load unfold %} {{ field|add_css_class:classes }}").render(
        Context(
            {
                "field": form["sample"],
                "classes": ["example-css-class"],
            }
        )
    )

    assert "example-css-class" in response
    assert "sample-css-class" in response


@pytest.mark.django_db
def test_tags_preserve_changelist_filters(rf, user_factory):
    user = user_factory(username="sample@example.com", is_superuser=True, is_staff=True)
    request = rf.get("/")
    request.user = user

    user_admin = UserAdmin(User, UnfoldAdminSite())
    changelist_view = user_admin.changelist_view(request=request)
    context_data = (
        changelist_view.context_data
        if hasattr(changelist_view, "context_data")
        else changelist_view.context
    )

    response = Template("{% load unfold %} {% preserve_filters %}").render(
        RequestContext(
            rf.get("/?is_staff__exact=1"),
            {
                "cl": context_data["cl"],
            },
        )
    )

    assert '<input type="hidden" name="is_staff__exact" value="1">' in response

    response = Template("{% load unfold %} {% preserve_filters %}").render(
        RequestContext(
            rf.get("/?is_staff__exact=1"),
            {
                "cl": None,
            },
        )
    )

    assert response.replace("\n", "").strip() == ""


@pytest.mark.django_db
def test_tags_element_classes(rf):
    response = Template("{% load unfold %} {% element_classes 'example' %}").render(
        RequestContext(
            rf.get("/"),
            {
                "element_classes": {
                    "example": "example-class",
                }
            },
        )
    )
    assert "example-class" in response

    response = Template("{% load unfold %} {% element_classes 'example' %}").render(
        RequestContext(
            rf.get("/"),
            {
                "element_classes": {
                    "example": ["example-class", "sample-class"],
                }
            },
        )
    )
    assert "example-class" in response
    assert "sample-class" in response


@pytest.mark.django_db
def test_tags_fieldset_rows_classes(rf, user_factory):
    user = user_factory(username="sample@example.com", is_superuser=True, is_staff=True)
    request = rf.get("/")
    request.user = user

    user_admin = UserAdmin(User, UnfoldAdminSite())
    changeform_view = user_admin.changeform_view(
        request=request, object_id=str(user.pk)
    )

    assert "form-rows" in changeform_view.render().content.decode()


@pytest.mark.django_db
def test_tags_fieldset_row_classes(rf, user_factory):
    user = user_factory(username="sample@example.com", is_superuser=True, is_staff=True)
    request = rf.get("/")
    request.user = user

    user_admin = UserAdmin(User, UnfoldAdminSite())
    changeform_view = user_admin.changeform_view(
        request=request, object_id=str(user.pk)
    )

    assert "form-row" in changeform_view.render().content.decode()


@pytest.mark.django_db
def test_tags_fieldset_line_classes(rf, user_factory):
    user = user_factory(username="sample@example.com", is_superuser=True, is_staff=True)
    request = rf.get("/")
    request.user = user

    user_admin = UserAdmin(User, UnfoldAdminSite())
    changeform_view = user_admin.changeform_view(
        request=request, object_id=str(user.pk)
    )

    assert "field-line" in changeform_view.render().content.decode()


@pytest.mark.django_db
def test_tags_action_item_classes(rf):
    response = Template("{% load unfold %} {% action_item_classes action %}").render(
        RequestContext(
            rf.get("/"),
            {
                "action": {
                    "action_name": "action_name",
                    "method": lambda: False,
                    "description": "action_description",
                    "path": "action_path",
                    "attrs": {},
                    "icon": None,
                    "variant": ActionVariant.DEFAULT,
                },
            },
        )
    )

    assert "border-base-200" in response


@pytest.mark.django_db
def test_tags_action_item_classes_existing_variant_as_string(rf):
    response = Template("{% load unfold %} {% action_item_classes action %}").render(
        RequestContext(
            rf.get("/"),
            {
                "action": {
                    "action_name": "action_name",
                    "method": lambda: False,
                    "description": "action_description",
                    "path": "action_path",
                    "attrs": {},
                    "icon": None,
                    "variant": "primary",
                },
            },
        )
    )

    assert "border-primary-700" in response


@pytest.mark.django_db
def test_tags_action_item_classes_non_existing_variant(rf):
    response = Template("{% load unfold %} {% action_item_classes action %}").render(
        RequestContext(
            rf.get("/"),
            {
                "action": {
                    "action_name": "action_name",
                    "method": lambda: False,
                    "description": "action_description",
                    "path": "action_path",
                    "attrs": {},
                    "icon": None,
                    "variant": "non_existing_variant",
                },
            },
        )
    )

    assert "border-base-200" in response


@pytest.mark.django_db
def test_tags_changeform_data(rf, user_factory):
    user = user_factory(username="sample@example.com", is_superuser=True, is_staff=True)
    request = rf.get("/")
    request.user = user

    user_admin = UserAdmin(User, UnfoldAdminSite())
    changeform_view = user_admin.changeform_view(
        request=request, object_id=str(user.pk)
    )
    context_data = (
        changeform_view.context_data
        if hasattr(changeform_view, "context_data")
        else changeform_view.context
    )

    response = Template("{% load unfold %} {{ adminform|changeform_data }}").render(
        RequestContext(
            rf.get("/"),
            {
                "adminform": context_data["adminform"],
            },
        )
    )
    assert '"username": null' in response


@pytest.mark.django_db
def test_tags_changeform_condition_field(rf):
    form = UserAdmin(User, UnfoldAdminSite()).get_form(None)()
    admin_field = AdminField(form, "username", False)

    response = Template(
        "{% load unfold %} {% with admin_field|changeform_condition as field %}{{ field.field }}{% endwith %}"
    ).render(
        RequestContext(
            rf.get("/"),
            {
                "admin_field": admin_field,
            },
        )
    )
    assert 'x-model.fill="username"' in response


@pytest.mark.django_db
def test_tags_changeform_condition_field_datetime(rf, user_factory):
    user = user_factory(username="sample@example.com")
    form = UserAdmin(User, UnfoldAdminSite()).get_form(
        rf.get("/"), obj=user, change=True
    )()
    admin_field = UnfoldAdminField(form, "date_joined", False)

    response = Template(
        "{% load unfold %} {% with admin_field|changeform_condition as field %}{{ field.field }}{% endwith %}"
    ).render(
        RequestContext(
            rf.get("/"),
            {
                "admin_field": admin_field,
            },
        )
    )
    assert 'x-model.fill="date_joined_0"' in response
    assert 'x-model.fill="date_joined_1"' in response


@pytest.mark.django_db
def test_tags_changeform_condition_field_fk(rf, user_factory):
    user = user_factory(username="sample@example.com")
    form = UserAdmin(User, UnfoldAdminSite()).get_form(
        rf.get("/"), obj=user, change=True
    )()
    admin_field = UnfoldAdminField(form, "tags", False)

    response = Template(
        "{% load unfold %} {% with admin_field|changeform_condition as field %}{{ field.field }}{% endwith %}"
    ).render(
        RequestContext(
            rf.get("/"),
            {
                "admin_field": admin_field,
            },
        )
    )

    assert 'x-model.fill="tags"' in response


@pytest.mark.django_db
def test_tags_changeform_condition_field_select2(rf, user_factory):
    user = user_factory(username="sample@example.com")
    form = UserAdmin(User, UnfoldAdminSite()).get_form(
        rf.get("/"), obj=user, change=True
    )()
    admin_field = UnfoldAdminField(form, "status", False)

    response = Template(
        "{% load unfold %} {% with admin_field|changeform_condition as field %}{{ field.field }}{% endwith %}"
    ).render(
        RequestContext(
            rf.get("/"),
            {
                "admin_field": admin_field,
            },
        )
    )

    assert 'x-model.fill="status"' in response


@pytest.mark.django_db
def test_tags_changeform_condition_readonly_field(rf, user_factory):
    user = user_factory(username="sample@example.com")
    user_admin = UserAdmin(User, UnfoldAdminSite())
    form = user_admin.get_form(rf.get("/"), obj=user, change=True)()
    admin_field = UnfoldAdminReadonlyField(
        form, "custom_readonly_field", False, user_admin
    )
    response = Template(
        "{% load unfold %} {% with admin_field|changeform_condition as field %}{{ field.field }}{% endwith %}"
    ).render(
        RequestContext(
            rf.get("/"),
            {
                "admin_field": admin_field,
            },
        )
    )

    assert "Custom readonly field" in response
    assert "readonly" in response


@pytest.mark.django_db
def test_tags_infinite_paginator_url(rf, user_factory):
    user = user_factory(username="sample@example.com", is_superuser=True, is_staff=True)
    request = rf.get("/")
    request.user = user

    user_admin = UserAdmin(User, UnfoldAdminSite())
    changelist_view = user_admin.changelist_view(request=request)
    context_data = (
        changelist_view.context_data
        if hasattr(changelist_view, "context_data")
        else changelist_view.context
    )

    response = Template(
        "{% load unfold %} {% infinite_paginator_url cl cl.page_num %}"
    ).render(
        RequestContext(
            rf.get("/"),
            {
                "cl": context_data["cl"],
            },
        )
    )
    assert "?p=1" in response


@pytest.mark.django_db
def test_tags_elided_page_range(rf):
    response = Template(
        """
        {% load unfold %}
        {% elided_page_range paginator page as elided_page_range %}
        {% for i in elided_page_range %}{{ i }}{% endfor %}
        """
    ).render(
        RequestContext(
            rf.get("/"),
            {
                "paginator": Paginator(list(range(100)), 10),
                "page": 1,
            },
        )
    )
    assert "12345678910" in response


@pytest.mark.django_db
def test_tags_querystring_params(rf):
    response = Template(
        "{% load unfold %} {% querystring_params 'example1' 'value1' %}"
    ).render(RequestContext(rf.get("/?example2=value2&example1=value3"), {}))

    assert "example1=value1" in response


@pytest.mark.django_db
def test_tags_unfold_querystring(rf):
    request = rf.get("/?123=456")
    response = Template(
        "{% load unfold %} {% unfold_querystring sample='example' item_to_remove=None iterate=list_var %}"
    ).render(
        RequestContext(
            request,
            {
                "list_var": ["aaa", "bbb"],
            },
        )
    )
    assert "?123=456&amp;sample=example&amp;iterate=aaa&amp;iterate=bbb" in response

    with pytest.raises(
        TemplateSyntaxError,
        match="querystring requires mappings for positional arguments",
    ):
        Template("{% load unfold %} {% unfold_querystring '' %}").render(
            RequestContext(rf.get("/"), {})
        )

    with pytest.raises(
        TemplateSyntaxError, match="querystring requires strings for mapping keys"
    ):
        Template("{% load unfold %} {% unfold_querystring wrong_param %}").render(
            RequestContext(
                rf.get("/"),
                {
                    "wrong_param": {
                        111: "abc",
                    },
                },
            )
        )


@pytest.mark.django_db
def test_tags_header_title(rf, user_factory, user_model_admin):
    user = user_factory(username="sample@example.com")
    request = rf.get("/")
    request.user = user

    response = Template("{% load unfold %} {% header_title %}").render(
        RequestContext(
            request,
            {},
        )
    )
    assert "Welcome sample@example.com" in response

    response = Template("{% load unfold %} {% header_title %}").render(
        RequestContext(
            rf.get("/"),
            {
                "content_title": "Custom content title",
            },
        )
    )
    assert "Custom content title" in response

    response = Template("{% load unfold %} {% header_title %}").render(
        RequestContext(
            rf.get("/"),
            {
                "model_admin": user_model_admin,
            },
        )
    )

    assert "/admin/example/user" in response
    assert "Users" in response

    response = Template("{% load unfold %} {% header_title %}").render(
        RequestContext(
            rf.get("/"),
            {
                "opts": get_user_model()._meta,
            },
        )
    )

    assert "/admin/example/user" in response
    assert "Users" in response

    response = Template("{% load unfold %} {% header_title %}").render(
        RequestContext(
            rf.get("/"),
            {
                "opts": get_user_model()._meta,
                "original": user,
            },
        )
    )

    assert "/admin/example/user" in response
    assert "Users" in response
    assert f"/admin/example/user/{user.pk}" in response
    assert user.username.lower() in response.lower()

    response = Template("{% load unfold %} {% header_title %}").render(
        RequestContext(
            rf.get("/"),
            {
                "opts": get_user_model()._meta,
                "object": user,
            },
        )
    )

    assert "/admin/example/user" in response
    assert "Users" in response
    assert f"/admin/example/user/{user.pk}" in response
    assert user.username.lower() in response.lower()

    response = Template("{% load unfold %} {% header_title %}").render(
        RequestContext(
            rf.get("/"),
            {
                "object": user,
            },
        )
    )

    assert "/admin/example/user" in response
    assert "Users" in response
    assert f"/admin/example/user/{user.pk}" in response
    assert user.username.lower() in response.lower()


@pytest.mark.django_db
def test_tags_admin_object_app_url(rf, user_factory):
    user = user_factory()
    response = Template(
        "{% load unfold %} {% admin_object_app_url object 'changelist' %}"
    ).render(
        RequestContext(
            rf.get("/"),
            {
                "object": user,
            },
        )
    )
    assert "admin:example_user_changelist" in response


def test_tags_do_capture():
    content = Template(
        "{% load unfold %} {% capture as value %}Hello world!{% endcapture %}"
    ).render(Context({}))

    assert "Hello world!" in content


def test_tags_do_capture_with_silent():
    content = Template(
        "{% load unfold %} {% capture as value silent %}Hello world!{% endcapture %} Value: {{ value }}"
    ).render(Context({}))

    assert "Value: Hello world!" in content


def test_tags_do_capture_too_many_params():
    with pytest.raises(
        TemplateSyntaxError, match="Too many arguments for 'capture' tag."
    ):
        Template(
            "{% load unfold %} {% capture as value silent TOO_MANY_PARAMS %}Hello world!{% endcapture %}"
        ).render(Context({}))


def test_tags_do_capture_missing_as():
    with pytest.raises(
        TemplateSyntaxError, match="'as' is required for 'capture' tag."
    ):
        Template(
            "{% load unfold %} {% capture WRONG_PARAM value silent %}Hello world!{% endcapture %}"
        ).render(Context({}))


def test_tags_do_capture_missing_silent():
    with pytest.raises(
        TemplateSyntaxError, match="'silent' is required for 'capture' tag."
    ):
        Template(
            "{% load unfold %} {% capture as value WRONG_PARAM %}Hello world!{% endcapture %}"
        ).render(Context({}))


@pytest.mark.django_db
def test_tags_tabs_errors_count(admin_client, user_factory):
    user = user_factory(username="sample@example.com")
    response = admin_client.post(
        reverse("admin:example_user_change", args=[user.pk]),
        {
            "username": "",
        },
    )
    assert "Please correct the errors below." in response.content.decode()
    assert "x-data=\"{ activeFieldsetTab: 'permissions'}" in response.content.decode()
    assert 'data-testid="error-count"' in response.content.decode()


@pytest.mark.django_db
def test_tags_tabs_active(rf, user_factory):
    user = user_factory(username="sample@example.com", is_superuser=True, is_staff=True)
    request = rf.get("/")
    request.user = user

    user_admin = UserAdmin(User, UnfoldAdminSite())
    changeform_view = user_admin.changeform_view(
        request=request, object_id=str(user.pk)
    )
    context_data = (
        changeform_view.context_data
        if hasattr(changeform_view, "context_data")
        else changeform_view.context
    )

    response = Template(
        "{% load unfold %}{% with tabs=adminform|tabs %}{{ tabs|tabs_active }} {% endwith %}"
    ).render(
        Context(
            {
                "adminform": context_data["adminform"],
            },
        )
    )

    assert "personal-info" in response


@pytest.mark.django_db
def test_tags_tabs_primary_active(rf, user_factory, monkeypatch):
    user = user_factory(username="sample@example.com", is_superuser=True, is_staff=True)
    request = rf.get("/")
    request.user = user

    user_admin = UserAdmin(User, UnfoldAdminSite())
    changeform_view = user_admin.changeform_view(
        request=request, object_id=str(user.pk)
    )
    context_data = (
        changeform_view.context_data
        if hasattr(changeform_view, "context_data")
        else changeform_view.context
    )

    formsets = context_data["inline_admin_formsets"]

    response = Template(
        "{% load unfold %}{% tabs_primary_active inline_admin_formsets %}"
    ).render(
        Context(
            {
                "inline_admin_formsets": formsets,
            },
        )
    )
    assert "general" in response

    class ErrorsProperty:
        def __get__(self, obj, objtype=None):
            return [{"example_field": ["Example error."]}]

    monkeypatch.setattr(
        type(formsets[0].formset), "errors", property(ErrorsProperty().__get__)
    )

    response = Template(
        "{% load unfold %}{% tabs_primary_active inline_admin_formsets %}"
    ).render(
        Context(
            {
                "inline_admin_formsets": formsets,
            },
        )
    )
    assert "user_tags" in response


@pytest.mark.django_db
def test_tags_tabs_primary_errors_count(rf, user_factory, monkeypatch):
    user = user_factory(username="sample@example.com", is_superuser=True, is_staff=True)
    request = rf.get("/")
    request.user = user

    user_admin = UserAdmin(User, UnfoldAdminSite())
    changeform_view = user_admin.changeform_view(
        request=request, object_id=str(user.pk)
    )
    context_data = (
        changeform_view.context_data
        if hasattr(changeform_view, "context_data")
        else changeform_view.context
    )

    formsets = context_data["inline_admin_formsets"]

    # Errors in the inline which is displayed as tab
    class ErrorsPropertyTab:
        @property
        def errors(self):
            return [
                {"example_field": ["Example error."]},
                {"example_field2": ["Example error 2."]},
            ]

    original_errors_property_0 = getattr(formsets[0].formset.__class__, "errors", None)
    monkeypatch.setattr(
        formsets[0].formset.__class__, "errors", ErrorsPropertyTab.errors
    )

    response = Template("{% load unfold %}{% tab_list 'changeform' opts %}").render(
        RequestContext(
            request,
            {
                "opts": get_user_model()._meta,
                "adminform": context_data["adminform"],
                "inline_admin_formsets": formsets,
            },
        )
    )

    assert "2" in response

    # Restore previous patch for next usage
    if original_errors_property_0 is not None:
        monkeypatch.setattr(
            formsets[0].formset.__class__, "errors", original_errors_property_0
        )

    # Errors in the inline display in "General" tab
    class ErrorsPropertyGeneral:
        @property
        def errors(self):
            return [
                {"example_field": ["Example error."]},
                {"example_field2": ["Example error 2."]},
                {"example_field3": ["Example error 3."]},
            ]

    original_errors_property_1 = getattr(formsets[1].formset.__class__, "errors", None)
    monkeypatch.setattr(
        formsets[1].formset.__class__, "errors", ErrorsPropertyGeneral.errors
    )

    response = Template("{% load unfold %}{% tab_list 'changeform' opts %}").render(
        RequestContext(
            request,
            {
                "opts": get_user_model()._meta,
                "adminform": context_data["adminform"],
                "inline_admin_formsets": formsets,
            },
        )
    )

    assert "3" in response

    if original_errors_property_1 is not None:
        monkeypatch.setattr(
            formsets[1].formset.__class__, "errors", original_errors_property_1
        )


@pytest.mark.django_db
def test_tags_result_list_tag(rf, user_factory):
    template = Template("{% load unfold_list %} {% unfold_result_list cl %}")
    request = rf.get("/")
    user = user_factory(username="sample@example.com", is_superuser=True, is_staff=True)
    request.user = user
    user.content_type = ContentType.objects.get_for_model(User)
    user.save()
    cl = ChangeList(
        request=request,
        model=get_user_model(),
        model_admin=UserAdmin(User, UnfoldAdminSite()),
        sortable_by=["username"],
        date_hierarchy=[],
        search_fields=["username"],
        search_help_text=None,
        list_select_related=[],
        list_editable=[],
        list_display=["username", "content_type"],
        list_display_links=[],
        list_filter=[],
        list_per_page=10,
        list_max_show_all=100,
    )

    cl.formset = None
    cl.to_field = "pk"

    response = template.render(
        RequestContext(
            request,
            {
                "opts": get_user_model()._meta,
                "cl": cl,
            },
        )
    )
    assert "sample@example.com" in response


@pytest.mark.django_db
def test_tags_result_list_tag_no_display_links(rf, user_factory):
    template = Template("{% load unfold_list %} {% unfold_result_list cl %}")
    request = rf.get("/")
    request.user = user_factory(
        username="sample@example.com", is_superuser=True, is_staff=True
    )

    cl = ChangeList(
        request=request,
        model=get_user_model(),
        model_admin=UserAdmin(User, UnfoldAdminSite()),
        sortable_by=["username"],
        date_hierarchy=[],
        search_fields=["username"],
        search_help_text=None,
        list_select_related=[],
        list_editable=[],
        list_display=["username"],
        list_display_links=None,
        list_filter=[],
        list_per_page=10,
        list_max_show_all=100,
    )

    cl.formset = None

    response = template.render(
        RequestContext(
            request,
            {
                "opts": get_user_model()._meta,
                "cl": cl,
            },
        )
    )

    assert "sample@example.com" in response
    assert "/admin/example/user/1/change" not in response


def test_tags_result_list_view(admin_client, user_factory):
    user = user_factory(username="sample@example.com")
    response = admin_client.get(reverse("admin:example_user_changelist"))

    assert response.status_code == HTTPStatus.OK
    assert (
        f'<a href="{reverse("admin:example_user_change", args=[user.pk])}"'
        in response.content.decode()
    )


@pytest.mark.django_db
def test_tags_paginator_number(rf, user_factory):
    template = Template("{% load unfold_list %} {% paginator_number cl i %}")
    request = rf.get("/")
    request.user = user_factory(
        username="sample@example.com", is_superuser=True, is_staff=True
    )
    user_factory.create_batch(25)
    cl = ChangeList(
        request=request,
        model=get_user_model(),
        model_admin=UserAdmin(User, UnfoldAdminSite()),
        sortable_by=[],
        date_hierarchy=[],
        search_fields=["username"],
        search_help_text=None,
        list_select_related=[],
        list_editable=[],
        list_display=[],
        list_display_links=[],
        list_filter=[],
        list_per_page=5,
        list_max_show_all=100,
    )

    response = template.render(RequestContext(request, {"cl": cl, "i": 1}))
    assert (
        '<span class="font-medium text-primary-600">1</span>'
        in response.replace("\n", "").strip()
    )

    response = template.render(RequestContext(request, {"cl": cl, "i": 2}))
    assert (
        '<a href="?p=2" x-data x-on:click.prevent="window.location.href = $el.href + window.location.hash">2</a>'
        in response
    )


@pytest.mark.django_db
def test_tags_unfold_admin_search_form_tag(rf, user_factory):
    template = Template("{% load unfold_list %} {% unfold_search_form cl %}")
    request = rf.get("/")
    request.user = user_factory(
        username="sample@example.com", is_superuser=True, is_staff=True
    )
    response = template.render(
        RequestContext(
            request,
            {
                "cl": ChangeList(
                    request=request,
                    model=get_user_model(),
                    model_admin=UserAdmin(User, UnfoldAdminSite()),
                    sortable_by=[],
                    date_hierarchy=[],
                    search_fields=["username"],
                    search_help_text=None,
                    list_select_related=[],
                    list_editable=[],
                    list_display=[],
                    list_display_links=[],
                    list_filter=[],
                    list_per_page=10,
                    list_max_show_all=100,
                ),
                "opts": get_user_model()._meta,
            },
        )
    )
    assert "Type to search" in response


def test_tags_unfold_admin_actions(rf):
    template = Template("{% load unfold_list %} {% unfold_admin_actions %}")
    response = template.render(
        RequestContext(
            rf.get("/"),
            {
                "opts": get_user_model()._meta,
                "dataset": ProjectDataset(
                    request=rf.get("/"),
                    extra_context={},
                ),
            },
        )
    )
    assert "Run the selected action" in response


def test_tags_is_facet_var_django42(monkeypatch):
    monkeypatch.delattr(options, "IS_FACETS_VAR", raising=False)
    from unfold.templatetags import unfold_list as unfold_list_modified

    importlib.reload(unfold_list_modified)
    assert unfold_list_modified.IS_FACETS_VAR is None


@pytest.mark.django_db
def test_tags_result_list_object_does_not_exist(rf, user_factory, monkeypatch):
    from django.contrib.admin.utils import lookup_field as real_lookup_field

    template = Template("{% load unfold_list %} {% unfold_result_list cl %}")
    request = rf.get("/")
    user = user_factory(username="sample@example.com", is_superuser=True, is_staff=True)
    request.user = user

    cl = ChangeList(
        request=request,
        model=get_user_model(),
        model_admin=UserAdmin(User, UnfoldAdminSite()),
        sortable_by=["username"],
        date_hierarchy=[],
        search_fields=["username"],
        search_help_text=None,
        list_select_related=[],
        list_editable=[],
        list_display=["username"],
        list_display_links=[],
        list_filter=[],
        list_per_page=10,
        list_max_show_all=100,
    )

    cl.formset = None

    def mock_lookup_field(field_name, result, model_admin):
        if field_name == "username":
            raise ObjectDoesNotExist("Related object does not exist")
        return real_lookup_field(field_name, result, model_admin)

    monkeypatch.setattr(
        "unfold.templatetags.unfold_list.lookup_field", mock_lookup_field
    )

    opts = get_user_model()._meta
    opts.app_label = "non_existing_label"
    response = template.render(
        RequestContext(
            request,
            {
                "opts": opts,
                "cl": cl,
            },
        )
    )

    assert "sample@example.com" not in response


########################################################
# Fieldset active tab
########################################################
@pytest.mark.parametrize(
    ("fieldset_names", "active_name"),
    [
        # Latin
        (["Personal info", "Permissions"], "Personal info"),
        # Cyrillic
        (["Личная информация", "Права"], "Личная информация"),
        # Latin edge case (German ß)
        (["Straße", "Berechtigungen"], "Straße"),
        # Greek
        (["Προσωπικές πληροφορίες", "Δικαιώματα"], "Προσωπικές πληροφορίες"),
        # RTL (Arabic)
        (["المعلومات الشخصية", "الأذونات"], "المعلومات الشخصية"),
        # CJK (Chinese)
        (["个人信息", "权限"], "个人信息"),
    ],
)
def test_fieldset_active_tab(fieldset_names, active_name):
    tabs = [{"name": fieldset_name} for fieldset_name in fieldset_names]

    response = Template(
        """
        {% load unfold %}
        {% for fieldset in tabs %}
            <div class="tab-wrapper{% if fieldset.name %} fieldset-{{ fieldset.name|unicoded_slugify }}{% endif %}"
                 x-show="activeFieldsetTab == '{{ fieldset.name|unicoded_slugify }}'">
                Test
            </div>
        {% endfor %}
        """
    ).render(
        Context(
            {
                "tabs": tabs,
            }
        )
    )

    tab_ids = re.findall(r"""x-show="activeFieldsetTab == '([^']*)'""", response)
    fieldset_classes = re.findall(r'class="tab-wrapper fieldset-([^"]+)"', response)

    assert fieldset_classes == tab_ids
