from http import HTTPStatus

import pytest
from django.urls import reverse_lazy


@pytest.mark.django_db
def test_sections_template(admin_client):
    response = admin_client.get(reverse_lazy("admin:example_sectionuser_changelist"))
    assert response.status_code == HTTPStatus.OK
    assert "Section template successfully rendered" in response.content.decode()


@pytest.mark.django_db
def test_sections_related_table(admin_client):
    response = admin_client.get(reverse_lazy("admin:example_sectionuser_changelist"))
    assert response.status_code == HTTPStatus.OK
    assert "Related log entries" in response.content.decode()
    assert "No data" in response.content.decode()
