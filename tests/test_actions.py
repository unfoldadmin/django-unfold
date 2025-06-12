from http import HTTPStatus

import pytest
from django.urls import reverse_lazy


######################################################################
# Changelist actions
######################################################################
@pytest.mark.django_db
def test_actions_list_anonymous(client):
    response = client.get(
        reverse_lazy("admin:example_actionuser_changelist_action"), follow=True
    )
    assert response.status_code == HTTPStatus.OK
    assert response.wsgi_request.path == "/admin/login/"


@pytest.mark.django_db
def test_actions_list(client, admin_user):
    client.force_login(admin_user)
    response = client.get(reverse_lazy("admin:example_actionuser_changelist"))

    assert response.status_code == HTTPStatus.OK
    assert "Changelist action" in response.content.decode()

    response = client.get(
        reverse_lazy("admin:example_actionuser_changelist_action"), follow=True
    )
    assert response.status_code == HTTPStatus.OK
    assert "Changelist action successfully executed" in response.content.decode()


@pytest.mark.django_db
def test_actions_list_with_dropdown(client, admin_user):
    client.force_login(admin_user)
    response = client.get(reverse_lazy("admin:example_actionuser_changelist"))

    assert response.status_code == HTTPStatus.OK
    assert "Changelist dropdown for actions" in response.content.decode()
    assert "Changelist action dropdown" in response.content.decode()

    response = client.get(
        reverse_lazy("admin:example_actionuser_changelist_action_dropdown"),
        follow=True,
    )
    assert response.status_code == HTTPStatus.OK
    assert (
        "Changelist action dropdown successfully executed" in response.content.decode()
    )


@pytest.mark.django_db
def test_actions_list_mixed_permissions_true(client, staff_user):
    client.force_login(staff_user)
    response = client.get(reverse_lazy("admin:example_actionuser_changelist"))

    assert response.status_code == HTTPStatus.OK
    assert "Changelist action with mixed permissions true" in response.content.decode()

    response = client.get(
        reverse_lazy(
            "admin:example_actionuser_changelist_action_mixed_permissions_true"
        ),
        follow=True,
    )
    assert response.status_code == HTTPStatus.OK
    assert (
        "Changelist action with mixed permissions true successfully executed"
        in response.content.decode()
    )


@pytest.mark.django_db
def test_actions_list_mixed_permissions_false(client, staff_user):
    client.force_login(staff_user)
    response = client.get(reverse_lazy("admin:example_actionuser_changelist"))

    assert response.status_code == HTTPStatus.OK
    assert (
        "Changelist action with mixed permissions false"
        not in response.content.decode()
    )

    response = client.get(
        reverse_lazy(
            "admin:example_actionuser_changelist_action_mixed_permissions_false"
        ),
        follow=True,
    )
    assert response.status_code == HTTPStatus.FORBIDDEN
    assert (
        "Changelist action with mixed permissions false successfully executed"
        not in response.content.decode()
    )


@pytest.mark.django_db
def test_actions_list_mixed_permissions_perm_not_granted(client, staff_user):
    client.force_login(staff_user)
    response = client.get(reverse_lazy("admin:example_actionuser_changelist"))

    assert response.status_code == HTTPStatus.OK
    assert (
        "Changelist action with mixed permissions perm not granted"
        not in response.content.decode()
    )

    response = client.get(
        reverse_lazy(
            "admin:example_actionuser_changelist_action_mixed_permissions_perm_not_granted"
        ),
        follow=True,
    )
    assert response.status_code == HTTPStatus.FORBIDDEN
    assert (
        "Changelist action with mixed permissions perm not granted successfully executed"
        not in response.content.decode()
    )


@pytest.mark.django_db
def test_actions_list_permission_true(client, admin_user):
    client.force_login(admin_user)
    response = client.get(reverse_lazy("admin:example_actionuser_changelist"))

    assert response.status_code == HTTPStatus.OK
    assert "Changelist action permission true" in response.content.decode()

    response = client.get(
        reverse_lazy("admin:example_actionuser_changelist_action_permission_true"),
        follow=True,
    )
    assert response.status_code == HTTPStatus.OK
    assert (
        "Changelist action with true permission successfully executed"
        in response.content.decode()
    )


