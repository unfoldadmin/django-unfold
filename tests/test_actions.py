from http import HTTPStatus

import pytest
from django.urls import reverse_lazy


######################################################################
# Changelist actions
######################################################################
@pytest.mark.django_db
def test_actions_list_anonymous(client, user_model_admin_with_actions):
    response = client.get(
        reverse_lazy("admin:example_user_changelist_action"), follow=True
    )
    assert response.status_code == HTTPStatus.OK
    assert response.wsgi_request.path == "/admin/login/"


@pytest.mark.django_db
def test_actions_list(client, admin_user, user_model_admin_with_actions):
    client.force_login(admin_user)
    response = client.get(reverse_lazy("admin:example_user_changelist"))

    assert response.status_code == HTTPStatus.OK
    assert "Changelist action" in response.content.decode()

    response = client.get(
        reverse_lazy("admin:example_user_changelist_action"), follow=True
    )
    assert response.status_code == HTTPStatus.OK
    assert "Changelist action successfully executed" in response.content.decode()


@pytest.mark.django_db
def test_actions_list_with_dropdown(client, admin_user, user_model_admin_with_actions):
    client.force_login(admin_user)
    response = client.get(reverse_lazy("admin:example_user_changelist"))

    assert response.status_code == HTTPStatus.OK
    assert "Changelist dropdown for actions" in response.content.decode()
    assert "Changelist action dropdown" in response.content.decode()

    response = client.get(
        reverse_lazy("admin:example_user_changelist_action_dropdown"),
        follow=True,
    )
    assert response.status_code == HTTPStatus.OK
    assert (
        "Changelist action dropdown successfully executed" in response.content.decode()
    )


@pytest.mark.django_db
def test_actions_list_permission_true(
    client, admin_user, user_model_admin_with_actions
):
    client.force_login(admin_user)
    response = client.get(reverse_lazy("admin:example_user_changelist"))

    assert response.status_code == HTTPStatus.OK
    assert "Changelist action permission true" in response.content.decode()

    response = client.get(
        reverse_lazy("admin:example_user_changelist_action_permission_true"),
        follow=True,
    )
    assert response.status_code == HTTPStatus.OK
    assert (
        "Changelist action with true permission successfully executed"
        in response.content.decode()
    )


@pytest.mark.django_db
def test_actions_list_permission_false(
    client, admin_user, user_model_admin_with_actions
):
    client.force_login(admin_user)
    response = client.get(reverse_lazy("admin:example_user_changelist"))

    assert response.status_code == HTTPStatus.OK
    assert "Changelist action permission false" not in response.content.decode()

    response = client.get(
        reverse_lazy("admin:example_user_changelist_action_permission_false"),
        follow=True,
    )
    assert response.status_code == HTTPStatus.FORBIDDEN
    assert (
        "Changelist action with false permission successfully executed"
        not in response.content.decode()
    )


@pytest.mark.django_db
def test_actions_list_multiple_different_permissions(
    client, admin_user, user_model_admin_with_actions
):
    client.force_login(admin_user)
    response = client.get(reverse_lazy("admin:example_user_changelist"))

    assert response.status_code == HTTPStatus.OK
    assert (
        "Changelist action with multiple permissions" not in response.content.decode()
    )

    response = client.get(
        reverse_lazy(
            "admin:example_user_changelist_action_multiple_different_permissions"
        ),
        follow=True,
    )
    assert response.status_code == HTTPStatus.FORBIDDEN
    assert (
        "Changelist action with multiple different permissions successfully executed"
        not in response.content.decode()
    )


######################################################################
# Changelist row actions
######################################################################
@pytest.mark.django_db
def test_actions_row_anonymous(client, admin_user, user_model_admin_with_actions):
    response = client.get(
        reverse_lazy("admin:example_user_changelist_row_action", args=(admin_user.pk,)),
        follow=True,
    )
    assert response.status_code == HTTPStatus.OK
    assert response.wsgi_request.path == "/admin/login/"


@pytest.mark.django_db
def test_actions_row(client, admin_user, user_model_admin_with_actions):
    client.force_login(admin_user)
    response = client.get(reverse_lazy("admin:example_user_changelist"))

    assert response.status_code == HTTPStatus.OK
    assert "Changelist row action" in response.content.decode()

    response = client.get(
        reverse_lazy("admin:example_user_changelist_row_action", args=(admin_user.pk,)),
        follow=True,
    )
    assert response.status_code == HTTPStatus.OK
    assert "Changelist row action successfully executed" in response.content.decode()


