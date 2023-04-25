from http import HTTPStatus
from typing import Any, Dict, List

from django.apps import apps
from django.contrib.admin import AdminSite
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.core.validators import EMPTY_VALUES
from django.http import HttpRequest, HttpResponse
from django.template.response import TemplateResponse
from django.urls import path, reverse, reverse_lazy
from django.utils.module_loading import import_string

from .settings import get_config
from .typing import ConfigModelEntry


class UnfoldAdminSite(AdminSite):
    default_site = "unfold.admin.UnfoldAdminSite"
    settings_name = "UNFOLD"

    def __init__(self, name="admin"):
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

    def get_urls(self):
        urlpatterns = [
            path("search/", self.admin_view(self.search), name="search"),
            path(
                "toggle-sidebar/",
                self.admin_view(self.toggle_sidebar),
                name="toggle_sidebar",
            ),
        ] + super().get_urls()

        return urlpatterns

    def each_context(self, request):
        context = super().each_context(request)

        available_apps = context["available_apps"]

        context.update(
            {
                "logo": self._get_value(
                    get_config(self.settings_name)["SIDEBAR"].get("logo"), request
                ),
                "colors": get_config(self.settings_name)["COLORS"],
                "icon": self._get_value(
                    get_config(self.settings_name)["SITE_ICON"], request
                ),
                "symbol": self._get_value(
                    get_config(self.settings_name)["SITE_SYMBOL"], request
                ),
                "tab_list": get_config(self.settings_name)["TABS"],
                "styles": [
                    self._get_value(style, request)
                    for style in get_config(self.settings_name)["STYLES"]
                ],
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
                "sidebar_navigation": self.get_sidebar_list(request, available_apps)
                if self.has_permission(request)
                else [],
            }
        )

        return context

    def index(self, request, extra_context=None):
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

    def toggle_sidebar(self, request, extra_context=None):
        if "toggle_sidebar" not in request.session:
            request.session["toggle_sidebar"] = True
        else:
            request.session["toggle_sidebar"] = not request.session["toggle_sidebar"]

        return HttpResponse(status=HTTPStatus.OK)

    def search(self, request, extra_context=None):
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

    def login(self, request, extra_context=None):
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

    def password_change(self, request, extra_context=None):
        from django.contrib.auth.views import PasswordChangeView

        from .forms import AdminOwnPasswordChangeForm

        url = reverse("admin:password_change_done", current_app=self.name)
        defaults = {
            "form_class": AdminOwnPasswordChangeForm,
            "success_url": url,
            "extra_context": {**self.each_context(request), **(extra_context or {})},
        }
        if self.password_change_template is not None:
            defaults["template_name"] = self.password_change_template
        request.current_app = self.name
        return PasswordChangeView.as_view(**defaults)(request)

    def get_sidebar_list(
        self, request: HttpRequest, available_apps: List[Dict[str, Any]]
    ):
        """
        Returns the list of sidebar navigation groups and items, filtered based on permissions and with
        flag "active", when user is currently visiting given item.
        :param request:
        :param available_apps: List of all available apps generated by Django Admin
        :return:
        """
        navigation = get_config(self.settings_name)["SIDEBAR"].get("navigation", [])
        results = []

        def _get_is_active(link: str) -> bool:
            """
            Returns whether `link` is currently active based on request path provided
            :param link: Reversed link containing URL path as string or lazy reversed proxy
            :return:
            """
            if not isinstance(link, str):
                link = str(link)

            return (
                link == request.path
                if link == reverse_lazy("admin:index")
                else link in request.path
            )

        def _filter_and_map_item_models(
            models: List[Dict[str, Any]]
        ) -> List[ConfigModelEntry]:
            """
            Returns filtered and mapped item models.
            :param models: The list of original item models
            :return:
            """

            def _map(model_entry: Dict[str, Any]) -> ConfigModelEntry:
                """
                Map each individual model entry in config to ConfigModelEntry typed dict
                :param model_entry: model entry from config under UNFOLD["SIDEBAR"]["navigation"]["items"]["models"]
                :return:
                """
                app_label, model_label = model_entry.get("model").split(".")
                model_class = apps.get_model(app_label, model_label)
                return {
                    "model": model_entry.get("model"),
                    "model_class": model_class,
                    "title": model_entry.get(
                        "title", model_class._meta.verbose_name_plural.title()
                    ),
                    "link": model_entry.get(
                        "link",
                        reverse_lazy(f"admin:{app_label}_{model_label}_changelist"),
                    ),
                    "active": False,
                }

            def _filter_permissions(model_entry: ConfigModelEntry) -> bool:
                """
                Filter each ConfigModelEntry based on whether current user has permissions to it.
                It is filtered based on available_apps (which are filtered by Django itself)
                :param model_entry:
                :return:
                """
                app_label, model_label = model_entry.get("model").split(".")
                for app in available_apps:
                    if app.get("app_label") == app_label:
                        for m in app.get("models", []):
                            if m.get("model", "") == model_entry.get("model_class"):
                                # When our model is found in available_apps, it means user has permissions to it
                                return True
                return False

            return [m for m in [_map(m) for m in models] if _filter_permissions(m)]

        def _filter_items_in_group_by_permissions(
            items: List[Dict[str, Any]]
        ) -> List[Dict[str, Any]]:
            """
            Filter all items passed to function based on whether user has permissions to it.
            In case there is `permission` attribute specified on item it is filtered based on it.
            If there is `models` attribute specified and `models` are empty, it means user has
            no access to models within the item, and therefore he has no access to item itself.
            :param items:
            :return:
            """

            def _filter(i: Dict[str, Any]) -> bool:
                # TODO add filtering based on permissions
                return bool(i.get("models", True))

            return [i for i in items if _filter(i)]

        for group in navigation:
            for item in group["items"]:
                if item.get("models"):
                    # Filter items based on permission
                    item["models"] = _filter_and_map_item_models(item["models"])
                    # If item has no link specified, we give it link to first of its models
                    if not item.get("link") and item["models"]:
                        item["link"] = item["models"][0]["link"]

                # If item had no link it means it has no link in config and
                # user has no permission to models inside this item
                if not item.get("link"):
                    continue

                item["active"] = _get_is_active(item["link"])

                # Search whether any model inside item is currently displayed and if yes,
                # highlight given item in sidebar
                for model in item.get("models", []):
                    if _get_is_active(model["link"]):
                        model["active"] = True
                        item["active"] = True

                # Badge callbacks
                if "badge" in item and isinstance(item["badge"], str):
                    try:
                        item["badge"] = import_string(item["badge"])(request)
                    except ImportError:
                        pass
            group["items"] = _filter_items_in_group_by_permissions(group["items"])
            # If group was left with no items in it, we don't want to add it into results
            if group["items"]:
                results.append(group)
        return results

    def _get_value(self, instance, *args):
        if instance is None:
            return None

        if isinstance(instance, str):
            return instance

        return instance(*args)

    def _replace_values(self, target, source, request):
        for key in source.keys():
            if source[key] is not None and callable(source[key]):
                target[key] = source[key](request)
            else:
                target[key] = source[key]

        return target
