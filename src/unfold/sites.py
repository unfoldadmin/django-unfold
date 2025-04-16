import copy
from http import HTTPStatus
from typing import Any, Callable, Optional, Union
from urllib.parse import parse_qs, urlparse

from django.contrib.admin import AdminSite
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.core.validators import EMPTY_VALUES
from django.http import HttpRequest, HttpResponse
from django.template.response import TemplateResponse
from django.urls import URLPattern, path, reverse, reverse_lazy
from django.utils.decorators import method_decorator
from django.utils.functional import lazy
from django.utils.module_loading import import_string
from django.views.decorators.cache import never_cache

from unfold.dataclasses import DropdownItem, Favicon

try:
    from django.contrib.auth.decorators import login_not_required
except ImportError:

    def login_not_required(func: Callable) -> Callable:
        return func


from unfold.settings import get_config
from unfold.utils import hex_to_rgb
from unfold.widgets import (
    BUTTON_CLASSES,
    CHECKBOX_CLASSES,
    FILE_CLASSES,
    INPUT_CLASSES,
    RADIO_CLASSES,
    SWITCH_CLASSES,
)


class UnfoldAdminSite(AdminSite):
    default_site = "unfold.admin.UnfoldAdminSite"
    settings_name = "UNFOLD"

    def __init__(self, name: str = "admin") -> None:
        from unfold.forms import AuthenticationForm

        super().__init__(name)

        if self.login_form is None:
            self.login_form = AuthenticationForm

    def get_urls(self) -> list[URLPattern]:
        extra_urls = []

        if hasattr(self, "extra_urls") and callable(self.extra_urls):
            extra_urls = self.extra_urls()

        urlpatterns = (
            [
                path("search/", self.admin_view(self.search), name="search"),
                path(
                    "toggle-sidebar/",
                    self.admin_view(self.toggle_sidebar),
                    name="toggle_sidebar",
                ),
            ]
            + extra_urls
            + super().get_urls()
        )

        return urlpatterns

    def each_context(self, request: HttpRequest) -> dict[str, Any]:
        context = super().each_context(request)

        sidebar_config = self._get_config("SIDEBAR", request)
        data = {
            "form_classes": {
                "text_input": " ".join(INPUT_CLASSES),
                "checkbox": " ".join(CHECKBOX_CLASSES),
                "button": " ".join(BUTTON_CLASSES),
                "radio": " ".join(RADIO_CLASSES),
                "switch": " ".join(SWITCH_CLASSES),
                "file": " ".join(FILE_CLASSES),
            },
            "site_title": self._get_config("SITE_TITLE", request),
            "site_header": self._get_config("SITE_HEADER", request),
            "site_url": self._get_config("SITE_URL", request),
            "site_subheader": self._get_config("SITE_SUBHEADER", request),
            "site_dropdown": self._get_site_dropdown_items("SITE_DROPDOWN", request),
            "site_logo": self._get_theme_images("SITE_LOGO", request),
            "site_icon": self._get_theme_images("SITE_ICON", request),
            "site_symbol": self._get_config("SITE_SYMBOL", request),
            "site_favicons": self._get_favicons("SITE_FAVICONS", request),
            "show_history": self._get_config("SHOW_HISTORY", request),
            "show_view_on_site": self._get_config("SHOW_VIEW_ON_SITE", request),
            "show_languages": self._get_config("SHOW_LANGUAGES", request),
            "show_back_button": self._get_config("SHOW_BACK_BUTTON", request),
            "theme": self._get_config("THEME", request),
            "border_radius": self._get_config("BORDER_RADIUS", request),
            "colors": self._get_colors("COLORS", request),
            "environment": self._get_config("ENVIRONMENT", request),
            "environment_title_prefix": self._get_config(
                "ENVIRONMENT_TITLE_PREFIX", request
            ),
            "tab_list": self.get_tabs_list(request),
            "styles": self._get_list("STYLES", request),
            "scripts": self._get_list("SCRIPTS", request),
            "sidebar_show_all_applications": self._get_value(
                sidebar_config.get("show_all_applications"), request
            ),
            "sidebar_show_search": self._get_value(
                sidebar_config.get("show_search"), request
            ),
            "sidebar_navigation": self.get_sidebar_list(request)
            if self.has_permission(request)
            else [],
        }

        context.update(data)

        if hasattr(self, "extra_context") and callable(self.extra_context):
            return self.extra_context(context, request)

        return context

    def index(
        self, request: HttpRequest, extra_context: Optional[dict[str, Any]] = None
    ) -> TemplateResponse:
        app_list = self.get_app_list(request)

        context = {
            **self.each_context(request),
            "title": self.index_title,
            "subtitle": None,
            "app_list": app_list,
            "index": True,
            **(extra_context or {}),
        }

        dashboard_callback = get_config(self.settings_name)["DASHBOARD_CALLBACK"]

        if isinstance(dashboard_callback, str):
            context = import_string(dashboard_callback)(request, context)

        request.current_app = self.name

        return TemplateResponse(
            request, self.index_template or "admin/index.html", context
        )

    def toggle_sidebar(
        self, request: HttpRequest, extra_context: Optional[dict[str, Any]] = None
    ) -> HttpResponse:
        if "toggle_sidebar" not in request.session:
            request.session["toggle_sidebar"] = True
        else:
            request.session["toggle_sidebar"] = not request.session["toggle_sidebar"]

        return HttpResponse(status=HTTPStatus.OK)

    def search(
        self, request: HttpRequest, extra_context: Optional[dict[str, Any]] = None
    ) -> TemplateResponse:
        query = request.GET.get("s").lower()
        app_list = super().get_app_list(request)
        results = []

        if query in EMPTY_VALUES:
            return HttpResponse()

        for app in app_list:
            if query in app["name"].lower():
                results.append(app)
                continue

            models = []

            for model in app["models"]:
                if query in model["name"].lower():
                    models.append(model)

            if len(models) > 0:
                app["models"] = models
                results.append(app)

        return TemplateResponse(
            request,
            template="unfold/helpers/search_results.html",
            context={
                "results": results,
            },
        )

    @method_decorator(never_cache)
    @login_not_required
    def login(
        self, request: HttpRequest, extra_context: Optional[dict[str, Any]] = None
    ) -> HttpResponse:
        extra_context = {} if extra_context is None else extra_context
        image = self._get_value(
            get_config(self.settings_name)["LOGIN"].get("image"), request
        )

        redirect_field_name = self._get_value(
            get_config(self.settings_name)["LOGIN"].get("redirect_after"), request
        )

        if image not in EMPTY_VALUES:
            extra_context.update(
                {
                    "image": image,
                }
            )

        if redirect_field_name not in EMPTY_VALUES:
            extra_context.update({REDIRECT_FIELD_NAME: redirect_field_name})

        return super().login(request, extra_context)

    def password_change(
        self, request: HttpRequest, extra_context: Optional[dict[str, Any]] = None
    ) -> HttpResponse:
        from django.contrib.auth.views import PasswordChangeView

        from .forms import AdminOwnPasswordChangeForm

        url = reverse(f"{self.name}:password_change_done", current_app=self.name)
        defaults = {
            "form_class": AdminOwnPasswordChangeForm,
            "success_url": url,
            "extra_context": {**self.each_context(request), **(extra_context or {})},
        }
        if self.password_change_template is not None:
            defaults["template_name"] = self.password_change_template
        request.current_app = self.name
        return PasswordChangeView.as_view(**defaults)(request)

    def get_sidebar_list(self, request: HttpRequest) -> list[dict[str, Any]]:
        navigation = self._get_value(
            self._get_config("SIDEBAR", request).get("navigation"), request
        )
        tabs = self._get_value(self._get_config("TABS", request), request) or []
        results = []

        for group in copy.deepcopy(navigation):
            allowed_items = []

            for item in group["items"]:
                if "active" in item:
                    item["active"] = self._get_value(item["active"], request)
                else:
                    item["active"] = self._get_is_active(
                        request, item.get("link_callback") or item["link"]
                    )

                # Checks if any tab item is active and then marks the sidebar link as active
                for tab in tabs:
                    has_primary_link = False
                    has_tab_link_active = False

                    for tab_item in tab["items"]:
                        if item["link"] == tab_item["link"]:
                            has_primary_link = True
                            continue

                        if self._get_is_active(
                            request, tab_item.get("link_callback") or tab_item["link"]
                        ):
                            has_tab_link_active = True
                            break

                    if has_primary_link and has_tab_link_active:
                        item["active"] = True

                if isinstance(item["link"], Callable):
                    item["link_callback"] = lazy(item["link"])(request)

                # Permission callback
                item["has_permission"] = self._call_permission_callback(
                    item.get("permission"), request
                )

                # Badge callbacks
                if "badge" in item and isinstance(item["badge"], str):
                    try:
                        callback = import_string(item["badge"])
                        item["badge_callback"] = lazy(callback)(request)
                    except ImportError:
                        pass

                allowed_items.append(item)

            group["items"] = allowed_items

            results.append(group)

        return results

    def get_tabs_list(self, request: HttpRequest) -> list[dict[str, Any]]:
        tabs = copy.deepcopy(self._get_config("TABS", request))

        if not tabs:
            return []

        for tab in tabs:
            allowed_items = []

            for item in tab["items"]:
                item["has_permission"] = self._call_permission_callback(
                    item.get("permission"), request
                )

                if isinstance(item["link"], Callable):
                    item["link_callback"] = lazy(item["link"])(request)

                if "active" not in item:
                    item["active"] = self._get_is_active(
                        request, item.get("link_callback") or item["link"], True
                    )
                else:
                    item["active"] = self._get_value(item["active"], request)

                allowed_items.append(item)

            tab["items"] = allowed_items

        return tabs

    def _call_permission_callback(
        self, callback: Union[str, Callable, None], request: HttpRequest
    ) -> bool:
        if callback is None:
            return True

        if isinstance(callback, str):
            try:
                callback = import_string(callback)
            except ImportError:
                pass

        if isinstance(callback, str) or isinstance(callback, Callable):
            # We are not able to use here "is" because type is lazy loaded function
            if lazy(callback)(request) == True:  # noqa: E712
                return True

        return False

    def _replace_values(self, target: dict, source: dict, request: HttpRequest):
        for key in source.keys():
            if source[key] is not None and callable(source[key]):
                target[key] = source[key](request)
            else:
                target[key] = source[key]

        return target

    def _get_is_active(
        self, request: HttpRequest, link: Union[str, Callable], is_tab: bool = False
    ) -> bool:
        if not isinstance(link, str):
            link = str(link)

        index_path = reverse_lazy(f"{self.name}:index")
        link_path = urlparse(link).path

        # Dashboard
        if link_path == request.path == index_path:
            return True

        if link_path != "" and link_path in request.path and link_path != index_path:
            query_params = parse_qs(urlparse(link).query)
            request_params = parse_qs(request.GET.urlencode())

            # In case of tabs, we need to check if the query params are the same
            if is_tab and not all(
                request_params.get(k) == v for k, v in query_params.items()
            ):
                return False

            return True

        return False

    def _get_config(self, key: str, *args) -> Any:
        config = get_config(self.settings_name)

        if key in config and config[key]:
            return self._get_value(config[key], *args)

    def _get_theme_images(
        self, key: str, *args: Any
    ) -> Union[dict[str, str], str, None]:
        images = self._get_config(key, *args)

        if isinstance(images, dict):
            if "light" in images and "dark" in images:
                return {
                    "light": self._get_value(images["light"], *args),
                    "dark": self._get_value(images["dark"], *args),
                }

            return None

        return images

    def _get_colors(self, key: str, *args) -> dict[str, dict[str, str]]:
        colors = self._get_config(key, *args)

        def rgb_to_values(value: str) -> str:
            return " ".join(
                list(
                    map(
                        str.strip,
                        value.removeprefix("rgb(").removesuffix(")").split(","),
                    )
                )
            )

        def hex_to_values(value: str) -> str:
            return " ".join(str(item) for item in hex_to_rgb(value))

        for name, weights in colors.items():
            weights = self._get_value(weights, *args)
            colors[name] = weights

            for weight, value in weights.items():
                if value[0] == "#":
                    colors[name][weight] = hex_to_values(value)
                elif value.startswith("rgb"):
                    colors[name][weight] = rgb_to_values(value)

        return colors

    def _get_list(self, key: str, *args) -> list[Any]:
        items = get_config(self.settings_name)[key]

        if isinstance(items, list):
            return [self._get_value(item, *args) for item in items]

        return []

    def _get_favicons(self, key: str, *args) -> list[Favicon]:
        favicons = self._get_config(key, *args)

        if not favicons:
            return []

        return [
            Favicon(
                href=self._get_value(item["href"], *args),
                rel=item.get("rel"),
                sizes=item.get("sizes"),
                type=item.get("type"),
            )
            for item in favicons
        ]

    def _get_site_dropdown_items(self, key: str, *args) -> list[dict[str, Any]]:
        items = self._get_config(key, *args)

        if not items:
            return []

        return [
            DropdownItem(
                title=item.get("title"),
                link=self._get_value(item["link"], *args),
                icon=item.get("icon"),
            )
            for item in items
        ]

    def _get_value(
        self, value: Union[str, Callable, lazy, None], *args: Any
    ) -> Optional[str]:
        if value is None:
            return None

        if isinstance(value, str):
            try:
                callback = import_string(value)
                return callback(*args)
            except ImportError:
                pass

            return value

        if isinstance(value, Callable):
            return value(*args)

        return value
