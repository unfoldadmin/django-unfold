import re
from http import HTTPStatus

import pytest
from django.urls import reverse

from tests.factories import ConditionalFieldsTestModelFactory


@pytest.mark.django_db
def test_conditional_fields_in_context(admin_client):
    """Test that conditional fields are properly included in the admin form context."""
    conditional_fields_test_instance = ConditionalFieldsTestModelFactory(
        status="ACTIVE",
        conditional_field_active="Active Value",
        conditional_field_inactive="Inactive Value"
    )
    change_url = reverse(
        "admin:example_conditionalfieldstestmodel_change",
        args=[conditional_fields_test_instance.pk]
    )

    response = admin_client.get(change_url)

    assert response.status_code == HTTPStatus.OK
    content = response.content.decode()
    # Test that the x-bind:disabled directive is present to disable hidden fields
    assert re.search(r'x-bind:disabled="!\(status\s*===\s*&quot;ACTIVE&quot;\)"', content)
    assert re.search(r'x-bind:disabled="!\(status\s*===\s*&quot;INACTIVE&quot;\)"', content)
    # TODO: test that the fields are disabled (at init & on update)