@pytest.mark.django_db
def test_actions_list_permission_false(client, admin_user):
    client.force_login(admin_user)
    response = client.get(reverse_lazy("admin:example_actionuser_changelist"))

    assert response.status_code == HTTPStatus.OK
    assert "Changelist action permission false" not in response.content.decode()

    response = client.get(
        reverse_lazy("admin:example_actionuser_changelist_action_permission_false"),
        follow=True,
    )
    assert response.status_code == HTTPStatus.FORBIDDEN
    assert (
        "Changelist action with false permission successfully executed"
        not in response.content.decode()
    )


@pytest.mark.django_db
def test_actions_list_multiple_different_permissions(client, admin_user):
    client.force_login(admin_user)
    response = client.get(reverse_lazy("admin:example_actionuser_changelist"))

    assert response.status_code == HTTPStatus.OK
    assert (
        "Changelist action with multiple permissions" not in response.content.decode()
    )

    response = client.get(
        reverse_lazy(
            "admin:example_actionuser_changelist_action_multiple_different_permissions"
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
def test_actions_row_anonymous(client, admin_user):
    response = client.get(
        reverse_lazy(
            "admin:example_actionuser_changelist_row_action", args=(admin_user.pk,)
        ),
        follow=True,
    )
    assert response.status_code == HTTPStatus.OK
    assert response.wsgi_request.path == "/admin/login/"


@pytest.mark.django_db
def test_actions_row(client, admin_user):
    client.force_login(admin_user)
    response = client.get(reverse_lazy("admin:example_actionuser_changelist"))

    assert response.status_code == HTTPStatus.OK
    assert "Changelist row action" in response.content.decode()

    response = client.get(
        reverse_lazy(
            "admin:example_actionuser_changelist_row_action", args=(admin_user.pk,)
        ),
        follow=True,
    )
    assert response.status_code == HTTPStatus.OK
    assert "Changelist row action successfully executed" in response.content.decode()


@pytest.mark.django_db
def test_actions_row_mixed_permissions_true(client, staff_user):
    client.force_login(staff_user)
    response = client.get(reverse_lazy("admin:example_actionuser_changelist"))

    assert response.status_code == HTTPStatus.OK
    assert (
        "Changelist row action with mixed permissions true" in response.content.decode()
    )

    response = client.get(
        reverse_lazy(
            "admin:example_actionuser_changelist_row_action_mixed_permissions_true",
            args=(staff_user.pk,),
        ),
        follow=True,
    )
    assert response.status_code == HTTPStatus.OK
    assert (
        "Changelist row action with mixed permissions true successfully executed"
        in response.content.decode()
    )


@pytest.mark.django_db
def test_actions_row_mixed_permissions_false(client, staff_user):
    client.force_login(staff_user)
    response = client.get(reverse_lazy("admin:example_actionuser_changelist"))

    assert response.status_code == HTTPStatus.OK
    assert (
        "Changelist row action with mixed permissions false"
        not in response.content.decode()
    )

    response = client.get(
        reverse_lazy(
            "admin:example_actionuser_changelist_row_action_mixed_permissions_false",
            args=(staff_user.pk,),
        ),
        follow=True,
    )
    assert response.status_code == HTTPStatus.FORBIDDEN
    assert (
        "Changelist row action with mixed permissions false successfully executed"
        not in response.content.decode()
    )


@pytest.mark.django_db
def test_actions_row_mixed_permissions_perm_not_granted(client, staff_user):
    client.force_login(staff_user)
    response = client.get(reverse_lazy("admin:example_actionuser_changelist"))

    assert response.status_code == HTTPStatus.OK
    assert (
        "Changelist row action with mixed permissions perm not granted"
        not in response.content.decode()
    )

    response = client.get(
        reverse_lazy(
            "admin:example_actionuser_changelist_row_action_mixed_permissions_perm_not_granted",
            args=(staff_user.pk,),
        ),
        follow=True,
    )
    assert response.status_code == HTTPStatus.FORBIDDEN
    assert (
        "Changelist row action with mixed permissions perm not granted successfully executed"
        not in response.content.decode()
    )


@pytest.mark.django_db
def test_actions_row_permission_true(client, admin_user):
    client.force_login(admin_user)
    response = client.get(reverse_lazy("admin:example_actionuser_changelist"))

    assert response.status_code == HTTPStatus.OK
    assert "Changelist row action permission true" in response.content.decode()

    response = client.get(
        reverse_lazy(
            "admin:example_actionuser_changelist_row_action_permission_true",
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
def test_actions_row_permission_false(client, admin_user):
    client.force_login(admin_user)
    response = client.get(reverse_lazy("admin:example_actionuser_changelist"))

    assert response.status_code == HTTPStatus.OK
    assert "Changelist row action permission false" not in response.content.decode()

    response = client.get(
        reverse_lazy(
            "admin:example_actionuser_changelist_row_action_permission_false",
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
def test_actions_row_multiple_different_permissions(client, admin_user):
    client.force_login(admin_user)
    response = client.get(reverse_lazy("admin:example_actionuser_changelist"))

    assert response.status_code == HTTPStatus.OK
    assert (
        "Changelist row action with multiple permissions"
        not in response.content.decode()
    )

    response = client.get(
        reverse_lazy(
            "admin:example_actionuser_changelist_row_action_multiple_different_permissions",
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
def test_actions_changeform_anonymous(client, admin_user):
    response = client.get(
        reverse_lazy(
            "admin:example_actionuser_changeform_action", args=(admin_user.pk,)
        ),
        follow=True,
    )
    assert response.status_code == HTTPStatus.OK
    assert response.wsgi_request.path == "/admin/login/"


@pytest.mark.django_db
def test_actions_changeform(client, admin_user):
    client.force_login(admin_user)
    response = client.get(
        reverse_lazy("admin:example_actionuser_change", args=(admin_user.pk,))
    )

    assert response.status_code == HTTPStatus.OK
    assert "Changeform action" in response.content.decode()

    response = client.get(
        reverse_lazy(
            "admin:example_actionuser_changeform_action", args=(admin_user.pk,)
        ),
        follow=True,
    )
    assert response.status_code == HTTPStatus.OK
    assert "Changeform action successfully executed" in response.content.decode()


@pytest.mark.django_db
def test_actions_changeform_with_dropdown(client, admin_user):
    client.force_login(admin_user)
    response = client.get(
        reverse_lazy("admin:example_actionuser_change", args=(admin_user.pk,))
    )

    assert response.status_code == HTTPStatus.OK
    assert "Changeform dropdown for actions" in response.content.decode()
    assert "Changeform action dropdown" in response.content.decode()

    response = client.get(
        reverse_lazy(
            "admin:example_actionuser_changeform_action_dropdown", args=(admin_user.pk,)
        ),
        follow=True,
    )
    assert response.status_code == HTTPStatus.OK
    assert (
        "Changeform action dropdown successfully executed" in response.content.decode()
    )


@pytest.mark.django_db
def test_actions_changeform_mixed_permissions_true(client, staff_user):
    client.force_login(staff_user)
    response = client.get(
        reverse_lazy("admin:example_actionuser_change", args=(staff_user.pk,))
    )

    assert response.status_code == HTTPStatus.OK
    assert "Changeform action with mixed permissions true" in response.content.decode()

    response = client.get(
        reverse_lazy(
            "admin:example_actionuser_changeform_action_mixed_permissions_true",
            args=(staff_user.pk,),
        ),
        follow=True,
    )
    assert response.status_code == HTTPStatus.OK
    assert (
        "Changeform action with mixed permissions true successfully executed"
        in response.content.decode()
    )


@pytest.mark.django_db
def test_actions_changeform_mixed_permissions_false(client, staff_user):
    client.force_login(staff_user)
    response = client.get(
        reverse_lazy("admin:example_actionuser_change", args=(staff_user.pk,))
    )

    assert response.status_code == HTTPStatus.OK
    assert (
        "Changeform action with mixed permissions false"
        not in response.content.decode()
    )

    response = client.get(
        reverse_lazy(
            "admin:example_actionuser_changeform_action_mixed_permissions_false",
            args=(staff_user.pk,),
        ),
        follow=True,
    )
    assert response.status_code == HTTPStatus.FORBIDDEN
    assert (
        "Changeform action with mixed permissions false successfully executed"
        not in response.content.decode()
    )


@pytest.mark.django_db
def test_actions_changeform_mixed_permissions_perm_not_granted(client, staff_user):
    client.force_login(staff_user)
    response = client.get(
        reverse_lazy("admin:example_actionuser_change", args=(staff_user.pk,))
    )

    assert response.status_code == HTTPStatus.OK
    assert (
        "Changeform action with mixed permissions perm not granted"
        not in response.content.decode()
    )

    response = client.get(
        reverse_lazy(
            "admin:example_actionuser_changeform_action_mixed_permissions_perm_not_granted",
            args=(staff_user.pk,),
        ),
        follow=True,
    )
    assert response.status_code == HTTPStatus.FORBIDDEN
    assert (
        "Changeform action with mixed permissions perm not granted successfully executed"
        not in response.content.decode()
    )


@pytest.mark.django_db
def test_actions_changeform_permission_true(client, admin_user):
    client.force_login(admin_user)
    response = client.get(
        reverse_lazy("admin:example_actionuser_change", args=(admin_user.pk,))
    )

    assert response.status_code == HTTPStatus.OK
    assert "Changeform action permission true" in response.content.decode()

    response = client.get(
        reverse_lazy(
            "admin:example_actionuser_changeform_action_permission_true",
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
def test_actions_changeform_permission_false(client, admin_user):
    client.force_login(admin_user)
    response = client.get(
        reverse_lazy("admin:example_actionuser_change", args=(admin_user.pk,))
    )

    assert response.status_code == HTTPStatus.OK
    assert "Changeform action permission false" not in response.content.decode()

    response = client.get(
        reverse_lazy(
            "admin:example_actionuser_changeform_action_permission_false",
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
def test_changeform_multiple_different_permissions(client, admin_user):
    client.force_login(admin_user)
    response = client.get(
        reverse_lazy("admin:example_actionuser_change", args=(admin_user.pk,))
    )

    assert response.status_code == HTTPStatus.OK
    assert (
        "Changeform action with multiple permissions" not in response.content.decode()
    )

    response = client.get(
        reverse_lazy(
            "admin:example_actionuser_changeform_action_multiple_different_permissions",
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
def test_submit_line(client, admin_user):
    client.force_login(admin_user)
    response = client.get(
        reverse_lazy("admin:example_actionuser_change", args=(admin_user.pk,))
    )
    assert response.status_code == HTTPStatus.OK
    assert "Submit line action" in response.content.decode()

    response = client.post(
        reverse_lazy("admin:example_actionuser_change", args=(admin_user.pk,)),
        {
            "username": admin_user.username,
            "date_joined_0": "2025-01-01",
            "date_joined_1": "12:00",
            "is_active": True,
            "is_staff": True,
            "is_superuser": True,
            "example_actionuser_submit_line_action": "1",
        },
        follow=True,
    )

    assert response.status_code == HTTPStatus.OK
    assert "Submit line action successfully executed" in response.content.decode()


@pytest.mark.django_db
def test_submit_line_mixed_permissions_true(client, staff_user):
    client.force_login(staff_user)
    response = client.get(
        reverse_lazy("admin:example_actionuser_change", args=(staff_user.pk,))
    )
    assert response.status_code == HTTPStatus.OK
    assert "Submit line action with mixed permissions true" in response.content.decode()

    response = client.post(
        reverse_lazy("admin:example_actionuser_change", args=(staff_user.pk,)),
        {
            "username": staff_user.username,
            "date_joined_0": "2025-01-01",
            "date_joined_1": "12:00",
            "is_active": True,
            "is_staff": True,
            "is_superuser": True,
            "example_actionuser_submit_line_action_mixed_permissions_true": "1",
        },
        follow=True,
    )

    assert response.status_code == HTTPStatus.OK
    print(response.content.decode())
    assert (
        "Submit line action with mixed permissions true successfully executed"
        in response.content.decode()
    )


@pytest.mark.django_db
def test_submit_line_mixed_permissions_false(client, staff_user):
    client.force_login(staff_user)
    response = client.get(
        reverse_lazy("admin:example_actionuser_change", args=(staff_user.pk,))
    )
    assert response.status_code == HTTPStatus.OK
    assert (
        "Submit line action with mixed permissions false"
        not in response.content.decode()
    )

    response = client.post(
        reverse_lazy("admin:example_actionuser_change", args=(staff_user.pk,)),
        {
            "username": staff_user.username,
            "date_joined_0": "2025-01-01",
            "date_joined_1": "12:00",
            "is_active": True,
            "is_staff": True,
            "is_superuser": True,
            "example_user_submit_line_action_mixed_permissions_false": "1",
        },
        follow=True,
    )

    assert response.status_code == HTTPStatus.OK
    assert (
        "Submit line action with mixed permissions false successfully executed"
        not in response.content.decode()
    )


@pytest.mark.django_db
def test_submit_line_mixed_permissions_perm_not_granted(client, staff_user):
    client.force_login(staff_user)
    response = client.get(
        reverse_lazy("admin:example_actionuser_change", args=(staff_user.pk,))
    )
    assert response.status_code == HTTPStatus.OK
    assert (
        "Submit line action with mixed permissions perm not granted"
        not in response.content.decode()
    )

    response = client.post(
        reverse_lazy("admin:example_actionuser_change", args=(staff_user.pk,)),
        {
            "username": staff_user.username,
            "date_joined_0": "2025-01-01",
            "date_joined_1": "12:00",
            "is_active": True,
            "is_staff": True,
            "is_superuser": True,
            "example_user_submit_line_action_mixed_permissions_perm_not_granted": "1",
        },
        follow=True,
    )

    assert response.status_code == HTTPStatus.OK
    assert (
        "Submit line action with mixed permissions perm not granted successfully executed"
        not in response.content.decode()
    )


@pytest.mark.django_db
def test_submit_line_permission_true(client, admin_user):
    client.force_login(admin_user)
    response = client.get(
        reverse_lazy("admin:example_actionuser_change", args=(admin_user.pk,))
    )
    assert response.status_code == HTTPStatus.OK
    assert "Submit line action permission true" in response.content.decode()

    response = client.post(
        reverse_lazy("admin:example_actionuser_change", args=(admin_user.pk,)),
        {
            "username": admin_user.username,
            "date_joined_0": "2025-01-01",
            "date_joined_1": "12:00",
            "is_active": True,
            "is_staff": True,
            "is_superuser": True,
            "example_actionuser_submit_line_action_permission_true": "1",
        },
        follow=True,
    )

    assert response.status_code == HTTPStatus.OK
    assert (
        "Submit line action with true permission successfully executed"
        in response.content.decode()
    )


@pytest.mark.django_db
def test_submit_line_permission_false(client, admin_user):
    client.force_login(admin_user)
    response = client.get(
        reverse_lazy("admin:example_actionuser_change", args=(admin_user.pk,))
    )
    assert response.status_code == HTTPStatus.OK
    assert "Submit line action permission false" not in response.content.decode()

    response = client.post(
        reverse_lazy("admin:example_actionuser_change", args=(admin_user.pk,)),
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
def test_submit_line_multiple_different_permissions(client, admin_user):
    client.force_login(admin_user)
    response = client.get(
        reverse_lazy("admin:example_actionuser_change", args=(admin_user.pk,))
    )
    assert response.status_code == HTTPStatus.OK
    assert (
        "Submit line action with multiple permissions" not in response.content.decode()
    )

    response = client.post(
        reverse_lazy("admin:example_actionuser_change", args=(admin_user.pk,)),
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
