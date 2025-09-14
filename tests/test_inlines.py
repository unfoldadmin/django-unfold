from http import HTTPStatus

import pytest
from django.contrib.auth.models import Permission
from django.urls import reverse
from example.models import Project, Task

from .factories import TagFactory

USER_DATA = {
    "is_active": True,
    "is_staff": True,
    "is_superuser": True,
    "username": "admin@example.com",
    "email": "admin@example.com",
    "User_tags-TOTAL_FORMS": "0",
    "User_tags-INITIAL_FORMS": "0",
}


@pytest.mark.django_db
def test_inline_pagination(client, admin_user):
    tags_count = 50
    client.force_login(admin_user)

    for i in range(tags_count):
        tag = TagFactory(name=f"Tag {i}")
        admin_user.tags.add(tag)

    response = client.get(reverse("admin:example_user_change", args=(admin_user.pk,)))

    assert response.status_code == HTTPStatus.OK
    assert f"{tags_count} user-tag relationships" in response.content.decode()


@pytest.mark.django_db
def test_inline_pagination_no_relationships(client, admin_user):
    client.force_login(admin_user)
    response = client.get(reverse("admin:example_user_change", args=(admin_user.pk,)))
    assert response.status_code == HTTPStatus.OK

    assert "user-tag" not in response.content.decode()


@pytest.mark.django_db
def test_inline_pagination_one_relationship(client, admin_user):
    tag = TagFactory(name="Tag 1")
    admin_user.tags.add(tag)
    client.force_login(admin_user)

    response = client.get(reverse("admin:example_user_change", args=(admin_user.pk,)))
    assert response.status_code == HTTPStatus.OK
    assert "user-tag" not in response.content.decode()


@pytest.mark.django_db
def test_inline_collapsible(client, admin_user):
    tag = TagFactory(name="Tag 1")
    admin_user.tags.add(tag)
    client.force_login(admin_user)

    response = client.get(reverse("admin:example_user_change", args=(admin_user.pk,)))
    assert response.status_code == HTTPStatus.OK
    assert (
        "x-on:click=\"$event.target.tagName.toLowerCase() === 'h3' && (openRow = !openRow)"
        in response.content.decode()
    )


@pytest.mark.django_db(transaction=True)
def test_nested_inline_create_parent_object(client, admin_user):
    client.force_login(admin_user)

    data = {
        **USER_DATA,
        "project_set-TOTAL_FORMS": "1",
        "project_set-INITIAL_FORMS": "0",
        "project_set-0-name": "Test Project",
        "project_set-0-task_set-TOTAL_FORMS": "0",
        "project_set-0-task_set-INITIAL_FORMS": "0",
    }

    client.post(
        reverse("admin:example_user_change", args=(admin_user.pk,)),
        data=data,
        follow=True,
    )
    assert Project.objects.count() == 1
    assert Project.objects.first().name == "Test Project"
    assert Project.objects.first().user == admin_user


@pytest.mark.django_db
def test_nested_inline_create_nested_object(client, admin_user):
    client.force_login(admin_user)

    data = {
        **USER_DATA,
        "project_set-TOTAL_FORMS": "1",
        "project_set-INITIAL_FORMS": "0",
        "project_set-0-name": "Test Project",
        "project_set-0-task_set-TOTAL_FORMS": "1",
        "project_set-0-task_set-INITIAL_FORMS": "0",
        "project_set-0-task_set-0-name": "Test Task",
    }
    client.post(reverse("admin:example_user_change", args=(admin_user.pk,)), data=data)
    assert Project.objects.count() == 1
    assert Project.objects.first().name == "Test Project"
    assert Project.objects.first().user == admin_user
    assert Task.objects.count() == 1
    assert Task.objects.first().name == "Test Task"
    assert Task.objects.first().project == Project.objects.first()


