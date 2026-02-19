from http import HTTPStatus

import pytest
from django.contrib import admin
from django.urls import reverse
from example.admin import CategoryAdmin, ProjectNonrelatedInline
from example.models import Category, Project

from unfold.contrib.inlines.admin import NonrelatedTabularInline


@pytest.mark.django_db
def test_nonrelated_inlines(
    admin_client, admin_user, category_factory, project_factory
):
    category = category_factory(name="Test Category")
    project = project_factory(name="Test Project")

    response = admin_client.get(
        reverse("admin:example_category_change", args=(category.pk,))
    )
    assert response.status_code == HTTPStatus.OK
    assert "Test Project" in response.content.decode()

    response = admin_client.post(
        reverse("admin:example_category_change", args=(category.pk,)),
        {
            "name": "New Category",
            "example-project-TOTAL_FORMS": "4",
            "example-project-INITIAL_FORMS": "1",
            "example-project-MIN_NUM_FORMS": "0",
            "example-project-MAX_NUM_FORMS": "1000",
            "example-project-0-id": project.pk,
            "example-project-0-name": "New Project",
            "_continue": True,
        },
        follow=True,
    )

    assert response.status_code == HTTPStatus.OK

    assert (
        'The Category “<a href="/admin/example/category/1/change/">New Category</a>” was changed successfully'
        in response.content.decode()
    )
    assert "New Category" in response.content.decode()
    assert "New Project" in response.content.decode()


# TODO: test new
@pytest.mark.django_db
def test_nonrelated_inline_delete(
    admin_client, admin_user, category_factory, project_factory
):
    category = category_factory(name="Test Category")
    project = project_factory(name="Test Project")

    response = admin_client.get(
        reverse("admin:example_category_change", args=(category.pk,))
    )
    assert response.status_code == HTTPStatus.OK
    assert "Test Project" in response.content.decode()

    response = admin_client.post(
        reverse("admin:example_category_change", args=(category.pk,)),
        {
            "name": "Test Category",
            "example-project-TOTAL_FORMS": "4",
            "example-project-INITIAL_FORMS": "1",
            "example-project-MIN_NUM_FORMS": "0",
            "example-project-MAX_NUM_FORMS": "1000",
            "example-project-0-id": project.pk,
            "example-project-0-name": project.name,
            "example-project-0-DELETE": True,
            "_continue": True,
        },
        follow=True,
    )

    assert (
        'The Category “<a href="/admin/example/category/1/change/">Test Category</a>” was changed successfully'
        in response.content.decode()
    )
    assert Project.objects.all().count() == 0
    assert project.name not in response.content.decode()


def test_nonrelated_inline_delete_with_protected_related_objects(
    admin_client, admin_user, category_factory, project_factory, task_factory
):
    category = category_factory(name="Test Category")
    project = project_factory(name="Test Project")
    _task = task_factory(name="Test Task", project=project)

    response = admin_client.get(
        reverse("admin:example_category_change", args=(category.pk,))
    )
    assert response.status_code == HTTPStatus.OK
    assert "Test Project" in response.content.decode()

    response = admin_client.post(
        reverse("admin:example_category_change", args=(category.pk,)),
        {
            "name": "Test Category",
            "example-project-TOTAL_FORMS": "4",
            "example-project-INITIAL_FORMS": "1",
            "example-project-MIN_NUM_FORMS": "0",
            "example-project-MAX_NUM_FORMS": "1000",
            "example-project-0-id": project.pk,
            "example-project-0-name": project.name,
            "example-project-0-DELETE": True,
            "_continue": True,
        },
        follow=True,
    )

    assert (
        "Deleting project Test Project would require deleting the following protected related objects: task Test Task"
        in response.content.decode()
    )


@pytest.mark.django_db
def test_nonrelated_inlines_get_form_queryset_raises_not_implemented(category_factory):
    class InlineWithoutGetFormQueryset(NonrelatedTabularInline):
        model = Project

        def save_new_instance(self, parent, instance):
            pass

    parent_admin = CategoryAdmin(Category, admin.site)
    inline = InlineWithoutGetFormQueryset(parent_admin, admin.site)
    category = category_factory(name="Test Category")

    with pytest.raises(
        NotImplementedError, match="get_form_queryset must be implemented"
    ):
        inline.get_form_queryset(category)


@pytest.mark.django_db
def test_nonrelated_inlines_save_new_instance_raises_not_implemented(
    category_factory, project_factory
):
    class InlineWithoutSaveNewInstance(NonrelatedTabularInline):
        model = Project

        def get_form_queryset(self, obj):
            return self.model.objects.all()

    parent_admin = CategoryAdmin(Category, admin.site)
    inline = InlineWithoutSaveNewInstance(parent_admin, admin.site)
    category = category_factory(name="Test Category")
    project = project_factory(name="Test Project")

    with pytest.raises(
        NotImplementedError, match="save_new_instance must be implemented"
    ):
        inline.save_new_instance(category, project)


@pytest.mark.django_db
def test_nonrelated_inlines_get_form_queryset_returns_queryset(
    category_factory, project_factory
):
    category = category_factory(name="Test Category")
    project_factory(name="Project A")
    project_factory(name="Project B")

    parent_admin = CategoryAdmin(Category, admin.site)
    inline = ProjectNonrelatedInline(parent_admin, admin.site)
    qs = inline.get_form_queryset(category)

    assert list(qs.values_list("name", flat=True).order_by("name")) == [
        "Project A",
        "Project B",
    ]
