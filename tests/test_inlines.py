from http import HTTPStatus

import pytest
from django.urls import reverse

from .factories import TagFactory


@pytest.mark.django_db
def test_inline_pagination(client, admin_user):
    tags_count = 50
    client.force_login(admin_user)

    for i in range(tags_count):
        tag = TagFactory(name=f"Tag {i}")
        admin_user.tags.add(tag)

    response = client.get(reverse("admin:example_user_change", args=(admin_user.pk,)))

    assert response.status_code == HTTPStatus.OK
    assert f"{tags_count} user-tag relationships" in response.content.decode()


@pytest.mark.django_db
def test_inline_pagination_no_relationships(client, admin_user):
    client.force_login(admin_user)
    response = client.get(reverse("admin:example_user_change", args=(admin_user.pk,)))
    assert response.status_code == HTTPStatus.OK

    assert "user-tag" not in response.content.decode()


@pytest.mark.django_db
def test_inline_pagination_one_relationship(client, admin_user):
    tag = TagFactory(name="Tag 1")
    admin_user.tags.add(tag)
    client.force_login(admin_user)

    response = client.get(reverse("admin:example_user_change", args=(admin_user.pk,)))
    assert response.status_code == HTTPStatus.OK
    assert "user-tag" not in response.content.decode()


@pytest.mark.django_db
def test_inline_collapsible(client, admin_user):
    tag = TagFactory(name="Tag 1")
    admin_user.tags.add(tag)
    client.force_login(admin_user)

    response = client.get(reverse("admin:example_user_change", args=(admin_user.pk,)))
    assert response.status_code == HTTPStatus.OK
    assert 'x-on:click="open = !open' in response.content.decode()
