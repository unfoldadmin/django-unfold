from http import HTTPStatus

import pytest
from django.contrib.admin.templatetags.admin_list import admin_list_filter
from django.contrib.auth import get_user_model
from django.urls import reverse_lazy
from example.models import ApprovalChoices, StatusChoices, Tag

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
# Choice filters
########################################################
@pytest.mark.django_db
@pytest.mark.parametrize("facet", [True, False])
@pytest.mark.parametrize(
    "param, value, expected, not_expected",
    [
        [
            "custom_radio_filter",
            StatusChoices.ACTIVE,
            ["sample1@example.com"],
            ["sample2@example.com"],
        ],
        [
            "custom_radio_filter",
            StatusChoices.PENDING,
            [],
            ["sample1@example.com", "sample2@example.com"],
        ],
    ],
)
def test_filters_choices_radio_custom(
    admin_client, user_factory, facet, param, value, expected, not_expected
):
    user_factory.create(username="sample1@example.com", status=StatusChoices.ACTIVE)
    user_factory.create(username="sample2@example.com", status=StatusChoices.INACTIVE)

    response = admin_client.get(
        reverse_lazy("admin:example_filteruser_changelist"),
        data={
            param: value,
            **({"_facets": "True"} if facet else {}),
        },
    )
    assert response.status_code == HTTPStatus.OK

    for user in expected:
        assert response.context_data["cl"].queryset.filter(username=user).exists()

    for user in not_expected:
        assert not response.context_data["cl"].queryset.filter(username=user).exists()


@pytest.mark.django_db
@pytest.mark.parametrize("facet", [True, False])
@pytest.mark.parametrize(
    "param, value, expected, not_expected",
    [
        [
            "custom_checkbox_filter",
            ApprovalChoices.NEW,
            ["sample1@example.com"],
            ["sample2@example.com"],
        ],
        [
            "custom_checkbox_filter",
            ApprovalChoices.REVIEWED,
            ["sample2@example.com"],
            ["sample1@example.com"],
        ],
    ],
)
def test_filters_choices_checkbox_custom(
    admin_client, user_factory, facet, param, value, expected, not_expected
):
    user_factory.create(username="sample1@example.com", approval=ApprovalChoices.NEW)
    user_factory.create(
        username="sample2@example.com", approval=ApprovalChoices.REVIEWED
    )

    response = admin_client.get(
        reverse_lazy("admin:example_filteruser_changelist"),
        data={
            param: value,
            **({"_facets": "True"} if facet else {}),
        },
    )
    assert response.status_code == HTTPStatus.OK
    for user in expected:
        assert response.context_data["cl"].queryset.filter(username=user).exists()

    for user in not_expected:
        assert not response.context_data["cl"].queryset.filter(username=user).exists()


@pytest.mark.django_db
@pytest.mark.parametrize("facet", [True, False])
def test_filters_choices_radio(admin_client, user_factory, facet):
    user_factory.create(username="sample1@example.com", status=StatusChoices.ACTIVE)
    user_factory.create(username="sample2@example.com", status=StatusChoices.INACTIVE)

    response = admin_client.get(
        reverse_lazy("admin:example_filteruser_changelist"),
        data={
            "status__exact": StatusChoices.ACTIVE,
            **({"_facets": "True"} if facet else {}),
        },
    )
    assert response.status_code == HTTPStatus.OK
    assert (
        response.context_data["cl"]
        .queryset.filter(username="sample1@example.com")
        .exists()
    )
    assert (
        not response.context_data["cl"]
        .queryset.filter(username="sample2@example.com")
        .exists()
    )


@pytest.mark.django_db
@pytest.mark.parametrize("facet", [True, False])
def test_filters_choices_checkbox(admin_client, user_factory, facet):
    user_factory.create(username="sample1@example.com", approval=ApprovalChoices.NEW)
    user_factory.create(
        username="sample2@example.com", approval=ApprovalChoices.REVIEWED
    )
    user_factory.create(
        username="sample3@example.com", approval=ApprovalChoices.APPROVED
    )

    response = admin_client.get(
        reverse_lazy("admin:example_filteruser_changelist"),
        data={
            "approval__exact": [
                ApprovalChoices.NEW,
                ApprovalChoices.REVIEWED,
            ],
            **({"_facets": "True"} if facet else {}),
        },
    )
    assert response.status_code == HTTPStatus.OK
    assert (
        response.context_data["cl"]
        .queryset.filter(username="sample1@example.com")
        .exists()
    )
    assert (
        response.context_data["cl"]
        .queryset.filter(username="sample2@example.com")
        .exists()
    )
    assert (
        not response.context_data["cl"]
        .queryset.filter(username="sample3@example.com")
        .exists()
    )


