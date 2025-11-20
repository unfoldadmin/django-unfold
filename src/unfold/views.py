from typing import Any

import django
from django.contrib import messages
from django.contrib.admin.views.main import ERROR_FLAG, PAGE_VAR
from django.contrib.admin.views.main import ChangeList as BaseChangeList
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.http import HttpRequest, JsonResponse
from django.views.generic import ListView

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

    def __init__(self, request: HttpRequest, *args: Any, **kwargs: Any) -> None:
        self.search_var = f"{kwargs.get('model')._meta.model_name}-q"
        self.page_var = f"{kwargs.get('model')._meta.model_name}-p"

        _search_form = DatasetChangeListSearchForm(
            request.GET, search_var=self.search_var
        )
        if not _search_form.is_valid():
            for error in _search_form.errors.values():
                messages.error(request, ", ".join(error))

        self.dataset_search_query = _search_form.cleaned_data.get(self.search_var) or ""

        super().__init__(request, *args, **kwargs)

    def get_results(self, request: HttpRequest) -> None:
        try:
            self.page_num = int(request.GET.get(self.page_var, 1))
        except ValueError:
            self.page_num = 1

        super().get_results(request)

    def get_queryset(self, request, exclude_parameters=None):
        self.query = self.dataset_search_query
        return super().get_queryset(request, exclude_parameters)


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


class BaseAutocompleteView(ListView):
    paginate_by = 20

    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> JsonResponse:
        super().get(request, *args, **kwargs)
        context = self.get_context_data()

        return JsonResponse(
            {
                "results": [
                    {
                        "id": obj.pk,
                        "text": str(obj),
                    }
                    for obj in self.object_list
                ],
                "pagination": {
                    "more": context["page_obj"].has_next(),
                },
            }
        )
