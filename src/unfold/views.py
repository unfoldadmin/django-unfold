from typing import Any

import django
from django.contrib.admin.views import main
from django.contrib.admin.views.main import ERROR_FLAG, PAGE_VAR
from django.contrib.admin.views.main import ChangeList as BaseChangeList
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.http import HttpRequest

from unfold.exceptions import UnfoldException
from unfold.forms import DatasetChangeListSearchForm


class ChangeList(BaseChangeList):
    def __init__(self, request: HttpRequest, *args: Any, **kwargs: Any) -> None:
        super().__init__(request, *args, **kwargs)

        if django.VERSION < (5, 0):
            self.filter_params = dict(request.GET.lists())
            self.filter_params.pop(PAGE_VAR, None)
            self.filter_params.pop(ERROR_FLAG, None)


class DatasetChangeList(ChangeList):
    is_dataset = True
    search_form_class = DatasetChangeListSearchForm

    def __init__(self, request: HttpRequest, *args: Any, **kwargs: Any) -> None:
        # Monkeypatch SEARCH_VAR and PAGE_VAR for custom datasets
        main.SEARCH_VAR = f"{kwargs.get('model')._meta.model_name}-q"
        main.PAGE_VAR = f"{kwargs.get('model')._meta.model_name}-p"
        super().__init__(request, *args, **kwargs)


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

        if not hasattr(self, "title"):
            raise UnfoldException(
                "UnfoldModelAdminViewMixin was not provided with 'title' attribute"
            )

        return super().get_context_data(
            **kwargs,
            **self.model_admin.admin_site.each_context(self.request),
            **{
                "title": self.title,
                "model_admin": self.model_admin,
            },
        )