@pytest.mark.django_db
@pytest.mark.parametrize("facet", [True, False])
def test_filters_choices_boolean_radio(admin_client, user_factory, facet):
    user_factory.create(username="sample1@example.com", is_active=True)
    user_factory.create(username="sample2@example.com", is_active=False)
    response = admin_client.get(
        reverse_lazy("admin:example_filteruser_changelist"),
        data={
            "is_active__exact": 1,
            **({"_facets": "True"} if facet else {}),
        },
    )
    assert response.status_code == HTTPStatus.OK

    assert (
        response.context_data["cl"]
        .queryset.filter(username="sample1@example.com")
        .exists()
    )
    assert (
        not response.context_data["cl"]
        .queryset.filter(username="sample2@example.com")
        .exists()
    )


@pytest.mark.django_db
@pytest.mark.parametrize("facet", [True, False])
@pytest.mark.parametrize(
    "param, value, expected, not_expected",
    [
        ["tags__id__exact", ["tag1"], ["sample1@example.com"], ["sample2@example.com"]],
        [
            "tags__id__exact",
            ["tag2"],
            ["sample1@example.com", "sample2@example.com"],
            [],
        ],
        ["tags__id__exact", ["tag3"], ["sample2@example.com"], ["sample1@example.com"]],
        [
            "tags__id__exact",
            ["tag4"],
            [],
            ["sample1@example.com", "sample2@example.com"],
        ],
    ],
)
def test_filters_choices_related_checkbox(
    admin_client, user_factory, tag_factory, facet, param, value, expected, not_expected
):
    tag1 = tag_factory.create(name="tag1")
    tag2 = tag_factory.create(name="tag2")
    tag3 = tag_factory.create(name="tag3")
    tag_factory.create(name="tag4")

    user_factory.create(username="sample1@example.com").tags.add(tag1, tag2)
    user_factory.create(username="sample2@example.com").tags.add(tag2, tag3)

    response = admin_client.get(
        reverse_lazy("admin:example_filteruser_changelist"),
        data={
            param: [Tag.objects.get(name=tag_name).pk for tag_name in value],
            **({"_facets": "True"} if facet else {}),
        },
    )
    assert response.status_code == HTTPStatus.OK
    for user in expected:
        assert response.context_data["cl"].queryset.filter(username=user).exists()

    for user in not_expected:
        assert not response.context_data["cl"].queryset.filter(username=user).exists()


@pytest.mark.django_db
@pytest.mark.parametrize("facet", [True, False])
@pytest.mark.parametrize(
    "param, value, expected, not_expected",
    [
        [
            "username",
            "sample1@example.com",
            ["sample1@example.com"],
            ["sample2@example.com"],
        ],
        [
            "username",
            "sample2@example.com",
            ["sample2@example.com"],
            ["sample1@example.com"],
        ],
        [
            "username",
            ["sample1@example.com", "sample2@example.com"],
            ["sample1@example.com", "sample2@example.com"],
            [],
        ],
    ],
)
def test_filters_choices_all_values_checkbox(
    admin_client, user_factory, facet, param, value, expected, not_expected
):
    user_factory.create(username="sample1@example.com")
    user_factory.create(username="sample2@example.com")
    response = admin_client.get(
        reverse_lazy("admin:example_filteruser_changelist"),
        data={
            param: value,
            **({"_facets": "True"} if facet else {}),
        },
    )
    assert response.status_code == HTTPStatus.OK
    for user in expected:
        assert response.context_data["cl"].queryset.filter(username=user).exists()

    for user in not_expected:
        assert not response.context_data["cl"].queryset.filter(username=user).exists()


