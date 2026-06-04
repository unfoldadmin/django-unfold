from http import HTTPStatus

from django.contrib.auth.models import AnonymousUser
from django.test.client import RequestFactory
from django.test.utils import override_settings

from unfold.settings import CONFIG_DEFAULTS
from unfold.sites import UnfoldAdminSite


@override_settings(UNFOLD={**CONFIG_DEFAULTS, **{"THEME": "light"}})
def test_theme_forced_light_in_context():
    admin_site = UnfoldAdminSite()
    request = RequestFactory().get("/rand")
    request.user = AnonymousUser()
    context = admin_site.each_context(request)

    assert context["theme"] == "light"


@override_settings(UNFOLD={**CONFIG_DEFAULTS, **{"THEME": "dark"}})
def test_theme_forced_dark_in_context():
    admin_site = UnfoldAdminSite()
    request = RequestFactory().get("/rand")
    request.user = AnonymousUser()
    context = admin_site.each_context(request)

    assert context["theme"] == "dark"


@override_settings(UNFOLD=CONFIG_DEFAULTS)
def test_theme_not_forced_in_context():
    admin_site = UnfoldAdminSite()
    request = RequestFactory().get("/rand")
    request.user = AnonymousUser()
    context = admin_site.each_context(request)

    assert not context.get("theme")


@override_settings(UNFOLD={**CONFIG_DEFAULTS, **{"THEME": "light"}})
def test_theme_forced_light_rendered_in_skeleton(admin_client):
    response = admin_client.get("/admin/")

    assert response.status_code == HTTPStatus.OK
    content = response.content.decode()
    # Server-side forced theme: <html> carries the class and Alpine is seeded.
    assert 'class="light"' in content
    assert "x-data=\"theme('light')\"" in content


@override_settings(UNFOLD={**CONFIG_DEFAULTS, **{"THEME": "dark"}})
def test_theme_forced_dark_rendered_in_skeleton(admin_client):
    response = admin_client.get("/admin/")

    assert response.status_code == HTTPStatus.OK
    content = response.content.decode()
    assert 'class="dark"' in content
    assert "x-data=\"theme('dark')\"" in content


@override_settings(UNFOLD=CONFIG_DEFAULTS)
def test_theme_auto_rendered_in_skeleton(admin_client):
    response = admin_client.get("/admin/")

    assert response.status_code == HTTPStatus.OK
    content = response.content.decode()
    # No forced theme — Alpine receives no default and falls back to "auto".
    assert 'x-data="theme()"' in content


@override_settings(UNFOLD={**CONFIG_DEFAULTS, **{"THEME": "light"}})
def test_theme_switcher_hidden_when_forced(admin_client):
    response = admin_client.get("/admin/")

    assert response.status_code == HTTPStatus.OK
    content = response.content.decode()
    # The dropdown switcher and the light/dark/system toggle row are both
    # gated on `{% if not theme %}` and must not render when THEME is set.
    assert "switchTheme('light')" not in content
    assert "switchTheme('dark')" not in content
    assert "switchTheme('auto')" not in content


@override_settings(UNFOLD=CONFIG_DEFAULTS)
def test_theme_switcher_visible_when_not_forced(admin_client):
    response = admin_client.get("/admin/")

    assert response.status_code == HTTPStatus.OK
    content = response.content.decode()
    assert "switchTheme('light')" in content
    assert "switchTheme('dark')" in content
    assert "switchTheme('auto')" in content
