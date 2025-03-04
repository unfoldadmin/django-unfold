from http import HTTPStatus

import pytest
from django.urls import reverse_lazy


@pytest.mark.django_db
def test_sections_template(client, admin_user, user_model_admin_with_actions):
    client.force_login(admin_user)
    response = client.get(reverse_lazy("admin:example_user_changelist"))
    assert response.status_code == HTTPStatus.OK
    assert "Section template successfully rendered" in response.content.decode()


@pytest.mark.django_db
def test_sections_related_table(client, admin_user, user_model_admin_with_actions):
    client.force_login(admin_user)
    response = client.get(reverse_lazy("admin:example_user_changelist"))

    assert response.status_code == HTTPStatus.OK
    assert "Related log entries" in response.content.decode()
    assert "No data" in response.content.decode()
