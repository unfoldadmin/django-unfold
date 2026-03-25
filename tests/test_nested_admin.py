from http import HTTPStatus

import pytest
from django.contrib import admin
from django.http import HttpResponse
from django.test import override_settings
from django.test.client import RequestFactory
from django.urls import include, path, reverse
from example.models import Project, Task, User

from unfold.admin import ModelAdmin
from unfold.contrib.nested_admin.admin import (
    NestedChildAdminMixin,
    NestedParentAdminMixin,
)
from unfold.decorators import action
from unfold.sites import UnfoldAdminSite


class _ControlTaskAdmin(NestedChildAdminMixin, ModelAdmin):
    nested_parent_fk = "project"
    actions_detail = ["preview"]

    @action(description="Preview", url_path="preview")
    def preview(self, request, object_id):
        return HttpResponse(f"preview:{object_id}")


class _ControlProjectAdmin(NestedParentAdminMixin, ModelAdmin):
    nested_child_model = Task
    nested_child_fk_name = "project"


_control_site = UnfoldAdminSite(name="control")
_control_site.register(Project, _ControlProjectAdmin)
_control_site.register(Task, _ControlTaskAdmin)

urlpatterns = [
    path("control/", _control_site.urls),
    path("admin/", admin.site.urls),
    path(
        "admin/",
        include(
            (
                [
                    path(
                        "toggle-sidebar/",
                        lambda request: HttpResponse(status=HTTPStatus.OK),
                        name="toggle_sidebar",
                    )
                ],
                "admin_extras",
            ),
            namespace="admin_extras",
        ),
    ),
]


def _response_content(response):
    return response.content.decode()


def _task_url(name, *args, site="admin"):
    return reverse(f"{site}:example_project_task_{name}", args=args)


@pytest.fixture
def project_with_tasks(project_factory, task_factory):
    project = project_factory(name="Nested Project")
    first_task = task_factory(name="Task A", project=project)
    second_task = task_factory(name="Task B", project=project)
    return project, first_task, second_task


@pytest.fixture
def nested_admin_client(client, admin_user):
    client.force_login(admin_user)
    return client


@pytest.mark.parametrize(
    "site, prefix", [("admin", "/admin/"), ("control", "/control/")]
)
@pytest.mark.django_db
@override_settings(ROOT_URLCONF="tests.test_nested_admin")
def test_nested_urls_reverse(project_factory, site, prefix):
    project = project_factory()

    add_url = _task_url("add", project.pk, site=site)
    changelist_url = _task_url("changelist", project.pk, site=site)
    history_url = _task_url("history", project.pk, 1, site=site)
    delete_url = _task_url("delete", project.pk, 1, site=site)

    assert add_url.endswith(f"{prefix}example/project/{project.pk}/task/add/")
    assert changelist_url.endswith(f"{prefix}example/project/{project.pk}/task/")
    assert history_url.endswith(f"{prefix}example/project/{project.pk}/task/1/history/")
    assert delete_url.endswith(f"{prefix}example/project/{project.pk}/task/1/delete/")


@pytest.mark.django_db
def test_nested_changelist_renders_nested_add_link_and_breadcrumbs(
    nested_admin_client, project_factory
):
    project = project_factory(name="Nested Parent")
    response = nested_admin_client.get(_task_url("changelist", project.pk))

    assert response.status_code == HTTPStatus.OK
    content = _response_content(response)
    assert _task_url("add", project.pk) in content
    assert "Nested Parent" in content
    assert reverse("admin:example_project_change", args=[project.pk]) in content


@pytest.mark.django_db
def test_parent_change_view_renders_nested_child_entrypoint(
    nested_admin_client, project_factory
):
    project = project_factory(name="Nested Parent")
    response = nested_admin_client.get(
        reverse("admin:example_project_change", args=[project.pk])
    )

    assert response.status_code == HTTPStatus.OK
    content = _response_content(response)
    assert _task_url("changelist", project.pk) in content
    assert "Tasks" in content


