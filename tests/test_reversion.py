from http import HTTPStatus

import pytest
import reversion
from django.urls import reverse
from reversion.models import Version
from reversion.revisions import set_comment, set_user


def _content(response):
    return response.content.decode()


@pytest.fixture
def tag_history(admin_user, tag_factory):
    with reversion.create_revision():
        set_user(admin_user)
        tag = tag_factory(name="First tag version")
        set_comment("Created tag")

    with reversion.create_revision():
        set_user(admin_user)
        tag.name = "Second tag version"
        tag.save()
        set_comment("Updated tag")

    return tag


@pytest.fixture
def deleted_tag_version(admin_user, tag_history):
    with reversion.create_revision():
        set_user(admin_user)
        tag_history.delete()
        set_comment("Deleted tag")

    return (
        Version.objects.get_deleted(tag_history.__class__)
        .select_related("revision")
        .get()
    )


@pytest.fixture
def label_history(admin_user, label_factory):
    with reversion.create_revision():
        set_user(admin_user)
        label = label_factory(name="First label version")
        set_comment("Created label")

    with reversion.create_revision():
        set_user(admin_user)
        label.name = "Second label version"
        label.save()
        set_comment("Updated label")

    return label


def test_reversion_change_list_renders_recover_action(admin_client):
    response = admin_client.get(reverse("admin:example_tag_changelist"))

    assert response.status_code == HTTPStatus.OK
    assert reverse("admin:example_tag_recoverlist") in _content(response)


def test_reversion_change_form_renders_history_action(admin_client, tag):
    response = admin_client.get(reverse("admin:example_tag_change", args=(tag.pk,)))

    assert response.status_code == HTTPStatus.OK
    assert reverse("admin:example_tag_history", args=(tag.pk,)) in _content(response)


def test_reversion_history_renders_revision_entries(admin_client, tag_history):
    response = admin_client.get(
        reverse("admin:example_tag_history", args=(tag_history.pk,))
    )

    assert response.status_code == HTTPStatus.OK
    content = _content(response)

    assert 'id="change-history"' in content
    assert "Created tag" in content
    assert "Updated tag" in content


def test_reversion_revision_form_renders_warning(admin_client, tag_history):
    version = (
        Version.objects.get_for_object(tag_history).select_related("revision").last()
    )

    response = admin_client.get(
        reverse("admin:example_tag_revision", args=(tag_history.pk, version.pk))
    )

    assert response.status_code == HTTPStatus.OK
    content = _content(response)

    assert (
        "Historic version. Press the save button below to revert to this version of the object."
        in content
    )
    assert reverse("admin:example_tag_history", args=(tag_history.pk,)) in content
    assert 'name="_save"' in content


def test_reversion_recover_list_renders_deleted_versions(
    admin_client, deleted_tag_version
):
    response = admin_client.get(reverse("admin:example_tag_recoverlist"))

    assert response.status_code == HTTPStatus.OK
    content = _content(response)

    assert deleted_tag_version.object_repr in content
    assert (
        reverse("admin:example_tag_recover", args=(deleted_tag_version.pk,)) in content
    )


def test_reversion_recover_form_renders_message(admin_client, deleted_tag_version):
    response = admin_client.get(
        reverse("admin:example_tag_recover", args=(deleted_tag_version.pk,))
    )

    assert response.status_code == HTTPStatus.OK
    content = _content(response)

    assert (
        "Press the save button below to recover this version of the object." in content
    )
    assert reverse("admin:example_tag_recoverlist") in content
    assert 'name="_save"' in content


def test_reversion_compare_history_renders_compare_form(admin_client, label_history):
    response = admin_client.get(
        reverse("admin:example_label_history", args=(label_history.pk,))
    )

    assert response.status_code == HTTPStatus.OK
    content = _content(response)

    assert reverse("admin:example_label_compare", args=(label_history.pk,)) in content
    assert 'name="version_id1"' in content
    assert 'name="version_id2"' in content
    assert 'type="radio"' in content
    assert 'type="submit"' in content
    assert "Compare" in content


def test_reversion_compare_view_renders_unfold_actions(admin_client, label_history):
    versions = list(Version.objects.get_for_object(label_history).order_by("pk"))

    response = admin_client.get(
        reverse("admin:example_label_compare", args=(label_history.pk,)),
        {"version_id1": versions[0].pk, "version_id2": versions[1].pk},
    )

    assert response.status_code == HTTPStatus.OK
    content = _content(response)

    assert "reversion_compare.css" in content
    assert "unfold/reversion/css/reversion-compare.css" in content
    assert reverse("admin:example_label_history", args=(label_history.pk,)) in content
    assert (
        reverse("admin:example_label_revision", args=(label_history.pk, versions[0].pk))
        in content
    )
    assert "Revision comment" in content
    assert "Revert to this version" in content
