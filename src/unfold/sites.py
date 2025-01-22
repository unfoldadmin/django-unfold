from http import HTTPStatus
from typing import Any, Callable, Dict, List, Optional, Union
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

try:
    from django.contrib.auth.decorators import login_not_required
except ImportError:

    def login_not_required(func: Callable) -> Callable:
        return func


from .dataclasses import Favicon
from .settings import get_config
from .utils import hex_to_rgb
from .widgets import CHECKBOX_CLASSES, INPUT_CLASSES


class UnfoldAdminSite(AdminSite):
    default_site = "unfold.admin.UnfoldAdminSite"
    settings_name = "UNFOLD"

    def __init__(self, name: str = "admin") -> None:
        from .forms import AuthenticationForm

        super().__init__(name)

        if self.login_form is None:
            self.login_form = AuthenticationForm

        if get_config(self.settings_name)["SITE_TITLE"]:
            self.site_title = get_config(self.settings_name)["SITE_TITLE"]

        if get_config(self.settings_name)["SITE_HEADER"]:
            self.site_header = get_config(self.settings_name)["SITE_HEADER"]

        if get_config(self.settings_name)["SITE_URL"]:
            self.site_url = get_config(self.settings_name)["SITE_URL"]

    def get_urls(self) -> List[URLPattern]:
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

    def each_context(self, request: HttpRequest) -> Dict[str, Any]:
        context = super().each_context(request)

        context.update(
            {
                "form_classes": {
                    "text_input": INPUT_CLASSES,
                    "checkbox": CHECKBOX_CLASSES,
                },
                "site_logo": self._get_mode_images(
                    get_config(self.settings_name)["SITE_LOGO"], request
                ),
                "site_icon": self._get_mode_images(
                    get_config(self.settings_name)["SITE_ICON"], request
                ),
                "site_symbol": self._get_value(
                    get_config(self.settings_name)["SITE_SYMBOL"], request
                ),
                "site_favicons": self._process_favicons(
                    request, get_config(self.settings_name)["SITE_FAVICONS"]
                ),
                "show_history": get_config(self.settings_name)["SHOW_HISTORY"],
                "show_view_on_site": get_config(self.settings_name)[
                    "SHOW_VIEW_ON_SITE"
                ],
                "show_languages": get_config(self.settings_name)["SHOW_LANGUAGES"],
                "show_back_button": get_config(self.settings_name)["SHOW_BACK_BUTTON"],
                "colors": self._process_colors(
                    get_config(self.settings_name)["COLORS"]
                ),
                "border_radius": get_config(self.settings_name).get(
                    "BORDER_RADIUS", "6px"
                ),
                "tab_list": self.get_tabs_list(request),
                "styles": [
                    self._get_value(style, request)
                    for style in get_config(self.settings_name)["STYLES"]
                ],
                "theme": get_config(self.settings_name).get("THEME"),
                "scripts": [
                    self._get_value(script, request)
                    for script in get_config(self.settings_name)["SCRIPTS"]
                ],
                "sidebar_show_all_applications": get_config(self.settings_name)[
                    "SIDEBAR"
                ].get("show_all_applications"),
                "sidebar_show_search": get_config(self.settings_name)["SIDEBAR"].get(
                    "show_search"
                ),
                "sidebar_navigation": self.get_sidebar_list(request)
                if self.has_permission(request)
                else [],
            }
        )

        environment = get_config(self.settings_name)["ENVIRONMENT"]

        if environment and isinstance(environment, str):
            try:
                callback = import_string(environment)
                context.update({"environment": callback(request)})
            except ImportError:
                pass

        if hasattr(self, "extra_context") and callable(self.extra_context):
            return self.extra_context(context, request)

        return context

    def index(
        self, request: HttpRequest, extra_context: Optional[Dict[str, Any]] = None
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
        self, request: HttpRequest, extra_context: Optional[Dict[str, Any]] = None
    ) -> HttpResponse:
        if "toggle_sidebar" not in request.session:
            request.session["toggle_sidebar"] = True
        else:
            request.session["toggle_sidebar"] = not request.session["toggle_sidebar"]

        return HttpResponse(status=HTTPStatus.OK)

    def search(
        self, request: HttpRequest, extra_context: Optional[Dict[str, Any]] = None
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
        self, request: HttpRequest, extra_context: Optional[Dict[str, Any]] = None
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
        self, request: HttpRequest, extra_context: Optional[Dict[str, Any]] = None
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

    def get_sidebar_list(self, request: HttpRequest) -> List[Dict[str, Any]]:
        navigation = get_config(self.settings_name)["SIDEBAR"].get("navigation", [])
        tabs = get_config(self.settings_name)["TABS"]
        results = []

        for group in navigation:
            allowed_items = []

            for item in group["items"]:
                item["active"] = False
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

    def get_tabs_list(self, request: HttpRequest) -> List[Dict[str, Any]]:
        tabs = get_config(self.settings_name)["TABS"]

        for tab in tabs:
            allowed_items = []

            for item in tab["items"]:
                item["has_permission"] = self._call_permission_callback(
                    item.get("permission"), request
                )

                if isinstance(item["link"], Callable):
                    item["link_callback"] = lazy(item["link"])(request)

                item["active"] = self._get_is_active(
                    request, item.get("link_callback") or item["link"], True
                )
                allowed_items.append(item)

            tab["items"] = allowed_items

        return tabs

    def _get_mode_images(
        self, images: Union[Dict[str, callable], callable, str], request: HttpRequest
    ) -> Union[Dict[str, str], str, None]:
        if isinstance(images, dict):
            if "light" in images and "dark" in images:
                return {
                    "light": self._get_value(images["light"], request),
                    "dark": self._get_value(images["dark"], request),
                }

            return None

        return self._get_value(images, request)

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

    def _get_value(
        self, instance: Union[str, Callable, None], *args: Any
    ) -> Optional[str]:
        if instance is None:
            return None

        if isinstance(instance, str):
            return instance

        if isinstance(instance, Callable):
            return instance(*args)

        return None

    def _replace_values(self, target: Dict, source: Dict, request: HttpRequest):
        for key in source.keys():
            if source[key] is not None and callable(source[key]):
                target[key] = source[key](request)
            else:
                target[key] = source[key]

        return target

    def _process_favicons(
        self, request: HttpRequest, favicons: List[Dict]
    ) -> List[Favicon]:
        return [
            Favicon(
                href=self._get_value(item["href"], request),
                rel=item.get("rel"),
                sizes=item.get("sizes"),
                type=item.get("type"),
            )
            for item in favicons
        ]

    def _process_colors(
        self, colors: Dict[str, Dict[str, str]]
    ) -> Dict[str, Dict[str, str]]:
        for name, weights in colors.items():
            for weight, value in weights.items():
                if value[0] != "#":
                    continue

                colors[name][weight] = " ".join(str(item) for item in hex_to_rgb(value))

        return colors

    def _get_is_active(
        self, request: HttpRequest, link: str, is_tab: bool = False
    ) -> bool:
        if not isinstance(link, str):
            link = str(link)

        index_path = reverse_lazy(f"{self.name}:index")
        link_path = urlparse(link).path

        # Dashboard
        if link_path == request.path == index_path:
            return True

        if link_path in request.path and link_path != index_path:
            query_params = parse_qs(urlparse(link).query)
            request_params = parse_qs(request.GET.urlencode())

            # In case of tabs, we need to check if the query params are the same
            if is_tab and not all(
                request_params.get(k) == v for k, v in query_params.items()
            ):
                return False

            return True

        return False