@pytest.mark.django_db
def test_nested_change_view_uses_nested_navigation_urls(
    nested_admin_client, project_with_tasks
):
    project, first_task, _ = project_with_tasks
    response = nested_admin_client.get(_task_url("change", project.pk, first_task.pk))

    assert response.status_code == HTTPStatus.OK
    content = _response_content(response)
    assert reverse("admin:example_project_change", args=[project.pk]) in content
    assert _task_url("changelist", project.pk) in content
    assert _task_url("add", project.pk) in content
    assert _task_url("history", project.pk, first_task.pk) in content
    assert _task_url("delete", project.pk, first_task.pk) in content
    assert f'href="{_task_url("changelist", project.pk)}"' in content
    assert f'href="{_task_url("add", project.pk)}"' in content


@pytest.mark.django_db
def test_nested_history_view_uses_nested_navigation_urls(
    nested_admin_client, project_with_tasks
):
    project, first_task, _ = project_with_tasks
    response = nested_admin_client.get(_task_url("history", project.pk, first_task.pk))

    assert response.status_code == HTTPStatus.OK
    content = _response_content(response)
    assert reverse("admin:example_project_change", args=[project.pk]) in content
    assert _task_url("changelist", project.pk) in content
    assert _task_url("change", project.pk, first_task.pk) in content
    assert "History" in content


@pytest.mark.django_db
def test_nested_delete_view_uses_nested_navigation_urls(
    nested_admin_client, project_with_tasks
):
    project, first_task, _ = project_with_tasks
    response = nested_admin_client.get(_task_url("delete", project.pk, first_task.pk))

    assert response.status_code == HTTPStatus.OK
    content = _response_content(response)
    assert reverse("admin:example_project_change", args=[project.pk]) in content
    assert _task_url("changelist", project.pk) in content
    assert _task_url("change", project.pk, first_task.pk) in content
    assert "Delete" in content


@pytest.mark.django_db
def test_nested_add_form_prefills_and_locks_parent_fk(
    nested_admin_client, project_factory
):
    project = project_factory()
    response = nested_admin_client.get(_task_url("add", project.pk))

    assert response.status_code == HTTPStatus.OK
    form = response.context["adminform"].form
    assert str(form.initial["project"]) == str(project.pk)
    assert list(form.fields["project"].queryset.values_list("pk", flat=True)) == [
        project.pk
    ]


@pytest.mark.django_db
def test_nested_child_admin_public_helpers(project_factory):
    project = project_factory()
    task_admin = admin.site._registry[Task]
    request = RequestFactory().get("/")
    request.nested_parent_id = str(project.pk)
    request.nested_parent_object = project

    assert task_admin.get_parent_id(request) == str(project.pk)
    assert task_admin.get_parent_object(request) == project
    assert task_admin.get_change_url(request, 7) == _task_url("change", project.pk, 7)


@pytest.mark.django_db
def test_nested_add_redirects_to_nested_change_and_preserves_filters(
    nested_admin_client, project_factory
):
    project = project_factory()
    add_url = _task_url("add", project.pk)
    response = nested_admin_client.post(
        f"{add_url}?_changelist_filters=project__id__exact%3D{project.pk}",
        {
            "name": "Nested Task",
            "project": str(project.pk),
            "_continue": "1",
        },
    )

    task = Task.objects.get(name="Nested Task")

    assert response.status_code == HTTPStatus.FOUND
    assert response["Location"].startswith(_task_url("change", project.pk, task.pk))
    assert "_changelist_filters=project__id__exact%3D" in response["Location"]


@pytest.mark.django_db
def test_nested_change_redirects_to_nested_changelist(
    nested_admin_client, project_with_tasks
):
    project, first_task, _ = project_with_tasks
    response = nested_admin_client.post(
        _task_url("change", project.pk, first_task.pk),
        {
            "name": first_task.name,
            "project": str(project.pk),
        },
    )

    assert response.status_code == HTTPStatus.FOUND
    assert response["Location"].rstrip("/") == _task_url(
        "changelist", project.pk
    ).rstrip("/")