@pytest.mark.django_db
def test_nested_inline_delete_parent_object(
    client, admin_user, project_factory, task_factory
):
    client.force_login(admin_user)
    project = project_factory(user=admin_user, name="Test Project")
    task = task_factory(project=project, name="Test Task")

    response = client.get(reverse("admin:example_user_change", args=(admin_user.pk,)))
    assert response.status_code == HTTPStatus.OK
    assert "Test Project" in response.content.decode()
    assert "Test Task" in response.content.decode()
    assert Project.objects.count() == 1
    assert Task.objects.count() == 1

    data = {
        **USER_DATA,
        "_continue": "1",
        "project_set-TOTAL_FORMS": "1",
        "project_set-INITIAL_FORMS": "1",
        "project_set-0-name": "Test Project",
        "project_set-0-DELETE": True,
        "project_set-0-id": project.pk,
        "project_set-0-user": admin_user.pk,
        "project_set-0-task_set-TOTAL_FORMS": "1",
        "project_set-0-task_set-INITIAL_FORMS": "1",
        "project_set-0-task_set-0-name": "Test Project",
        "project_set-0-task_set-0-id": task.pk,
        "project_set-0-task_set-0-project": project.pk,
    }

    response = client.post(
        reverse("admin:example_user_change", args=(admin_user.pk,)),
        data=data,
        follow=True,
    )

    assert "Test Project" not in response.content.decode()
    assert Project.objects.count() == 0
    assert Task.objects.count() == 0


@pytest.mark.django_db
def test_nested_inline_delete_nested_object(
    client, admin_user, project_factory, task_factory
):
    client.force_login(admin_user)
    project = project_factory(user=admin_user, name="Test Project")
    task = task_factory(project=project, name="Test Task")

    response = client.get(reverse("admin:example_user_change", args=(admin_user.pk,)))
    assert response.status_code == HTTPStatus.OK
    assert "Test Project" in response.content.decode()
    assert "Test Task" in response.content.decode()
    assert Project.objects.count() == 1
    assert Task.objects.count() == 1

    data = {
        **USER_DATA,
        "_continue": "1",
        "project_set-TOTAL_FORMS": "1",
        "project_set-INITIAL_FORMS": "1",
        "project_set-0-name": "Test Project",
        "project_set-0-id": project.pk,
        "project_set-0-user": admin_user.pk,
        "project_set-0-task_set-TOTAL_FORMS": "1",
        "project_set-0-task_set-INITIAL_FORMS": "1",
        "project_set-0-task-name": "Test Project",
        "project_set-0-task_set-0-DELETE": True,
        "project_set-0-task_set-0-id": task.pk,
        "project_set-0-task_set-0-project": project.pk,
    }

    response = client.post(
        reverse("admin:example_user_change", args=(admin_user.pk,)),
        data=data,
        follow=True,
    )
    assert "Test Project" in response.content.decode()
    assert "Test Task" not in response.content.decode()
    assert Project.objects.count() == 1
    assert Task.objects.count() == 0


@pytest.mark.django_db
@pytest.mark.parametrize(
    "permissions, delete_project, delete_task, project_count, task_count",
    [
        [[], True, True, 1, 1],
        [["delete_project"], True, True, 1, 1],
        [["view_project", "delete_project"], True, False, 0, 0],
        [["view_project", "delete_project"], False, True, 1, 1],
        [["view_project", "delete_project", "delete_task"], False, True, 1, 1],
        [
            ["view_project", "delete_project", "view_task", "delete_task"],
            False,
            True,
            1,
            0,
        ],
    ],
)
def test_nested_inlines_delete(
    permissions,
    delete_project,
    delete_task,
    project_count,
    task_count,
    client,
    staff_user,
    project_factory,
    task_factory,
):
    client.force_login(staff_user)
    project = project_factory(user=staff_user, name="Test Project")
    task = task_factory(project=project, name="Test Task")

    for permission in permissions:
        staff_user.user_permissions.add(Permission.objects.get(codename=permission))

    assert Project.objects.count() == 1
    assert Task.objects.count() == 1

    data = {
        **USER_DATA,
        "_continue": "1",
        "project_set-TOTAL_FORMS": "1",
        "project_set-INITIAL_FORMS": "1",
        "project_set-0-name": "Test Project",
        "project_set-0-id": project.pk,
        "project_set-0-user": staff_user.pk,
        "project_set-0-DELETE": delete_project,
        "project_set-0-task_set-TOTAL_FORMS": "1",
        "project_set-0-task_set-INITIAL_FORMS": "1",
        "project_set-0-task_set-0-name": "Task Value",
        "project_set-0-task_set-0-id": task.pk,
        "project_set-0-task_set-0-project": project.pk,
        "project_set-0-task_set-0-DELETE": delete_task,
    }

    client.post(
        reverse("admin:example_user_change", args=(staff_user.pk,)),
        data=data,
        follow=True,
    )

    assert Project.objects.count() == project_count
    assert Task.objects.count() == task_count


