from http import HTTPStatus

from django.urls import reverse


def test_import_export_import_form(admin_client):
    response = admin_client.get(reverse("admin:example_user_import"))
    assert response.status_code == HTTPStatus.OK
    assert (
        '<label for="id_import_file" class="block font-semibold text-font-important-light dark:text-font-important-dark">'
        in response.content.decode()
    )


def test_import_export_export_form(admin_client):
    response = admin_client.get(reverse("admin:example_user_export"))
    assert response.status_code == HTTPStatus.OK
    assert (
        '<label for="id_format" class="block font-semibold text-font-important-light dark:text-font-important-dark">'
        in response.content.decode()
    )


def test_import_export_selectable_fields_export_form(admin_client):
    response = admin_client.get(reverse("admin:example_project_export"))
    assert response.status_code == HTTPStatus.OK
    assert (
        '<label for="id_format" class="block font-semibold text-font-important-light dark:text-font-important-dark">'
        in response.content.decode()
    )