########################################################
# Numeric filters
########################################################
@pytest.mark.django_db
@pytest.mark.parametrize(
    "value, expected, not_expected",
    [
        ("", ["sample1@example.com", "sample2@example.com"], []),
        ("wrong_value", ["sample1@example.com", "sample2@example.com"], []),
        (10, ["sample1@example.com"], ["sample2@example.com"]),
        (20, ["sample2@example.com"], ["sample1@example.com"]),
        (30, [], ["sample1@example.com", "sample2@example.com"]),
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
        assert response.context_data["cl"].queryset.filter(username=user).exists()

    for user in not_expected:
        assert not response.context_data["cl"].queryset.filter(username=user).exists()


@pytest.mark.django_db
@pytest.mark.parametrize(
    "param, value_min, value_max, expected, not_expected",
    [
        ("numeric_range", 9, 11, ["sample1@example.com"], ["sample2@example.com"]),
        ("numeric_range", 19, 21, ["sample2@example.com"], ["sample1@example.com"]),
        ("numeric_range", 10, 20, ["sample1@example.com", "sample2@example.com"], []),
        ("numeric_range", 11, 19, [], ["sample1@example.com", "sample2@example.com  "]),
        (
            "numeric_range_custom",
            9,
            11,
            ["sample1@example.com"],
            ["sample2@example.com"],
        ),
        (
            "numeric_range_custom",
            19,
            21,
            ["sample2@example.com"],
            ["sample1@example.com"],
        ),
        (
            "numeric_range_custom",
            10,
            20,
            ["sample1@example.com", "sample2@example.com"],
            [],
        ),
        (
            "numeric_range_custom",
            11,
            19,
            [],
            ["sample1@example.com", "sample2@example.com"],
        ),
        ("numeric_slider", 9, 11, ["sample1@example.com"], ["sample2@example.com"]),
        ("numeric_slider", 19, 21, ["sample2@example.com"], ["sample1@example.com"]),
        ("numeric_slider", 10, 20, ["sample1@example.com", "sample2@example.com"], []),
        ("numeric_slider", 11, 19, [], ["sample1@example.com", "sample2@example.com"]),
        (
            "numeric_slider_custom",
            9,
            11,
            ["sample1@example.com"],
            ["sample2@example.com"],
        ),
        (
            "numeric_slider_custom",
            19,
            21,
            ["sample2@example.com"],
            ["sample1@example.com"],
        ),
        (
            "numeric_slider_custom",
            10,
            20,
            ["sample1@example.com", "sample2@example.com"],
            [],
        ),
        (
            "numeric_slider_custom",
            11,
            19,
            [],
            ["sample1@example.com", "sample2@example.com"],
        ),
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
        assert response.context_data["cl"].queryset.filter(username=user).exists()

    for user in not_expected:
        assert not response.context_data["cl"].queryset.filter(username=user).exists()


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
    assert (
        response.context_data["cl"]
        .queryset.filter(username="sample1@example.com")
        .exists()
    )
    assert (
        response.context_data["cl"]
        .queryset.filter(username="sample2@example.com")
        .exists()
    )

    response = admin_client.get(
        reverse_lazy("admin:example_filteruser_changelist"),
        data={"text_username": "sample1"},
    )
    assert response.status_code == HTTPStatus.OK
    assert (
        response.context_data["cl"]
        .queryset.filter(username="sample1@example.com")
        .exists()
    )
    assert (
        not response.context_data["cl"]
        .queryset.filter(username="sample2@example.com")
        .exists()
    )


@pytest.mark.django_db
def test_filters_fieldtext_filter(admin_client, user_factory):
    user_factory.create(username="sample1@example.com")
    user_factory.create(username="sample2@example.com")
    response = admin_client.get(reverse_lazy("admin:example_filteruser_changelist"))
    assert response.status_code == HTTPStatus.OK
    assert (
        response.context_data["cl"]
        .queryset.filter(username="sample1@example.com")
        .exists()
    )
    assert (
        response.context_data["cl"]
        .queryset.filter(username="sample2@example.com")
        .exists()
    )

    response = admin_client.get(
        reverse_lazy("admin:example_filteruser_changelist"),
        data={"username__icontains": "sample1"},
    )
    assert response.status_code == HTTPStatus.OK
    assert (
        response.context_data["cl"]
        .queryset.filter(username="sample1@example.com")
        .exists()
    )
    assert (
        not response.context_data["cl"]
        .queryset.filter(username="sample2@example.com")
        .exists()
    )


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
