import pytest
from django.contrib.admin.templatetags.admin_list import admin_list_filter
from django.contrib.auth import get_user_model

from src.unfold.contrib.filters.admin.numeric_filters import SliderNumericFilter
from unfold.contrib.filters.admin.autocomplete_filters import (
    AutocompleteSelectFilter,
    AutocompleteSelectMultipleFilter,
)
from unfold.contrib.filters.admin.text_filters import FieldTextFilter


@pytest.mark.django_db
def test_filters_field_text_filter(admin_request, user_model_admin, user_changelist):
    # Arrange
    User = get_user_model()
    user_field = "username"

    # Act
    admin_filter = FieldTextFilter(
        request=admin_request,
        params={user_field: "test"},
        model=User,
        model_admin=user_model_admin,
        field=User._meta.get_field(user_field),
        field_path=user_field,
    )

    # Assert
    assert f"id_{user_field}__icontains" in admin_list_filter(
        user_changelist, admin_filter
    )


@pytest.mark.django_db
def test_filters_autocomplete_select_multiple_filter(
    admin_request, user_model_admin, user_changelist
):
    # Arrange
    User = get_user_model()
    user_field = "content_type"

    # Act
    admin_filter = AutocompleteSelectMultipleFilter(
        request=admin_request,
        params={user_field: "test"},
        model=User,
        model_admin=user_model_admin,
        field=User._meta.get_field(user_field),
        field_path=user_field,
    )

    # Assert
    assert f"id_{user_field}__id__exact" in admin_list_filter(
        user_changelist, admin_filter
    )


@pytest.mark.django_db
def test_filters_autocomplete_select_filter(
    admin_request, user_model_admin, user_changelist
):
    # Arrange
    User = get_user_model()
    user_field = "content_type"

    # Act
    admin_filter = AutocompleteSelectFilter(
        request=admin_request,
        params={user_field: "test"},
        model=User,
        model_admin=user_model_admin,
        field=User._meta.get_field(user_field),
        field_path=user_field,
    )

    # Assert
    assert f"id_{user_field}__id__exact" in admin_list_filter(
        user_changelist, admin_filter
    )


@pytest.mark.django_db
def test_filters_slider_numeric_filter(
    admin_request, user_model_admin, user_changelist
):
    # Arrange
    User = get_user_model()
    user_field = "age"
    min = 10
    max = 20
    User.objects.create_user(username="test_child", age=min)
    User.objects.create_user(username="test_adult", age=max)
    value_from = 18
    value_to = 30

    # Act
    admin_filter = SliderNumericFilter(
        request=admin_request,
        params={f"{user_field}_from": value_from, f"{user_field}_to": value_to},
        model=User,
        model_admin=user_model_admin,
        field=User._meta.get_field(user_field),
        field_path=user_field,
    )
    choices = admin_filter.choices(user_changelist)[0]
    filtered_list = admin_list_filter(user_changelist, admin_filter)

    # Assert
    assert choices.get("min") == min
    assert choices.get("max") == max
    assert choices.get("value_from") == value_from
    assert choices.get("value_to") == value_to
    assert choices.get("request") == admin_request
    assert f"{user_field}_from" in filtered_list
    assert f"{user_field}_to" in filtered_list
