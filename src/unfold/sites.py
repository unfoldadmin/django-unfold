from http import HTTPStatus

from django.contrib.admin import AdminSite
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.core.validators import EMPTY_VALUES
from django.http import HttpResponse
from django.shortcuts import redirect
from django.template.response import TemplateResponse
from django.urls import path, reverse, reverse_lazy
from django.utils.module_loading import import_string

from .settings import get_config


class UnfoldAdminSite(AdminSite):
    default_site = "unfold.admin.UnfoldAdminSite"

    def __init__(self, name="admin"):
        from .forms import AuthenticationForm

        super().__init__(name)

        self.login_form = AuthenticationForm
        if get_config()["SITE_TITLE"]:
            self.site_title = get_config()["SITE_TITLE"]

        if get_config()["SITE_HEADER"]:
            self.site_header = get_config()["SITE_HEADER"]

        if get_config()["SITE_URL"]:
            self.site_url = get_config()["SITE_URL"]

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

        context.update(
            {
                "logo": self._get_value(get_config()["SIDEBAR"].get("logo"), request),
                "colors": get_config()["COLORS"],
                "icon": self._get_value(get_config()["SITE_ICON"], request),
                "tab_list": get_config()["TABS"],
                "styles": [
                    self._get_value(style, request) for style in get_config()["STYLES"]
                ],
                "scripts": [
                    self._get_value(script, request)
                    for script in get_config()["SCRIPTS"]
                ],
                "sidebar_show_all_applications": get_config()["SIDEBAR"].get(
                    "show_all_applications"
                ),
                "sidebar_show_search": get_config()["SIDEBAR"].get("show_search"),
                "sidebar_navigation": self.get_sidebar_list(request)
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

        dashboard_callback = get_config()["DASHBOARD_CALLBACK"]

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
        image = self._get_value(get_config()["LOGIN"].get("image"), request)

        redirect_field_name = self._get_value(
            get_config()["LOGIN"].get("redirect_after"), request
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

    def get_sidebar_list(self, request):
        navigation = get_config()["SIDEBAR"].get("navigation")
        results = []

        def _get_is_active(link):
            if not isinstance(link, str):
                link = str(link)

            if link in request.path and link != reverse_lazy("admin:index"):
                return True
            elif link == request.path == reverse_lazy("admin:index"):
                return True

            return False

        for group in navigation:
            for item in group["items"]:
                item["active"] = False
                item["active"] = _get_is_active(item["link"])

                for tab in get_config()["TABS"]:
                    has_primary_link = False
                    has_tab_link_active = False

                    for tab_item in tab["items"]:
                        if item["link"] == tab_item["link"]:
                            has_primary_link = True
                            continue

                        if _get_is_active(tab_item["link"]):
                            has_tab_link_active = True
                            break

                    if has_primary_link and has_tab_link_active:
                        item["active"] = True

                # Badge callbacks
                if "badge" in item and isinstance(item["badge"], str):
                    try:
                        item["badge"] = import_string(item["badge"])(request)
                    except ImportError:
                        pass

            results.append(group)

        return results

    def app_index(self, request, app_label, extra_context=None):
        return redirect("admin:index")

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
