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
