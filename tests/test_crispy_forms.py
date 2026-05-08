from http import HTTPStatus

import pytest
from django.urls import reverse


@pytest.mark.django_db
def test_crispy_forms_anonymous_user(client):
    response = client.get(reverse("admin:crispy_form"))
    assert response.status_code == HTTPStatus.FOUND

    response = client.get(reverse("admin:crispy_form"), follow=True)
    assert response.status_code == HTTPStatus.OK
    assert response.wsgi_request.path == "/admin/login/"
    assert "Log in" in response.content.decode()
    assert "Welcome back to" in response.content.decode()


@pytest.mark.django_db
def test_crispy_forms_staff_user(client, staff_user):
    client.force_login(staff_user)
    response = client.get(reverse("admin:crispy_form"))
    assert response.status_code == HTTPStatus.FORBIDDEN
    assert "Crispy form" not in response.content.decode()


@pytest.mark.django_db
def test_crispy_forms_authenticated_user(admin_client):
    response = admin_client.get(reverse("admin:crispy_form"))
    assert response.status_code == HTTPStatus.OK
    assert "Crispy form" in response.content.decode()
