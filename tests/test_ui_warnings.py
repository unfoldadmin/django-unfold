from http import HTTPStatus

from django.test.utils import override_settings

from unfold.settings import CONFIG_DEFAULTS

TESTING_MESSAGE = 'Field <strong class="font-semibold">UserInvoiceInline.user</strong> is not an autocomplete field. Please add it to the `autocomplete_fields` list.'


def ui_warnings_callback_true(request):
    return request.user.is_superuser


@override_settings(
    UNFOLD={
        **CONFIG_DEFAULTS,
        "SHOW_UI_WARNINGS": True,
    }
)
def test_ui_warnings_not_in_debug_mode(admin_client):
    response = admin_client.get("/admin/example/user/1/change/")
    assert response.status_code == HTTPStatus.OK
    assert TESTING_MESSAGE not in response.content.decode()


@override_settings(
    DEBUG=True,
    UNFOLD={
        **CONFIG_DEFAULTS,
        "SHOW_UI_WARNINGS": True,
    },
)
def test_ui_warnings_enabled(admin_client):
    response = admin_client.get("/admin/example/user/1/change/")
    assert response.status_code == HTTPStatus.OK
    assert TESTING_MESSAGE in response.content.decode()


@override_settings(
    DEBUG=True,
    UNFOLD={
        **CONFIG_DEFAULTS,
        "SHOW_UI_WARNINGS": False,
    },
)
def test_ui_warnings_disabled(admin_client):
    response = admin_client.get("/admin/example/user/1/change/")
    assert response.status_code == HTTPStatus.OK
    assert TESTING_MESSAGE not in response.content.decode()


@override_settings(DEBUG=True)
def test_ui_warnings_default(admin_client):
    response = admin_client.get("/admin/example/user/1/change/")
    assert response.status_code == HTTPStatus.OK
    assert TESTING_MESSAGE not in response.content.decode()


@override_settings(
    DEBUG=True,
    UNFOLD={
        **CONFIG_DEFAULTS,
        "SHOW_UI_WARNINGS": "tests.test_ui_warnings.ui_warnings_callback_true",
    },
)
def test_ui_warnings_with_callback_enabled(admin_client):
    response = admin_client.get("/admin/example/user/1/change/")
    assert response.status_code == HTTPStatus.OK
    assert TESTING_MESSAGE in response.content.decode()


@override_settings(
    DEBUG=True,
    UNFOLD={
        **CONFIG_DEFAULTS,
        "SHOW_UI_WARNINGS": "tests.test_ui_warnings.non_existing_callback",
    },
)
def test_ui_warnings_with_callback_non_existing(admin_client):
    response = admin_client.get("/admin/example/user/1/change/")
    assert response.status_code == HTTPStatus.OK
    assert TESTING_MESSAGE not in response.content.decode()


@override_settings(
    DEBUG=True,
    UNFOLD={
        **CONFIG_DEFAULTS,
        "SHOW_UI_WARNINGS": None,
    },
)
def test_ui_warnings_with_none_config(admin_client):
    response = admin_client.get("/admin/example/user/1/change/")
    assert response.status_code == HTTPStatus.OK
    assert TESTING_MESSAGE not in response.content.decode()


@override_settings(
    DEBUG=True,
    UNFOLD={
        **CONFIG_DEFAULTS,
        "SHOW_UI_WARNINGS": lambda request: not request.user.is_superuser,
    },
)
def test_ui_warnings_with_callback_disabled(admin_client):
    response = admin_client.get("/admin/example/user/1/change/")
    assert response.status_code == HTTPStatus.OK
    assert TESTING_MESSAGE not in response.content.decode()