@pytest.mark.django_db
def test_actions_row_permission_true(client, admin_user, user_model_admin_with_actions):
    client.force_login(admin_user)
    response = client.get(reverse_lazy("admin:example_user_changelist"))

    assert response.status_code == HTTPStatus.OK
    assert "Changelist row action permission true" in response.content.decode()

    response = client.get(
        reverse_lazy(
            "admin:example_user_changelist_row_action_permission_true",
            args=(admin_user.pk,),
        ),
        follow=True,
    )
    assert response.status_code == HTTPStatus.OK
    assert (
        "Changelist row action with true permission successfully executed"
        in response.content.decode()
    )


@pytest.mark.django_db
def test_actions_row_permission_false(
    client, admin_user, user_model_admin_with_actions
):
    client.force_login(admin_user)
    response = client.get(reverse_lazy("admin:example_user_changelist"))

    assert response.status_code == HTTPStatus.OK
    assert "Changelist row action permission false" not in response.content.decode()

    response = client.get(
        reverse_lazy(
            "admin:example_user_changelist_row_action_permission_false",
            args=(admin_user.pk,),
        ),
        follow=True,
    )
    assert response.status_code == HTTPStatus.FORBIDDEN
    assert (
        "Changelist row action with false permission successfully executed"
        not in response.content.decode()
    )


@pytest.mark.django_db
def test_actions_row_multiple_different_permissions(
    client, admin_user, user_model_admin_with_actions
):
    client.force_login(admin_user)
    response = client.get(reverse_lazy("admin:example_user_changelist"))

    assert response.status_code == HTTPStatus.OK
    assert (
        "Changelist row action with multiple permissions"
        not in response.content.decode()
    )

    response = client.get(
        reverse_lazy(
            "admin:example_user_changelist_row_action_multiple_different_permissions",
            args=(admin_user.pk,),
        ),
        follow=True,
    )
    assert response.status_code == HTTPStatus.FORBIDDEN
    assert (
        "Changelist row action with multiple different permissions successfully executed"
        not in response.content.decode()
    )


######################################################################
# Changeform actions
######################################################################
@pytest.mark.django_db
def test_actions_changeform_anonymous(
    client, admin_user, user_model_admin_with_actions
):
    response = client.get(
        reverse_lazy("admin:example_user_changeform_action", args=(admin_user.pk,)),
        follow=True,
    )
    assert response.status_code == HTTPStatus.OK
    assert response.wsgi_request.path == "/admin/login/"


@pytest.mark.django_db
def test_actions_changeform(client, admin_user, user_model_admin_with_actions):
    client.force_login(admin_user)
    response = client.get(
        reverse_lazy("admin:example_user_change", args=(admin_user.pk,))
    )

    assert response.status_code == HTTPStatus.OK
    assert "Changeform action" in response.content.decode()

    response = client.get(
        reverse_lazy("admin:example_user_changeform_action", args=(admin_user.pk,)),
        follow=True,
    )
    assert response.status_code == HTTPStatus.OK
    assert "Changeform action successfully executed" in response.content.decode()


@pytest.mark.django_db
def test_actions_changeform_with_dropdown(
    client, admin_user, user_model_admin_with_actions
):
    client.force_login(admin_user)
    response = client.get(
        reverse_lazy("admin:example_user_change", args=(admin_user.pk,))
    )

    assert response.status_code == HTTPStatus.OK
    assert "Changeform dropdown for actions" in response.content.decode()
    assert "Changeform action dropdown" in response.content.decode()

    response = client.get(
        reverse_lazy(
            "admin:example_user_changeform_action_dropdown", args=(admin_user.pk,)
        ),
        follow=True,
    )
    assert response.status_code == HTTPStatus.OK
    assert (
        "Changeform action dropdown successfully executed" in response.content.decode()
    )


@pytest.mark.django_db
def test_actions_changeform_permission_true(
    client, admin_user, user_model_admin_with_actions
):
    client.force_login(admin_user)
    response = client.get(
        reverse_lazy("admin:example_user_change", args=(admin_user.pk,))
    )

    assert response.status_code == HTTPStatus.OK
    assert "Changeform action permission true" in response.content.decode()

    response = client.get(
        reverse_lazy(
            "admin:example_user_changeform_action_permission_true",
            args=(admin_user.pk,),
        ),
        follow=True,
    )
    assert response.status_code == HTTPStatus.OK
    assert (
        "Changeform action with true permission successfully executed"
        in response.content.decode()
    )


@pytest.mark.django_db
def test_actions_changeform_permission_false(
    client, admin_user, user_model_admin_with_actions
):
    client.force_login(admin_user)
    response = client.get(
        reverse_lazy("admin:example_user_change", args=(admin_user.pk,))
    )

    assert response.status_code == HTTPStatus.OK
    assert "Changeform action permission false" not in response.content.decode()

    response = client.get(
        reverse_lazy(
            "admin:example_user_changeform_action_permission_false",
            args=(admin_user.pk,),
        ),
        follow=True,
    )
    assert response.status_code == HTTPStatus.FORBIDDEN
    assert (
        "Changeform action with false permission successfully executed"
        not in response.content.decode()
    )


