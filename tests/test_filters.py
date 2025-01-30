import pytest
from django.contrib.admin.templatetags.admin_list import admin_list_filter
from django.contrib.auth import get_user_model

from unfold.contrib.filters.admin.autocomplete_filters import (
    AutocompleteSelectFilter,
    AutocompleteSelectMultipleFilter,
)
from unfold.contrib.filters.admin.text_filters import FieldTextFilter


@pytest.mark.django_db
def test_filters_field_text_filter(admin_request, user_model_admin, user_changelist):
    filter = FieldTextFilter(
        request=admin_request,
        params={"username": "test"},
        model=get_user_model(),
        model_admin=user_model_admin,
        field="username",
        field_path="username",
    )

    assert "id_username__icontains" in admin_list_filter(user_changelist, filter)


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
