import pytest
from django.urls import reverse


@pytest.mark.django_db
def test_post_admin_ordering(admin_client, django_assert_num_queries, post_factory):
    post_A = post_factory(title="AAAA", weight=5)
    post_B = post_factory(title="BBBB", weight=2)
    post_C = post_factory(title="CCCC", weight=8)

    response = admin_client.get(reverse("admin:example_post_changelist"))

    content = response.content.decode()
    idx_B = content.find(post_B.title)
    idx_A = content.find(post_A.title)
    idx_C = content.find(post_C.title)

    assert idx_B < idx_A < idx_C, "Posts should be ordered by weight ascending"


@pytest.mark.django_db
def test_post_admin_ordering_with_same_weight(admin_client, post_factory):
    post_A = post_factory(title="first", weight=7)
    post_B = post_factory(title="second", weight=7)
    post_C = post_factory(title="third", weight=7)

    response = admin_client.get(reverse("admin:example_post_changelist"))
    content = response.content.decode()

    idx_A = content.find(post_A.title)
    idx_B = content.find(post_B.title)
    idx_C = content.find(post_C.title)

    assert idx_A < idx_B < idx_C, (
        "Posts should be ordered by weight ascending and then by PK ascending"
    )