@pytest.mark.django_db
def test_nested_inline_permissions(client, staff_user, project_factory, task_factory):
    client.force_login(staff_user)
    project = project_factory(user=staff_user, name="Test Project")
    task_factory(project=project, name="Test Task")

    response = client.get(reverse("admin:example_user_change", args=(staff_user.pk,)))
    assert "Test Project" not in response.content.decode()
    assert "Test Task" not in response.content.decode()
    assert "project_set-0-DELETE" not in response.content.decode()
    assert "<span>Add another Project</span>" not in response.content.decode()

    staff_user.user_permissions.add(Permission.objects.get(codename="change_project"))
    response = client.get(reverse("admin:example_user_change", args=(staff_user.pk,)))
    assert "Test Project" in response.content.decode()
    assert "Test Task" not in response.content.decode()
    assert "project_set-0-DELETE" not in response.content.decode()
    assert "<span>Add another Project</span>" not in response.content.decode()

    staff_user.user_permissions.add(Permission.objects.get(codename="delete_project"))
    response = client.get(reverse("admin:example_user_change", args=(staff_user.pk,)))
    assert "Test Project" in response.content.decode()
    assert "Test Task" not in response.content.decode()
    assert "project_set-0-DELETE" in response.content.decode()
    assert "<span>Add another Project</span>" not in response.content.decode()

    staff_user.user_permissions.add(Permission.objects.get(codename="add_project"))
    response = client.get(reverse("admin:example_user_change", args=(staff_user.pk,)))
    assert "Test Project" in response.content.decode()
    assert "Test Task" not in response.content.decode()
    assert "project_set-0-DELETE" in response.content.decode()
    assert "<span>Add another Project</span>" in response.content.decode()

    staff_user.user_permissions.add(Permission.objects.get(codename="view_task"))
    response = client.get(reverse("admin:example_user_change", args=(staff_user.pk,)))
    assert "Test Task" in response.content.decode()
    assert "project_set-0-task_set-0-DELETE" not in response.content.decode()
    assert "<span>Add another Task</span>" not in response.content.decode()

    staff_user.user_permissions.add(Permission.objects.get(codename="add_task"))
    response = client.get(reverse("admin:example_user_change", args=(staff_user.pk,)))
    assert "Test Task" in response.content.decode()
    assert "project_set-0-task_set-0-DELETE" not in response.content.decode()
    assert "<span>Add another Task</span>" in response.content.decode()

    staff_user.user_permissions.add(Permission.objects.get(codename="delete_task"))
    response = client.get(reverse("admin:example_user_change", args=(staff_user.pk,)))
    assert "Test Task" in response.content.decode()
    assert "project_set-0-task_set-0-DELETE" in response.content.decode()
    assert "<span>Add another Task</span>" in response.content.decode()


@pytest.mark.django_db
def test_nested_inline_change_task_value(
    client, admin_user, project_factory, task_factory
):
    client.force_login(admin_user)
    project = project_factory(user=admin_user, name="Test Project")
    task = task_factory(project=project, name="Test Task")

    response = client.get(reverse("admin:example_user_change", args=(admin_user.pk,)))
    assert response.status_code == HTTPStatus.OK
    assert "Test Task" in response.content.decode()

    data = {
        **USER_DATA,
        "_continue": "1",
        "project_set-TOTAL_FORMS": "1",
        "project_set-INITIAL_FORMS": "1",
        "project_set-0-name": "Test Project",
        "project_set-0-id": project.pk,
        "project_set-0-user": admin_user.pk,
        "project_set-0-task_set-TOTAL_FORMS": "1",
        "project_set-0-task_set-INITIAL_FORMS": "1",
        "project_set-0-task_set-0-name": "Test Task2",
        "project_set-0-task_set-0-id": task.pk,
        "project_set-0-task_set-0-project": project.pk,
    }

    response = client.post(
        reverse("admin:example_user_change", args=(admin_user.pk,)),
        data=data,
        follow=True,
    )
    assert response.status_code == HTTPStatus.OK
    assert "Test Task2" in response.content.decode()
    task.refresh_from_db()
    assert task.name == "Test Task2"


