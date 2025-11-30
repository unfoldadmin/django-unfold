import copy
import hashlib
import time
from collections.abc import Callable
from typing import Any
from urllib.parse import parse_qs, urlparse

from django.contrib.admin import AdminSite
from django.core.cache import cache
from django.core.paginator import Paginator
from django.core.validators import EMPTY_VALUES
from django.http import HttpRequest, HttpResponse
from django.template.response import TemplateResponse
from django.urls import URLPattern, path, reverse, reverse_lazy
from django.utils.encoding import force_bytes
from django.utils.functional import lazy
from django.utils.module_loading import import_string

from unfold.dataclasses import DropdownItem, Favicon, SearchResult

try:
    from django.contrib.auth.decorators import login_not_required
except ImportError:

    def login_not_required(func: Callable) -> Callable:
        return func


from unfold.settings import get_config
from unfold.utils import convert_color
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

        custom_login_form = get_config(self.settings_name)["LOGIN"]["form"]

        if custom_login_form is not None:
            self.login_form = import_string(custom_login_form)
        elif self.login_form is None:
            self.login_form = AuthenticationForm

    def get_urls(self) -> list[URLPattern]:
        extra_urls = []

        if hasattr(self, "extra_urls") and callable(self.extra_urls):
            extra_urls = self.extra_urls()

        urlpatterns = (
            [
                path("search/", self.admin_view(self.search), name="search"),
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
            "login_image": self._get_value(
                get_config(self.settings_name)["LOGIN"].get("image"), request
            ),
            "show_history": self._get_config("SHOW_HISTORY", request),
            "show_view_on_site": self._get_config("SHOW_VIEW_ON_SITE", request),
            "show_languages": self._get_config("SHOW_LANGUAGES", request),
            "language_flags": self._get_config("LANGUAGE_FLAGS", request),
            "show_back_button": self._get_config("SHOW_BACK_BUTTON", request),
            "theme": self._get_config("THEME", request),
            "border_radius": self._get_config("BORDER_RADIUS", request),
            "colors": self._get_colors("COLORS", request),
            "environment": self._get_config("ENVIRONMENT", request),
            "environment_title_prefix": self._get_config(
                "ENVIRONMENT_TITLE_PREFIX", request
            ),
            "languages_list": self._get_value(
                self._get_config("LANGUAGES", request).get("navigation"), request
            ),
            "languages_action": self._get_value(
                self._get_config("LANGUAGES", request).get("action"), request
            ),
            "account_links": self._get_account_links(request),
            "tab_list": self.get_tabs_list(request),
            "styles": self._get_list("STYLES", request),
            "scripts": self._get_list("SCRIPTS", request),
            "command_show_history": self._get_config("COMMAND", request).get(
                "show_history"
            ),
            "sidebar_command_search": self._get_config("SIDEBAR", request).get(
                "command_search"
            ),
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
        self, request: HttpRequest, extra_context: dict[str, Any] | None = None
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

    def _search_apps(
        self, app_list: list[dict[str, Any]], search_term: str
    ) -> list[SearchResult]:
        results = []
        apps = []

        for app in app_list:
            if search_term in app["name"].lower():
                apps.append(app)
                continue

            models = []

            for model in app["models"]:
                if search_term in model["name"].lower():
                    models.append(model)

            if len(models) > 0:
                app["models"] = models
                apps.append(app)

        for app in apps:
            for model in app["models"]:
                results.append(
                    SearchResult(
                        title=str(model["name"]),
                        description=app["name"],
                        link=model["admin_url"],
                        icon="tag",
                    )
                )

        return results

    def _search_models(
        self,
        request: HttpRequest,
        app_list: list[dict[str, Any]],
        search_term: str,
        allowed_models: list[str] | None = None,
    ) -> list[SearchResult]:
        results = []

        for app in app_list:
            for model in app["models"]:
                # Skip models which are not allowed
                if isinstance(allowed_models, list | tuple):
                    if model["model"]._meta.label.lower() not in [
                        m.lower() for m in allowed_models
                    ]:
                        continue

                admin_instance = self._registry.get(model["model"])
                search_fields = admin_instance.get_search_fields(request)

                if not search_fields:
                    continue

                pks = []

                qs = admin_instance.get_queryset(request)
                search_results, _has_duplicates = admin_instance.get_search_results(
                    request, qs, search_term
                )

                for item in search_results:
                    if item.pk in pks:
                        continue

                    pks.append(item.pk)

                    link = reverse_lazy(
                        f"{self.name}:{admin_instance.model._meta.app_label}_{admin_instance.model._meta.model_name}_change",
                        args=(item.pk,),
                    )

                    results.append(
                        SearchResult(
                            title=str(item),
                            description=f"{item._meta.app_label.capitalize()} - {item._meta.verbose_name.capitalize()}",
                            link=link,
                            icon="data_object",
                        )
                    )

        return results

    def search(
        self, request: HttpRequest, extra_context: dict[str, Any] | None = None
    ) -> TemplateResponse:
        start_time = time.time()

        CACHE_TIMEOUT = 5 * 60
        PER_PAGE = 100

        search_term = request.GET.get("s")
        extended_search = "extended" in request.GET
        app_list = super().get_app_list(request)
        template_name = "unfold/helpers/search_results.html"

        if search_term in EMPTY_VALUES:
            return HttpResponse()

        search_term = search_term.lower()
        search_key_base = f"{request.user.pk}_{search_term}"
        cache_key = (
            f"unfold_search_{hashlib.sha256(force_bytes(search_key_base)).hexdigest()}"
        )
        cache_results = cache.get(cache_key)

        if extended_search:
            template_name = "unfold/helpers/command_results.html"

        if cache_results:
            results = cache_results
        else:
            results = self._search_apps(app_list, search_term)

            if extended_search:
                if search_callback := self._get_config("COMMAND", request).get(
                    "search_callback"
                ):
                    results.extend(
                        self._get_value(search_callback, request, search_term)
                    )

                search_models = self._get_value(
                    self._get_config("COMMAND", request).get("search_models"), request
                )

                if search_models is True or isinstance(search_models, list | tuple):
                    allowed_models = (
                        search_models
                        if isinstance(search_models, list | tuple)
                        else None
                    )

                    results.extend(
                        self._search_models(
                            request, app_list, search_term, allowed_models
                        )
                    )

            cache.set(cache_key, results, timeout=CACHE_TIMEOUT)

        execution_time = time.time() - start_time
        paginator = Paginator(results, PER_PAGE)

        show_history = self._get_value(
            self._get_config("COMMAND", request).get("show_history"), request
        )

        return TemplateResponse(
            request,
            template=template_name,
            context={
                "page_obj": paginator,
                "results": paginator.page(request.GET.get("page", 1)),
                "page_counter": (int(request.GET.get("page", 1)) - 1) * PER_PAGE,
                "execution_time": execution_time,
                "command_show_history": show_history,
            },
            headers={
                "HX-Trigger": "search",
            },
        )

    def password_change(
        self, request: HttpRequest, extra_context: dict[str, Any] | None = None
    ) -> HttpResponse:
        from django.contrib.auth.views import PasswordChangeView

        from unfold.forms import AdminOwnPasswordChangeForm

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
            group["items"] = self._get_navigation_items(request, group["items"], tabs)

            # Badge callbacks
            if "badge" in group and isinstance(group["badge"], str):
                try:
                    callback = import_string(group["badge"])
                    group["badge_callback"] = lazy(callback)(request)
                except ImportError:
                    pass

            results.append(group)

        return results

    def _get_navigation_items(
        self, request: HttpRequest, items: list[dict], tabs: list[dict] = None
    ) -> list:
        allowed_items = []

        for item in items:
            link = item.get("link")

            if "active" in item:
                item["active"] = self._get_value(item["active"], request)
            else:
                item["active"] = self._get_is_active(
                    request, item.get("link_callback") or link
                )

            # Checks if any tab item is active and then marks the sidebar link as active
            if tabs and self._get_is_tab_active(request, tabs, link):
                item["active"] = True

            # Link callback
            if isinstance(link, Callable):
                item["link_callback"] = lazy(link)(request)

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

            # Process nested items
            if "items" in item:
                item["items"] = self._get_navigation_items(request, item["items"])

            allowed_items.append(item)

        return allowed_items

    def _get_account_links(self, request: HttpRequest) -> list[dict[str, Any]]:
        links = []

        navigation = self._get_value(
            get_config(self.settings_name)["ACCOUNT"].get("navigation"), request
        )

        for item in navigation:
            links.append(
                {
                    "title": self._get_value(item["title"], request),
                    "link": self._get_value(item["link"], request),
                }
            )

        return links

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
        self, callback: str | Callable | None, request: HttpRequest
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
        self, request: HttpRequest, link: str | Callable, is_tab: bool = False
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

    def _get_is_tab_active(
        self, request: HttpRequest, tabs: list[dict], link: str
    ) -> bool:
        for tab in tabs:
            has_primary_link = False
            has_tab_link_active = False

            for tab_item in tab["items"]:
                if link == tab_item["link"]:
                    has_primary_link = True
                    continue

                if self._get_is_active(
                    request, tab_item.get("link_callback") or tab_item["link"]
                ):
                    has_tab_link_active = True
                    continue

            if has_primary_link and has_tab_link_active:
                return True

        return False

    def _get_config(self, key: str, *args) -> Any:
        config = get_config(self.settings_name)

        if key in config and config[key]:
            return self._get_value(config[key], *args)

    def _get_theme_images(self, key: str, *args: Any) -> dict[str, str] | str | None:
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

        for name, weights in colors.items():
            weights = self._get_value(weights, *args)
            colors[name] = weights

            for weight, value in weights.items():
                colors[name][weight] = convert_color(value)

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
                attrs=item.get("attrs"),
            )
            for item in items
        ]

    def _get_value(self, value: str | Callable | None, *args: Any) -> str | None:
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
