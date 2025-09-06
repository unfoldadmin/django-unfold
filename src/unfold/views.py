from typing import Any

import django
from django.contrib.admin.views.main import ERROR_FLAG, PAGE_VAR
from django.contrib.admin.views.main import ChangeList as BaseChangeList
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.views.generic import TemplateView

from unfold.exceptions import UnfoldException


class ChangeList(BaseChangeList):
    def __init__(self, request, *args, **kwargs):
        super().__init__(request, *args, **kwargs)

        if django.VERSION < (5, 0):
            self.filter_params = dict(request.GET.lists())
            self.filter_params.pop(PAGE_VAR, None)
            self.filter_params.pop(ERROR_FLAG, None)


class UnfoldModelAdminViewMixin(PermissionRequiredMixin):
    """
    Prepares views to be displayed in admin
    """

    model_admin = None

    def __init__(self, model_admin, **kwargs):
        self.model_admin = model_admin
        super().__init__(**kwargs)

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        self.request.current_app = self.model_admin.admin_site.name

        if not hasattr(self, "model_admin"):
            raise UnfoldException(
                "UnfoldModelAdminViewMixin was not provided with 'model_admin' argument"
            )

        if not hasattr(self, "title") and not hasattr(self, "get_title"):
            raise UnfoldException(
                "UnfoldModelAdminViewMixin requires a 'title' attribute or a 'get_title' method."
            )

        context = {
            "title": self.get_title(),
            "model_admin": self.model_admin,
            **self.model_admin.admin_site.each_context(self.request),
        }
        context.update(kwargs)
        return super().get_context_data(**context)

    def get_title(self) -> str:
        return self.title


class UnfoldAdminView(UnfoldModelAdminViewMixin, TemplateView):
    """
    Base class for creating custom admin views.
    """

    title = None
    template_name = None

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context.update(self.get_extra_context())
        return context

    def get_extra_context(self) -> dict[str, Any]:
        return {}
