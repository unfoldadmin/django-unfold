from http import HTTPStatus

import pytest
from django.contrib.admin.templatetags.admin_list import admin_list_filter
from django.contrib.auth import get_user_model
from django.urls import reverse_lazy

from unfold.contrib.filters.admin import (
    RangeNumericFilter,
    SingleNumericFilter,
    SliderNumericFilter,
)
from unfold.contrib.filters.admin.autocomplete_filters import (
    AutocompleteSelectFilter,
    AutocompleteSelectMultipleFilter,
)


########################################################
# Numeric filters
########################################################
@pytest.mark.django_db
@pytest.mark.parametrize(
    "value, expected, not_expected",
    [
        ("", ["sample1", "sample2"], []),
        ("wrong_value", ["sample1", "sample2"], []),
        (10, ["sample1"], ["sample2"]),
        (20, ["sample2"], ["sample1"]),
        (30, [], ["sample1", "sample2"]),
    ],
)
def test_filters_numeric_single(
    admin_client, user_factory, value, expected, not_expected
):
    user_factory.create(username="sample1@example.com", numeric_single=10)
    user_factory.create(username="sample2@example.com", numeric_single=20)
    response = admin_client.get(
        reverse_lazy("admin:example_filteruser_changelist"),
        data={
            "numeric_single": value,
        },
    )
    assert response.status_code == HTTPStatus.OK
    assert "By Numeric Single" in response.content.decode()

    for user in expected:
        assert user in response.content.decode()

    for user in not_expected:
        assert user not in response.content.decode()


@pytest.mark.django_db
@pytest.mark.parametrize(
    "param, value_min, value_max, expected, not_expected",
    [
        ("numeric_range", 9, 11, ["sample1"], ["sample2"]),
        ("numeric_range", 19, 21, ["sample2"], ["sample1"]),
        ("numeric_range", 10, 20, ["sample1", "sample2"], []),
        ("numeric_range", 11, 19, [], ["sample1", "sample2"]),
        ("numeric_range_custom", 9, 11, ["sample1"], ["sample2"]),
        ("numeric_range_custom", 19, 21, ["sample2"], ["sample1"]),
        ("numeric_range_custom", 10, 20, ["sample1", "sample2"], []),
        ("numeric_range_custom", 11, 19, [], ["sample1", "sample2"]),
        ("numeric_slider", 9, 11, ["sample1"], ["sample2"]),
        ("numeric_slider", 19, 21, ["sample2"], ["sample1"]),
        ("numeric_slider", 10, 20, ["sample1", "sample2"], []),
        ("numeric_slider", 11, 19, [], ["sample1", "sample2"]),
        ("numeric_slider_custom", 9, 11, ["sample1"], ["sample2"]),
        ("numeric_slider_custom", 19, 21, ["sample2"], ["sample1"]),
        ("numeric_slider_custom", 10, 20, ["sample1", "sample2"], []),
        ("numeric_slider_custom", 11, 19, [], ["sample1", "sample2"]),
    ],
)
def test_filters_numeric_range(
    admin_client, user_factory, param, value_min, value_max, expected, not_expected
):
    user_factory.create(username="sample1@example.com", **{param: 10})
    user_factory.create(username="sample2@example.com", **{param: 20})
    response = admin_client.get(
        reverse_lazy("admin:example_filteruser_changelist"),
        data={
            f"{param}_from": value_min,
            f"{param}_to": value_max,
        },
    )
    assert response.status_code == HTTPStatus.OK

    for user in expected:
        assert user in response.content.decode()

    for user in not_expected:
        assert user not in response.content.decode()


@pytest.mark.django_db
@pytest.mark.parametrize(
    "filter_class",
    [
        SingleNumericFilter,
        RangeNumericFilter,
        SliderNumericFilter,
    ],
)
def test_filters_numeric_wrong_type(admin_request, user_model_admin, filter_class):
    with pytest.raises(TypeError) as excinfo:
        filter_class(
            request=admin_request,
            params={"numeric_wrong_type": ""},
            model=get_user_model(),
            model_admin=user_model_admin,
            field=get_user_model()._meta.get_field("numeric_wrong_type"),
            field_path="numeric_wrong_type",
        )
    assert "is not supported for" in str(excinfo.value)


########################################################
# Text filters
########################################################
@pytest.mark.django_db
def test_filters_text_filter(admin_client, user_factory):
    user_factory.create(username="sample1@example.com")
    user_factory.create(username="sample2@example.com")
    response = admin_client.get(reverse_lazy("admin:example_filteruser_changelist"))
    assert response.status_code == HTTPStatus.OK
    assert "By Text filter" in response.content.decode()
    assert "sample1@example.com" in response.content.decode()
    assert "sample2@example.com" in response.content.decode()

    response = admin_client.get(
        reverse_lazy("admin:example_filteruser_changelist"),
        data={"text_username": "sample1"},
    )
    assert response.status_code == HTTPStatus.OK
    assert "sample1@example.com" in response.content.decode()
    assert "sample2@example.com" not in response.content.decode()


@pytest.mark.django_db
def test_filters_fieldtext_filter(admin_client, user_factory):
    user_factory.create(username="sample1@example.com")
    user_factory.create(username="sample2@example.com")
    response = admin_client.get(reverse_lazy("admin:example_filteruser_changelist"))
    assert response.status_code == HTTPStatus.OK
    assert "By username" in response.content.decode()
    assert "sample1@example.com" in response.content.decode()
    assert "sample2@example.com" in response.content.decode()

    response = admin_client.get(
        reverse_lazy("admin:example_filteruser_changelist"),
        data={"username__icontains": "sample1"},
    )
    assert response.status_code == HTTPStatus.OK
    assert "sample1@example.com" in response.content.decode()
    assert "sample2@example.com" not in response.content.decode()


########################################################
# Autocomplete filters
########################################################
@pytest.mark.django_db
def test_filters_autocomplete_select_multiple_filter(
    admin_request, user_model_admin, user_changelist
):
    user_model = get_user_model()

    filter = AutocompleteSelectMultipleFilter(
        request=admin_request,
        params={"content_type": "test"},
        model=get_user_model(),
        model_admin=user_model_admin,
        field=user_model._meta.get_field("content_type"),
        field_path="content_type",
    )

    assert "id_content_type__id__exact" in admin_list_filter(user_changelist, filter)


@pytest.mark.django_db
def test_filters_autocomplete_select_filter(
    admin_request, user_model_admin, user_changelist
):
    user_model = get_user_model()

    filter = AutocompleteSelectFilter(
        request=admin_request,
        params={"content_type": "test"},
        model=get_user_model(),
        model_admin=user_model_admin,
        field=user_model._meta.get_field("content_type"),
        field_path="content_type",
    )

    assert "id_content_type__id__exact" in admin_list_filter(user_changelist, filter)
