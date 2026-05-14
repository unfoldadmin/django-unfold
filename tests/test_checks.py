from unittest.mock import patch

import pytest
from django.apps import apps
from django.core.checks import Tags, run_checks


@pytest.mark.django_db
def test_run_all_checks():
    app_config = apps.get_app_config("example")

    errors = run_checks(
        app_configs=[app_config],
        tags=[Tags.admin],
    )

    assert errors == []


@pytest.mark.django_db
def test_checks_during_initial_migration():
    """
    Simulate a fresh DB where auth_permission doesn't exist yet.
    The check should return no errors and not raise an OperationalError.
    """

    app_config = apps.get_app_config("example")

    # Mock table_names to return an empty list, simulating an empty DB
    with patch("django.db.connection.introspection.table_names", return_value=[]):
        errors = run_checks(
            app_configs=[app_config],
            tags=[Tags.admin],
        )

    assert errors == []
