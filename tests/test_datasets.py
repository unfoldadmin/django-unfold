from http import HTTPStatus

from django.urls import reverse
from example.models import Project


def test_datasets_no_selected_items(admin_client):
    response = admin_client.post(
        reverse("admin:example_user_change", args=[1]),
        {
            "_dataset": "ProjectDataset",
        },
        follow=True,
    )

    assert response.status_code == HTTPStatus.OK
    assert (
        "Items must be selected in order to perform actions on them. No items have been changed."
        in response.content.decode()
    )


def test_datasets_no_dataset_found(admin_client, project_factory):
    project = project_factory(name="Test Project")

    response = admin_client.post(
        reverse("admin:example_user_change", args=[1]),
        {
            "_selected_action": [project.pk],
            "_dataset": "NonExistingDataset",
        },
        follow=True,
    )

    assert response.status_code == HTTPStatus.OK
    assert "Dataset not found. No action performed." in response.content.decode()


def test_datasets_success_action(admin_client, project_factory):
    project = project_factory(name="Test Project")

    response = admin_client.post(
        reverse("admin:example_user_change", args=[1]),
        {
            "_selected_action": [project.pk],
            "_dataset": "ProjectDataset",
            "action": "delete_selected",
        },
        follow=True,
    )

    assert response.status_code == HTTPStatus.OK


def test_datasets_delete_selected_confirmation(admin_client, project_factory):
    project1 = project_factory(name="Test Project")
    project2 = project_factory(name="Another Project")

    response = admin_client.post(
        reverse("admin:example_user_change", args=[1]),
        {
            "_selected_action": [project1.pk, project2.pk],
            "_dataset": "ProjectDataset",
            "action": "delete_selected",
        },
        follow=True,
    )

    assert response.status_code == HTTPStatus.OK
    content = response.content.decode()
    assert 'name="_dataset"' in content
    assert "ProjectDataset" in content
    assert project1.name in content
    assert project2.name in content

    response = admin_client.post(
        reverse("admin:example_user_change", args=[1]),
        {
            "_selected_action": [project1.pk, project2.pk],
            "_dataset": "ProjectDataset",
            "action": "delete_selected",
            "post": "yes",
        },
        follow=True,
    )

    assert response.status_code == HTTPStatus.OK
    assert Project.objects.all().count() == 0
