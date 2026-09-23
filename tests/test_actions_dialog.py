from http import HTTPStatus

import pytest
from django.urls import reverse_lazy


@pytest.mark.django_db
@pytest.mark.parametrize(
    "action",
    [
        "changelist_dialog_action_without_custom_form",
        "changelist_dialog_action_with_custom_form",
        ("row_dialog_action_without_custom_form", 1),
        ("row_dialog_action_with_custom_form", 1),
        ("changeform_dialog_action_without_custom_form", 1),
        ("changeform_dialog_action_with_custom_form", 1),
    ],
)
def test_dialog_actions_anonymous(action, client):
    if isinstance(action, tuple):
        url = reverse_lazy(
            f"admin:example_dialogactionuser_{action[0]}", args=[action[1]]
        )
    else:
        url = reverse_lazy(f"admin:example_dialogactionuser_{action}")

    response = client.get(url, follow=True)

    assert response.status_code == HTTPStatus.OK
    assert response.wsgi_request.path == "/admin/login/"
    assert "Action successfully executed" not in response.content.decode()

    response = client.post(
        url,
        {
            "_form_submitted": True,
        },
        follow=True,
    )
    assert response.status_code == HTTPStatus.OK
    assert response.wsgi_request.path == "/admin/login/"
    assert "Action successfully executed" not in response.content.decode()


@pytest.mark.django_db
@pytest.mark.parametrize(
    "action",
    [
        "changelist_dialog_action_without_custom_form",
        ("row_dialog_action_without_custom_form", 1),
        ("changeform_dialog_action_without_custom_form", 1),
    ],
)
def test_dialog_actions_without_form_submitted(admin_client, action):
    if isinstance(action, tuple):
        url = reverse_lazy(
            f"admin:example_dialogactionuser_{action[0]}", args=[action[1]]
        )
    else:
        url = reverse_lazy(f"admin:example_dialogactionuser_{action}")

    response = admin_client.post(
        url,
        {
            "_form_submitted": True,
        },
        follow=True,
    )
    assert response.status_code == HTTPStatus.OK
    assert "HX-Redirect" in response.headers
    assert response.headers["HX-Redirect"] == reverse_lazy(
        "admin:example_dialogactionuser_changelist"
    )

    response = admin_client.get(
        reverse_lazy("admin:example_dialogactionuser_changelist"),
    )

    assert response.status_code == HTTPStatus.OK
    assert "Action successfully executed" in response.content.decode()


@pytest.mark.django_db
@pytest.mark.parametrize(
    "action",
    [
        "changelist_dialog_action_without_custom_form",
        ("row_dialog_action_without_custom_form", 1),
        ("changeform_dialog_action_without_custom_form", 1),
    ],
)
def test_dialog_actions_without_clicking_on_submit_button(admin_client, action):
    if isinstance(action, tuple):
        url = reverse_lazy(
            f"admin:example_dialogactionuser_{action[0]}", args=[action[1]]
        )
    else:
        url = reverse_lazy(f"admin:example_dialogactionuser_{action}")

    response = admin_client.post(
        url,
        {
            "_form_submitted": False,
        },
        follow=True,
    )
    assert response.status_code == HTTPStatus.OK
    assert "HX-Redirect" not in response.headers

    response = admin_client.get(
        reverse_lazy("admin:example_dialogactionuser_changelist"),
    )

    assert response.status_code == HTTPStatus.OK
    assert "Action successfully executed" not in response.content.decode()


@pytest.mark.django_db
@pytest.mark.parametrize(
    "action",
    [
        "changelist_dialog_action_with_custom_form",
        ("row_dialog_action_with_custom_form", 1),
        ("changeform_dialog_action_with_custom_form", 1),
    ],
)
def test_dialog_actions_with_form_submitted(action, admin_client):
    if isinstance(action, tuple):
        url = reverse_lazy(
            f"admin:example_dialogactionuser_{action[0]}", args=[action[1]]
        )
    else:
        url = reverse_lazy(f"admin:example_dialogactionuser_{action}")

    response = admin_client.post(
        url,
        {
            "confirm": "CONFIRM",
            "_form_submitted": True,
        },
    )
    assert response.status_code == HTTPStatus.OK
    assert "HX-Redirect" in response.headers
    assert response.headers["HX-Redirect"] == reverse_lazy(
        "admin:example_dialogactionuser_changelist"
    )

    response = admin_client.get(
        reverse_lazy("admin:example_dialogactionuser_changelist"),
    )

    assert response.status_code == HTTPStatus.OK
    assert "Action successfully executed" in response.content.decode()


@pytest.mark.django_db
@pytest.mark.parametrize(
    "action",
    [
        "changelist_dialog_action_with_custom_form",
        ("row_dialog_action_with_custom_form", 1),
        ("changeform_dialog_action_with_custom_form", 1),
    ],
)
def test_dialog_actions_with_form_validation_error(action, admin_client):
    if isinstance(action, tuple):
        url = reverse_lazy(
            f"admin:example_dialogactionuser_{action[0]}", args=[action[1]]
        )
    else:
        url = reverse_lazy(f"admin:example_dialogactionuser_{action}")

    response = admin_client.post(
        url,
        {
            "_form_submitted": True,
        },
    )
    assert response.status_code == HTTPStatus.OK
    assert "HX-Redirect" not in response.headers
    assert "This field is required." in response.content.decode()


@pytest.mark.django_db
@pytest.mark.parametrize(
    "action",
    [
        "changelist_dialog_action_with_custom_form",
        ("row_dialog_action_with_custom_form", 1),
        ("changeform_dialog_action_with_custom_form", 1),
    ],
)
def test_dialog_actions_with_form_custom_validation_error(action, admin_client):
    if isinstance(action, tuple):
        url = reverse_lazy(
            f"admin:example_dialogactionuser_{action[0]}", args=[action[1]]
        )
    else:
        url = reverse_lazy(f"admin:example_dialogactionuser_{action}")

    response = admin_client.post(
        url,
        {
            "confirm": "INVALID",
            "_form_submitted": True,
        },
    )
    assert response.status_code == HTTPStatus.OK
    assert "HX-Redirect" not in response.headers
    assert "You must confirm to proceed." in response.content.decode()


def test_dialog_actions_with_permissions_returning_true(admin_client):
    response = admin_client.post(
        reverse_lazy(
            "admin:example_dialogactionuser_changelist_dialog_action_with_permissions_true"
        ),
        {
            "_form_submitted": True,
        },
    )
    assert response.status_code == HTTPStatus.OK
    assert "HX-Redirect" in response.headers
    assert response.headers["HX-Redirect"] == reverse_lazy(
        "admin:example_dialogactionuser_changelist"
    )

    response = admin_client.get(
        reverse_lazy("admin:example_dialogactionuser_changelist"),
    )

    assert response.status_code == HTTPStatus.OK
    assert "Action successfully executed" in response.content.decode()


def test_dialog_actions_with_permissions_returning_false(admin_client):
    response = admin_client.post(
        reverse_lazy(
            "admin:example_dialogactionuser_changelist_dialog_action_with_permissions_false"
        ),
        {
            "_form_submitted": True,
        },
    )
    assert response.status_code == HTTPStatus.FORBIDDEN
    assert "HX-Redirect" not in response.headers
