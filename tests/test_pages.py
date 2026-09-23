from http import HTTPStatus

from django.test.utils import override_settings

from unfold.settings import CONFIG_DEFAULTS


def dashboard_callback(request, context):
    context["sample_variable"] = "Sample value"
    return context


@override_settings(
    UNFOLD={
        **CONFIG_DEFAULTS,
        **{
            "DASHBOARD_CALLBACK": "tests.test_pages.dashboard_callback",
        },
    }
)
def test_dashboard(admin_client):
    response = admin_client.get("/admin/")
    assert response.status_code == HTTPStatus.OK
    assert response.context["sample_variable"] == "Sample value"


def test_password_change(admin_client):
    response = admin_client.get("/admin/password_change/")
    assert response.status_code == HTTPStatus.OK