@pytest.mark.django_db
@pytest.mark.parametrize(
    "permissions, result",
    [
        [[], "Test Task"],
        [["change_project"], "Test Task"],
        [["change_task"], "Test Task"],
        [["change_project"], "Test Task"],
        [["change_project", "add_task"], "Test Task"],
        [["change_project", "change_task"], "Updated Task Value"],
    ],
)
def test_nested_inline_permissions_change(
    permissions, result, client, staff_user, project_factory, task_factory
):
    client.force_login(staff_user)
    project = project_factory(user=staff_user, name="Test Project")
    task = task_factory(project=project, name="Test Task")

    for permission in permissions:
        staff_user.user_permissions.add(Permission.objects.get(codename=permission))

    data = {
        **USER_DATA,
        "_continue": "1",
        "project_set-TOTAL_FORMS": "1",
        "project_set-INITIAL_FORMS": "1",
        "project_set-0-name": "Test Project",
        "project_set-0-id": project.pk,
        "project_set-0-user": staff_user.pk,
        "project_set-0-task_set-TOTAL_FORMS": "1",
        "project_set-0-task_set-INITIAL_FORMS": "1",
        "project_set-0-task_set-0-name": "Updated Task Value",
        "project_set-0-task_set-0-id": task.pk,
        "project_set-0-task_set-0-project": project.pk,
    }

    client.post(
        reverse("admin:example_user_change", args=(staff_user.pk,)),
        data=data,
        follow=True,
    )

    task.refresh_from_db()
    assert task.name == result


@pytest.mark.django_db
@pytest.mark.parametrize(
    "permissions,result",
    [
        [[], 0],
        [["change_project"], 0],
        [["add_task"], 0],
        [["change_task"], 0],
        [["change_project", "change_task"], 0],
        [["change_project", "add_task"], 1],
    ],
)
def test_nested_inline_add(permissions, result, client, staff_user, project_factory):
    client.force_login(staff_user)
    project = project_factory(user=staff_user, name="Test Project")

    for permission in permissions:
        staff_user.user_permissions.add(Permission.objects.get(codename=permission))

    assert Task.objects.count() == 0
    data = {
        **USER_DATA,
        "_continue": "1",
        "project_set-TOTAL_FORMS": "1",
        "project_set-INITIAL_FORMS": "1",
        "project_set-0-name": "Test Project",
        "project_set-0-id": project.pk,
        "project_set-0-user": staff_user.pk,
        "project_set-0-task_set-TOTAL_FORMS": "1",
        "project_set-0-task_set-INITIAL_FORMS": "0",
        "project_set-0-task_set-0-name": "New Task Value",
    }

    client.post(
        reverse("admin:example_user_change", args=(staff_user.pk,)),
        data=data,
        follow=True,
    )

    assert Task.objects.count() == result


@pytest.mark.django_db
def test_nested_inline_without_parent(client, admin_user):
    client.force_login(admin_user)

    assert Task.objects.count() == 0

    data = {
        **USER_DATA,
        "_continue": "1",
        "project_set-TOTAL_FORMS": "1",
        "project_set-INITIAL_FORMS": "0",
        "project_set-0-name": "",
        "project_set-0-task_set-TOTAL_FORMS": "1",
        "project_set-0-task_set-INITIAL_FORMS": "0",
        "project_set-0-task_set-0-name": "Updated Task Value",
    }

    response = client.post(
        reverse("admin:example_user_change", args=(admin_user.pk,)),
        data=data,
        follow=True,
    )

    assert Task.objects.count() == 0
    assert "Please correct the errors below." in response.content.decode()
    assert (
        "You can not create nested object without parent" in response.content.decode()
    )
