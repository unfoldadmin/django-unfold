from http import HTTPStatus

from django.urls import reverse


def test_datasets_no_selected_items(admin_client):
    response = admin_client.post(
        reverse("admin:example_user_change", args=[1]),
        {
            "dataset": "ProjectDataset",
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
            "dataset": "NonExistingDataset",
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
            "dataset": "ProjectDataset",
            "action": "delete_selected",
        },
        follow=True,
    )

    assert response.status_code == HTTPStatus.OK
