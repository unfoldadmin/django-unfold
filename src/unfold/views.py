from typing import Any

import django
from django.contrib.admin.views.main import ERROR_FLAG, PAGE_VAR
from django.contrib.admin.views.main import ChangeList as BaseChangeList
from django.contrib.auth.mixins import PermissionRequiredMixin

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
        if not hasattr(self, "model_admin"):
            raise UnfoldException(
                "UnfoldModelAdminViewMixin was not provided with 'model_admin' argument"
            )

        if not hasattr(self, "title"):
            raise UnfoldException(
                "UnfoldModelAdminViewMixin was not provided with 'title' attribute"
            )

        return super().get_context_data(
            **kwargs,
            **self.model_admin.admin_site.each_context(self.request),
            **{"title": self.title},
        )
