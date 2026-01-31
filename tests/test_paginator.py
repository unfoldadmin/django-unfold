import pytest
from django.template import RequestContext, Template
from example.admin import ProjectAdmin
from example.models import Project

from unfold.paginator import InfinitePaginator
from unfold.sites import UnfoldAdminSite


def test_infinite_paginator_count_returns_fixed_large_value():
    MAX_COUNT = 9_999_999_999
    paginator = InfinitePaginator(object_list=list(range(50)), per_page=10)
    assert paginator.count == MAX_COUNT


def test_infinite_paginator_has_next_true_when_page_has_objects():
    paginator = InfinitePaginator(object_list=list(range(50)), per_page=10)
    page = paginator.page(1)
    assert page.has_next() is True


def test_infinite_paginator_has_next_false_when_page_is_empty():
    paginator = InfinitePaginator(object_list=[], per_page=10)
    page = paginator.page(1)
    assert page.has_next() is False


@pytest.mark.django_db
def test_infinite_paginator_template(user_factory, project_factory, rf):
    user = user_factory(username="sample@example.com", is_superuser=True, is_staff=True)
    request = rf.get("/?p=2")
    request.user = user

    project_factory.create_batch(30)

    user_admin = ProjectAdmin(Project, UnfoldAdminSite())
    changelist_view = user_admin.changelist_view(request=request)
    context_data = (
        changelist_view.context_data
        if hasattr(changelist_view, "context_data")
        else changelist_view.context
    )

    response = Template(
        "{% include 'unfold/helpers/pagination.html' with cl=cl %}"
    ).render(
        RequestContext(
            request,
            {
                "opts": Project._meta,
                "cl": context_data["cl"],
            },
        )
    )

    assert 'href="?p=1"' in response
    assert 'href="?p=3"' in response
    assert "Previous" in response
    assert "Next" in response


@pytest.mark.django_db
def test_infinite_paginator_template_empty(user_factory, rf):
    user = user_factory(username="sample@example.com", is_superuser=True, is_staff=True)
    request = rf.get("/")
    request.user = user

    project_admin = ProjectAdmin(Project, UnfoldAdminSite())
    changelist_view = project_admin.changelist_view(request=request)
    context_data = (
        changelist_view.context_data
        if hasattr(changelist_view, "context_data")
        else changelist_view.context
    )

    response = Template(
        "{% include 'unfold/helpers/pagination.html' with cl=cl %}"
    ).render(
        RequestContext(
            request,
            {
                "opts": Project._meta,
                "cl": context_data["cl"],
            },
        )
    )
    assert "href=" not in response
    assert "Previous" in response
    assert "Next" in response
