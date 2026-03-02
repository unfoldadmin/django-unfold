from datetime import timedelta
from http import HTTPStatus

import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse_lazy
from django.utils.timezone import now
from example.models import (
    ApprovalChoices,
    Category,
    ColorChoices,
    Label,
    PriorityChoices,
    Project,
    StatusChoices,
    Tag,
    Task,
)

from unfold.contrib.filters.admin import (
    RangeDateFilter,
    RangeDateTimeFilter,
    RangeNumericFilter,
    SingleNumericFilter,
    SliderNumericFilter,
)


########################################################
# Dropdown filters
########################################################
@pytest.mark.django_db
@pytest.mark.parametrize("param", ["priority__exact", "custom_priority"])
@pytest.mark.parametrize(
    "value, expected, not_expected",
    [
        [PriorityChoices.LOW, ["sample1@example.com"], ["sample2@example.com"]],
        [PriorityChoices.HIGH, ["sample2@example.com"], ["sample1@example.com"]],
        [PriorityChoices.MEDIUM, [], ["sample1@example.com", "sample2@example.com"]],
    ],
)
def test_filters_dropdown_choices(
    admin_client, user_factory, param, value, expected, not_expected
):
    user_factory.create(username="sample1@example.com", priority=PriorityChoices.LOW)
    user_factory.create(username="sample2@example.com", priority=PriorityChoices.HIGH)

    response = admin_client.get(
        reverse_lazy("admin:example_filteruser_changelist"),
        data={param: value},
    )
    assert response.status_code == HTTPStatus.OK
    for user in expected:
        assert response.context_data["cl"].queryset.filter(username=user).exists()

    for user in not_expected:
        assert not response.context_data["cl"].queryset.filter(username=user).exists()


@pytest.mark.django_db
@pytest.mark.parametrize("param", ["color__exact", "custom_color"])
@pytest.mark.parametrize(
    "value, expected, not_expected",
    [
        [ColorChoices.RED, ["sample1@example.com"], ["sample2@example.com"]],
        [ColorChoices.BLUE, ["sample2@example.com"], ["sample1@example.com"]],
        [
            [ColorChoices.RED, ColorChoices.BLUE],
            ["sample1@example.com", "sample2@example.com"],
            [],
        ],
    ],
)
def test_filters_multiple_dropdown_choices(
    admin_client, user_factory, param, value, expected, not_expected
):
    user_factory.create(username="sample1@example.com", color=ColorChoices.RED)
    user_factory.create(username="sample2@example.com", color=ColorChoices.BLUE)

    response = admin_client.get(
        reverse_lazy("admin:example_filteruser_changelist"),
        data={param: value},
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
            "categories__exact",
            "category1",
            ["sample1@example.com"],
            ["sample2@example.com"],
        ],
        [
            "categories__exact",
            "category2",
            ["sample2@example.com"],
            ["sample1@example.com"],
        ],
        [
            "categories__exact",
            "category3",
            [],
            ["sample1@example.com", "sample2@example.com"],
        ],
    ],
)
def test_filters_related_dropdown_choices(
    admin_client,
    user_factory,
    category_factory,
    facet,
    param,
    value,
    expected,
    not_expected,
):
    category1 = category_factory.create(name="category1")
    category2 = category_factory.create(name="category2")
    category_factory.create(name="category3")

    user_factory.create(username="sample1@example.com").categories.add(category1)
    user_factory.create(username="sample2@example.com").categories.add(category2)

    response = admin_client.get(
        reverse_lazy("admin:example_filteruser_changelist"),
        data={
            param: Category.objects.get(name=value).pk,
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
            "labels__exact",
            ["label1"],
            ["sample1@example.com"],
            ["sample2@example.com"],
        ],
        [
            "labels__exact",
            ["label2"],
            ["sample2@example.com"],
            ["sample1@example.com"],
        ],
        [
            "labels__exact",
            ["label1", "label2"],
            ["sample1@example.com", "sample2@example.com"],
            [],
        ],
        [
            "labels__exact",
            ["label3"],
            [],
            ["sample1@example.com", "sample2@example.com"],
        ],
    ],
)
def test_filters_multiple_related_dropdown_choices(
    admin_client,
    user_factory,
    label_factory,
    facet,
    param,
    value,
    expected,
    not_expected,
):
    label1 = label_factory.create(name="label1")
    label2 = label_factory.create(name="label2")
    label_factory.create(name="label3")

    user_factory.create(username="sample1@example.com").labels.add(label1)
    user_factory.create(username="sample2@example.com").labels.add(label2)

    response = admin_client.get(
        reverse_lazy("admin:example_filteruser_changelist"),
        data={
            param: [Label.objects.get(name=label_name).pk for label_name in value],
            **({"_facets": "True"} if facet else {}),
        },
    )
    assert response.status_code == HTTPStatus.OK

    for user in expected:
        assert response.context_data["cl"].queryset.filter(username=user).exists()

    for user in not_expected:
        assert not response.context_data["cl"].queryset.filter(username=user).exists()


