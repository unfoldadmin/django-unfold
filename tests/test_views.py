from http import HTTPStatus

import pytest
from django.urls import reverse


def test_site_extra_url_view(admin_client):
    url = reverse("admin:extra_url_name")
    assert url == "/admin/extra-url"

    response = admin_client.get(url)

    assert response.status_code == HTTPStatus.OK
    assert response.template_name[0] == "site_extra_view.html"
    assert response.context["title"] == "Site Extra URL"
    assert "Extra view content" in response.content.decode()


def test_site_extra_url_view_anonymous_user(client):
    response = client.get(reverse("admin:extra_url_name"), follow=True)

    assert response.wsgi_request.path == "/admin/login/"
    assert "Welcome back to" in response.content.decode()
    assert "Log in" in response.content.decode()
    assert response.status_code == HTTPStatus.OK


@pytest.mark.django_db
def test_site_extra_url_view_not_enough_permissions(settings, client, staff_user):
    client.force_login(staff_user)
    response = client.get(reverse("admin:extra_url_name"))

    assert response.status_code == HTTPStatus.FORBIDDEN


def test_model_extra_url_view(admin_client):
    url = reverse("admin:custom_url_name")
    assert url == "/admin/example/project/extra-url"

    response = admin_client.get(url)

    assert response.status_code == HTTPStatus.OK
    assert response.template_name[0] == "model_extra_view.html"
    assert response.context["title"] == "Model Extra URL"
    assert "Model view content" in response.content.decode()


def test_model_extra_url_view_anonymous_user(client):
    response = client.get(reverse("admin:custom_url_name"), follow=True)

    assert response.wsgi_request.path == "/admin/login/"
    assert "Welcome back to" in response.content.decode()
    assert "Log in" in response.content.decode()
    assert response.status_code == HTTPStatus.OK


@pytest.mark.django_db
def test_model_extra_url_view_not_enough_permissions(settings, client, staff_user):
    client.force_login(staff_user)
    response = client.get(reverse("admin:custom_url_name"))

    assert response.status_code == HTTPStatus.FORBIDDEN


def test_changelist_view_anonymous_user(client):
    response = client.get(reverse("admin:example_project_changelist"), follow=True)

    assert response.wsgi_request.path == "/admin/login/"
    assert "Welcome back to" in response.content.decode()
    assert "Log in" in response.content.decode()
    assert response.status_code == HTTPStatus.OK


@pytest.mark.django_db
def test_changelist_view_regular_user(client, regular_user):
    client.force_login(regular_user)
    response = client.get(reverse("admin:example_project_changelist"), follow=True)

    assert response.wsgi_request.path == "/admin/login/"
    assert "Welcome back to" in response.content.decode()
    assert "Log in" in response.content.decode()
    assert response.status_code == HTTPStatus.OK


@pytest.mark.django_db
def test_changelist_view_staff_user(settings, client, staff_user):
    client.force_login(staff_user)
    response = client.get(reverse("admin:example_project_changelist"))
    assert response.status_code == HTTPStatus.FORBIDDEN


@pytest.mark.django_db
def test_changelist_view_super_user(admin_client, staff_user):
    response = admin_client.get(
        reverse("admin:example_project_changelist"), follow=True
    )
    assert response.status_code == HTTPStatus.OK
    assert "Select project to change | Django site admin" in response.content.decode()


@pytest.mark.django_db
def test_changeform_view_anonymous_user(client, project_factory):
    project = project_factory()
    response = client.get(
        reverse("admin:example_project_change", args=[project.id]), follow=True
    )

    assert response.wsgi_request.path == "/admin/login/"
    assert "Welcome back to" in response.content.decode()
    assert "Log in" in response.content.decode()
    assert response.status_code == HTTPStatus.OK


@pytest.mark.django_db
def test_changeform_view_regular_user(client, regular_user, project_factory):
    client.force_login(regular_user)
    project = project_factory()
    response = client.get(
        reverse("admin:example_project_change", args=[project.id]), follow=True
    )

    assert response.wsgi_request.path == "/admin/login/"
    assert "Welcome back to" in response.content.decode()
    assert "Log in" in response.content.decode()
    assert response.status_code == HTTPStatus.OK


@pytest.mark.django_db
def test_changeform_staff_user(settings, client, staff_user, project_factory):
    project = project_factory()
    client.force_login(staff_user)
    response = client.get(reverse("admin:example_project_change", args=[project.id]))
    assert response.status_code == HTTPStatus.FORBIDDEN


@pytest.mark.django_db
def test_changeform_view_super_user(admin_client, project_factory):
    project = project_factory()
    response = admin_client.get(
        reverse("admin:example_project_change", args=[project.id]), follow=True
    )

    assert response.status_code == HTTPStatus.OK
    assert (
        f"{project.name} | Change project | Django site admin"
        in response.content.decode()
    )
