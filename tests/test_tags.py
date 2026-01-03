import pytest
from django.contrib.auth import get_user_model
from django.template import Context, Template, TemplateSyntaxError
from django.template.context import RequestContext


@pytest.mark.django_db
def test_tags_action_list():
    pass


@pytest.mark.django_db
def test_tags_tab_list():
    pass


@pytest.mark.django_db
def test_tags_render_section():
    pass


@pytest.mark.django_db
def test_tags_has_nav_item_active():
    pass


@pytest.mark.django_db
def test_tags_class_name():
    pass


@pytest.mark.django_db
def test_tags_is_list():
    pass


@pytest.mark.django_db
def test_tags_has_active_item():
    pass


@pytest.mark.django_db
def test_tags_index():
    pass


@pytest.mark.django_db
def test_tags_tabs():
    pass


@pytest.mark.django_db
def test_tags_do_component():
    pass


@pytest.mark.django_db
def test_tags_add_css_class():
    pass


@pytest.mark.django_db
def test_tags_preserve_changelist_filters():
    pass


@pytest.mark.django_db
def test_tags_element_classes():
    pass


@pytest.mark.django_db
def test_tags_fieldset_rows_classes():
    pass


@pytest.mark.django_db
def test_tags_fieldset_row_classes():
    pass


@pytest.mark.django_db
def test_tags_fieldset_line_classes():
    pass


@pytest.mark.django_db
def test_tags_action_item_classes():
    pass


@pytest.mark.django_db
def test_tags_changeform_data():
    pass


@pytest.mark.django_db
def test_tags_changeform_condition():
    pass


@pytest.mark.django_db
def test_tags_infinite_paginator_url():
    pass


@pytest.mark.django_db
def test_tags_elided_page_range():
    pass


@pytest.mark.django_db
def test_tags_querystring_params():
    pass


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