########################################################
# Date/time filters
########################################################
@pytest.mark.django_db
@pytest.mark.parametrize(
    "date_from, date_to, expected, not_expected",
    [
        [
            "wrong_value",
            now().date() - timedelta(days=1),
            ["sample1@example.com"],
            [],
        ],
        [
            now().date() - timedelta(days=2),
            now().date() - timedelta(days=1),
            [],
            ["sample1@example.com"],
        ],
        [
            now().date() - timedelta(days=1),
            now().date() + timedelta(days=1),
            ["sample1@example.com"],
            [],
        ],
        [
            now().date() + timedelta(days=1),
            now().date() + timedelta(days=2),
            [],
            ["sample1@example.com"],
        ],
        [
            now().date() - timedelta(days=2),
            None,
            ["sample1@example.com"],
            [],
        ],
        [
            None,
            now().date() + timedelta(days=2),
            ["sample1@example.com"],
            [],
        ],
    ],
)
def test_filters_date(
    admin_client, user_factory, date_from, date_to, expected, not_expected
):
    user_factory.create(username="sample1@example.com", date_joined=now())

    response = admin_client.get(
        reverse_lazy("admin:example_filteruser_changelist"),
        data={
            "date_joined_from": date_from if date_from else "",
            "date_joined_to": date_to if date_to else "",
        },
    )
    assert response.status_code == HTTPStatus.OK

    for user in expected:
        assert response.context_data["cl"].queryset.filter(username=user).exists()

    for user in not_expected:
        assert not response.context_data["cl"].queryset.filter(username=user).exists()