@pytest.mark.django_db
def test_nested_delete_redirects_to_nested_changelist(
    nested_admin_client, project_with_tasks
):
    project, first_task, _ = project_with_tasks
    response = nested_admin_client.post(
        _task_url("delete", project.pk, first_task.pk),
        {"post": "yes"},
    )

    assert response.status_code == HTTPStatus.FOUND
    assert response["Location"].rstrip("/") == _task_url(
        "changelist", project.pk
    ).rstrip("/")


@pytest.mark.django_db
def test_nested_changelist_result_links_are_nested(
    nested_admin_client, project_with_tasks
):
    project, first_task, _ = project_with_tasks
    response = nested_admin_client.get(_task_url("changelist", project.pk))

    assert response.status_code == HTTPStatus.OK
    assert (
        response.context["cl"]
        .url_for_result(first_task)
        .endswith(f"/admin/example/project/{project.pk}/task/{first_task.pk}/change/")
    )


@pytest.mark.django_db
def test_example_task_detail_action_uses_nested_proxy_and_redirects_back(
    nested_admin_client, project_with_tasks
):
    project, first_task, _ = project_with_tasks
    response = nested_admin_client.get(_task_url("change", project.pk, first_task.pk))

    assert response.status_code == HTTPStatus.OK
    action_url = _task_url("action_proxy", project.pk, first_task.pk, "preview/")
    assert response.context["actions_detail"][0]["path"] == action_url

    action_response = nested_admin_client.get(action_url)

    assert action_response.status_code == HTTPStatus.FOUND
    assert action_response["Location"] == _task_url("change", project.pk, first_task.pk)


@pytest.mark.django_db
@override_settings(ROOT_URLCONF="tests.test_nested_admin")
def test_nested_change_view_renders_nested_detail_action_links(
    client, admin_user, project_factory, task_factory
):
    project = project_factory()
    task = task_factory(project=project, name="Action Task")
    client.force_login(admin_user)

    response = client.get(
        reverse("control:example_project_task_change", args=[project.pk, task.pk])
    )

    assert response.status_code == HTTPStatus.OK
    actions_detail = response.context["actions_detail"]
    assert actions_detail[0]["path"] == reverse(
        "control:example_project_task_action_proxy",
        args=[project.pk, task.pk, "preview/"],
    )


@pytest.mark.django_db
@override_settings(ROOT_URLCONF="tests.test_nested_admin")
def test_nested_action_proxy_delegates_to_child_admin_action(
    client, admin_user, project_factory, task_factory
):
    project = project_factory()
    task = task_factory(project=project, name="Action Task")
    client.force_login(admin_user)

    response = client.get(
        reverse(
            "control:example_project_task_action_proxy",
            args=[project.pk, task.pk, "preview/"],
        )
    )

    assert response.status_code == HTTPStatus.OK
    assert response.content.decode() == f"preview:{task.pk}"


@pytest.mark.django_db
def test_nested_parent_admin_checks():
    site = UnfoldAdminSite(name="checks")

    class MissingChildAdmin(NestedParentAdminMixin, ModelAdmin):
        pass

    class WrongFieldAdmin(NestedParentAdminMixin, ModelAdmin):
        nested_child_model = Task
        nested_child_fk_name = "name"

    class WrongParentAdmin(NestedParentAdminMixin, ModelAdmin):
        nested_child_model = User
        nested_child_fk_name = "profile"

    missing_errors = MissingChildAdmin(Project, site).check()
    wrong_field_errors = WrongFieldAdmin(Project, site).check()
    wrong_parent_errors = WrongParentAdmin(Project, site).check()

    assert any(error.id == "nested_admin.E001" for error in missing_errors)
    assert any(error.id == "nested_admin.E003" for error in wrong_field_errors)
    assert any(error.id == "nested_admin.E004" for error in wrong_parent_errors)
