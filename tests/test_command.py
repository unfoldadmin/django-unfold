from http import HTTPStatus

import pytest
from django.contrib.auth.models import Permission
from django.test import override_settings
from django.urls import reverse

from unfold.settings import CONFIG_DEFAULTS


@pytest.mark.django_db
def test_command_anonymous_unaccessible(client):
    response = client.get(reverse("admin:search"))
    assert response.status_code == HTTPStatus.FOUND


@pytest.mark.django_db
def test_command_authenticated_unaccessible(client, user_factory):
    user = user_factory(username="test", password="test")
    client.force_login(user)
    response = client.get(reverse("admin:search"))
    assert response.status_code == HTTPStatus.FOUND


@pytest.mark.django_db
def test_command_admin_accessible(admin_client):
    response = admin_client.get(reverse("admin:search"))
    assert response.status_code == HTTPStatus.OK


@pytest.mark.django_db
def test_command_search_empty(admin_client):
    response = admin_client.get(reverse("admin:search") + "?s=")
    assert response.status_code == HTTPStatus.OK


@pytest.mark.django_db
def test_command_search_non_existing_record(admin_client):
    response = admin_client.get(
        reverse("admin:search") + "?s=non-existing-record&extended=1"
    )
    assert response.status_code == HTTPStatus.OK
    assert "No results matching your query" in response.content.decode()


@override_settings(
    UNFOLD={
        **CONFIG_DEFAULTS,
        **{
            "COMMAND": {
                "search_models": True,
            }
        },
    }
)
@pytest.mark.django_db
def test_command_search_extended_models(admin_client, tag_factory):
    tag_factory(name="test-tagasdfsadf")
    response = admin_client.get(reverse("admin:search") + "?s=test-tag&extended=1")

    assert response.status_code == HTTPStatus.OK
    assert "test-tag" in response.content.decode()


@override_settings(
    UNFOLD={
        **CONFIG_DEFAULTS,
        **{
            "COMMAND": {
                "search_models": True,
            }
        },
    }
)
@pytest.mark.django_db
def test_command_search_extended_model_without_permission(
    client, staff_user, tag_factory
):
    client.force_login(staff_user)
    tag_factory(name="sample-test-tag")
    response = client.get(reverse("admin:search") + "?s=sample-test-tag&extended=1")
    assert response.status_code == HTTPStatus.OK
    assert "sample-test-tag" not in response.content.decode()


@override_settings(
    UNFOLD={
        **CONFIG_DEFAULTS,
        **{
            "COMMAND": {
                "search_models": True,
            }
        },
    }
)
@pytest.mark.django_db
def test_command_search_extended_model_with_permission(
    admin_client, staff_user, tag_factory
):
    # Add view tags permission to staff user
    view_tag_permission = Permission.objects.get(codename="view_tag")
    staff_user.user_permissions.add(view_tag_permission)

    admin_client.force_login(staff_user)
    tag_factory(name="sample-test-tag-with-permission")
    response = admin_client.get(
        reverse("admin:search") + "?s=sample-test-tag-with-permission&extended=1"
    )
    assert response.status_code == HTTPStatus.OK
    assert "sample-test-tag-with-permission" in response.content.decode()