@pytest.mark.django_db
@pytest.mark.parametrize(
    "date_from, date_to, expected, not_expected",
    [
        [
            {
                "date": "2024-01-01",
                "time": "12:00:00",
            },
            None,
            ["sample1@example.com"],
            [],
        ],
        [
            "wrong_value",
            now() + timedelta(days=1),
            ["sample1@example.com"],
            [],
        ],
        [
            now() - timedelta(days=2),
            now() - timedelta(days=1),
            [],
            ["sample1@example.com"],
        ],
        [
            now() - timedelta(days=1),
            now() + timedelta(days=1),
            ["sample1@example.com"],
            [],
        ],
        [
            now() + timedelta(days=1),
            now() + timedelta(days=2),
            [],
            ["sample1@example.com"],
        ],
        [
            now() - timedelta(days=2),
            None,
            ["sample1@example.com"],
            [],
        ],
        [
            None,
            now() + timedelta(days=2),
            ["sample1@example.com"],
            [],
        ],
    ],
)
def test_filters_datetime(
    admin_client, user_factory, date_from, date_to, expected, not_expected
):
    user_factory.create(username="sample1@example.com", last_login=now())

    if date_from is None:
        from_0 = ""
        from_1 = ""
    elif isinstance(date_from, dict):
        from_0 = date_from["date"]
        from_1 = date_from["time"]
    elif isinstance(date_from, str):
        from_0 = date_from
        from_1 = date_from
    else:
        from_0 = date_from.date()
        from_1 = date_from.time()

    if date_to is None:
        to_0 = ""
        to_1 = ""
    elif isinstance(date_to, dict):
        to_0 = date_to["date"]
        to_1 = date_to["time"]
    elif isinstance(date_to, str):
        to_0 = date_to
        to_1 = date_to
    else:
        to_0 = date_to.date()
        to_1 = date_to.time()

    response = admin_client.get(
        reverse_lazy("admin:example_filteruser_changelist"),
        data={
            "last_login_from_0": from_0,
            "last_login_from_1": from_1,
            "last_login_to_0": to_0,
            "last_login_to_1": to_1,
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
    [RangeDateFilter, RangeDateTimeFilter],
)
def test_filters_datetime_wrong_type(admin_request, user_model_admin, filter_class):
    with pytest.raises(TypeError) as excinfo:
        filter_class(
            request=admin_request,
            params={"date_wrong_type": ""},
            model=get_user_model(),
            model_admin=user_model_admin,
            field=get_user_model()._meta.get_field("username"),
            field_path="username",
        )
    assert "is not supported for" in str(excinfo.value)


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
        (
            "numeric_range",
            "wrong_value",
            11,
            ["sample1@example.com", "sample2@example.com"],
            [],
        ),
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
            field=get_user_model()._meta.get_field("username"),
            field_path="username",
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
@pytest.mark.parametrize(
    "param, value, expected, not_expected",
    [
        (
            "projects__id__exact",
            "project1",
            ["sample1@example.com"],
            ["sample2@example.com"],
        ),
        (
            "projects__id__exact",
            "project2",
            ["sample2@example.com"],
            ["sample1@example.com"],
        ),
        (
            "projects__id__exact",
            "project3",
            [],
            ["sample1@example.com", "sample2@example.com"],
        ),
    ],
)
def test_filters_autocomplete_select_filter(
    admin_client, user_factory, project_factory, param, value, expected, not_expected
):
    project1 = project_factory.create(name="project1")
    project2 = project_factory.create(name="project2")
    project_factory.create(name="project3")

    user_factory.create(username="sample1@example.com").projects.add(project1)
    user_factory.create(username="sample2@example.com").projects.add(project2)

    response = admin_client.get(
        reverse_lazy("admin:example_filteruser_changelist"),
        data={
            param: Project.objects.get(name=value).pk,
        },
    )

    assert response.status_code == HTTPStatus.OK
    for user in expected:
        assert response.context_data["cl"].queryset.filter(username=user).exists()

    for user in not_expected:
        assert not response.context_data["cl"].queryset.filter(username=user).exists()


@pytest.mark.django_db
@pytest.mark.parametrize(
    "param, value, expected, not_expected",
    [
        (
            "tasks__id__exact",
            ["task1"],
            ["sample1@example.com"],
            ["sample2@example.com"],
        ),
        (
            "tasks__id__exact",
            ["task2"],
            ["sample2@example.com"],
            ["sample1@example.com"],
        ),
        (
            "tasks__id__exact",
            ["task1", "task2"],
            ["sample1@example.com", "sample2@example.com"],
            [],
        ),
        (
            "tasks__id__exact",
            ["task3"],
            [],
            ["sample1@example.com", "sample2@example.com"],
        ),
    ],
)
def test_filters_autocomplete_select_multiple_filter(
    admin_client,
    user_factory,
    task_factory,
    project_factory,
    param,
    value,
    expected,
    not_expected,
):
    project = project_factory.create(name="project1")
    task1 = task_factory.create(name="task1", project=project)
    task2 = task_factory.create(name="task2", project=project)
    task_factory.create(name="task3", project=project)

    user_factory.create(username="sample1@example.com").tasks.add(task1)
    user_factory.create(username="sample2@example.com").tasks.add(task2)

    response = admin_client.get(
        reverse_lazy("admin:example_filteruser_changelist"),
        data={
            param: [Task.objects.get(name=task_name).pk for task_name in value],
        },
    )

    assert response.status_code == HTTPStatus.OK

    for user in expected:
        assert response.context_data["cl"].queryset.filter(username=user).exists()

    for user in not_expected:
        assert not response.context_data["cl"].queryset.filter(username=user).exists()