@pytest.mark.django_db
def test_changeform_multiple_different_permissions(
    client, admin_user, user_model_admin_with_actions
):
    client.force_login(admin_user)
    response = client.get(
        reverse_lazy("admin:example_user_change", args=(admin_user.pk,))
    )

    assert response.status_code == HTTPStatus.OK
    assert (
        "Changeform action with multiple permissions" not in response.content.decode()
    )

    response = client.get(
        reverse_lazy(
            "admin:example_user_changeform_action_multiple_different_permissions",
            args=(admin_user.pk,),
        ),
        follow=True,
    )
    assert response.status_code == HTTPStatus.FORBIDDEN
    assert (
        "Changeform action with multiple different permissions successfully executed"
        not in response.content.decode()
    )


######################################################################
# Submit line actions
######################################################################
@pytest.mark.django_db
def test_submit_line(client, admin_user, user_model_admin_with_actions):
    client.force_login(admin_user)
    response = client.get(
        reverse_lazy("admin:example_user_change", args=(admin_user.pk,))
    )
    assert response.status_code == HTTPStatus.OK
    assert "Submit line action" in response.content.decode()

    response = client.post(
        reverse_lazy("admin:example_user_change", args=(admin_user.pk,)),
        {
            "username": admin_user.username,
            "date_joined_0": "2025-01-01",
            "date_joined_1": "12:00",
            "is_active": True,
            "is_staff": True,
            "is_superuser": True,
            "example_user_submit_line_action": "1",
        },
        follow=True,
    )

    assert response.status_code == HTTPStatus.OK
    assert "Submit line action successfully executed" in response.content.decode()


@pytest.mark.django_db
def test_submit_line_permission_true(client, admin_user, user_model_admin_with_actions):
    client.force_login(admin_user)
    response = client.get(
        reverse_lazy("admin:example_user_change", args=(admin_user.pk,))
    )
    assert response.status_code == HTTPStatus.OK
    assert "Submit line action permission true" in response.content.decode()

    response = client.post(
        reverse_lazy("admin:example_user_change", args=(admin_user.pk,)),
        {
            "username": admin_user.username,
            "date_joined_0": "2025-01-01",
            "date_joined_1": "12:00",
            "is_active": True,
            "is_staff": True,
            "is_superuser": True,
            "example_user_submit_line_action_permission_true": "1",
        },
        follow=True,
    )

    assert response.status_code == HTTPStatus.OK
    assert (
        "Submit line action with true permission successfully executed"
        in response.content.decode()
    )


@pytest.mark.django_db
def test_submit_line_permission_false(
    client, admin_user, user_model_admin_with_actions
):
    client.force_login(admin_user)
    response = client.get(
        reverse_lazy("admin:example_user_change", args=(admin_user.pk,))
    )
    assert response.status_code == HTTPStatus.OK
    assert "Submit line action permission false" not in response.content.decode()

    response = client.post(
        reverse_lazy("admin:example_user_change", args=(admin_user.pk,)),
        {
            "username": admin_user.username,
            "date_joined_0": "2025-01-01",
            "date_joined_1": "12:00",
            "is_active": True,
            "is_staff": True,
            "is_superuser": True,
            "example_user_submit_line_action_permission_false": "1",
        },
        follow=True,
    )

    assert response.status_code == HTTPStatus.OK
    assert (
        "Submit line action with false permission successfully executed"
        not in response.content.decode()
    )


@pytest.mark.django_db
def test_submit_line_multiple_different_permissions(
    client, admin_user, user_model_admin_with_actions
):
    client.force_login(admin_user)
    response = client.get(
        reverse_lazy("admin:example_user_change", args=(admin_user.pk,))
    )
    assert response.status_code == HTTPStatus.OK
    assert (
        "Submit line action with multiple permissions" not in response.content.decode()
    )

    response = client.post(
        reverse_lazy("admin:example_user_change", args=(admin_user.pk,)),
        {
            "username": admin_user.username,
            "date_joined_0": "2025-01-01",
            "date_joined_1": "12:00",
            "is_active": True,
            "is_staff": True,
            "is_superuser": True,
            "example_user_submit_line_action_multiple_different_permissions": "1",
        },
        follow=True,
    )

    assert response.status_code == HTTPStatus.OK
    assert (
        "Submit line action with multiple different permissions successfully executed"
        not in response.content.decode()
    )
