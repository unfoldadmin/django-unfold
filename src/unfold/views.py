from typing import TYPE_CHECKING, Any

from django.contrib import messages
from django.contrib.admin import AdminSite
from django.contrib.admin.filters import ListFilter
from django.contrib.admin.views.autocomplete import AutocompleteJsonView
from django.contrib.admin.views.main import ChangeList as BaseChangeList
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.core.exceptions import FieldDoesNotExist, PermissionDenied, ValidationError
from django.db import models
from django.db.models import QuerySet
from django.http import HttpRequest, JsonResponse
from django.views import View
from django.views.generic import ListView
from django.views.generic.base import ContextMixin

from unfold.exceptions import UnfoldException
from unfold.forms import DatasetChangeListSearchForm

if TYPE_CHECKING:
    from django.contrib.admin.options import ModelAdmin


class ChangeList(BaseChangeList):
    def __init__(self, request: HttpRequest, *args: Any, **kwargs: Any) -> None:
        super().__init__(request, *args, **kwargs)


class DatasetChangeList(ChangeList):
    is_dataset = True

    def __init__(self, request: HttpRequest, *args: Any, **kwargs: Any) -> None:
        self.search_var = f"{kwargs['model']._meta.model_name}-q"
        self.page_var = f"{kwargs['model']._meta.model_name}-p"

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

    def get_queryset(
        self, request: HttpRequest, exclude_parameters: list[str | None] | None = None
    ) -> QuerySet:
        self.query = self.dataset_search_query
        return super().get_queryset(request, exclude_parameters)

    def get_filters(
        self, request: HttpRequest
    ) -> tuple[list[ListFilter], bool, dict[str, bool | str], bool, bool]:
        # Disable filters for dataset
        return ([], False, {}, False, False)


class UnfoldSiteViewMixin(PermissionRequiredMixin, ContextMixin, View):
    admin_site: AdminSite | None = None

    def __init__(self, admin_site: AdminSite | None = None, **kwargs: Any) -> None:
        self.admin_site = admin_site
        super().__init__(**kwargs)

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        if self.admin_site is None:
            raise UnfoldException(
                "UnfoldSiteViewMixin was not provided with 'admin_site' argument"
            )

        if not hasattr(self, "title"):
            raise UnfoldException(
                "UnfoldSiteViewMixin was not provided with 'title' attribute"
            )

        self.request.current_app = self.admin_site.name

        context = super().get_context_data(**kwargs)
        context.update(
            **self.admin_site.each_context(self.request),
            **{
                "title": self.title,
            },
        )

        return context


class UnfoldModelAdminViewMixin(PermissionRequiredMixin, ContextMixin, View):
    model_admin: "ModelAdmin | None" = None

    def __init__(self, model_admin: "ModelAdmin | None" = None, **kwargs: Any) -> None:
        self.model_admin = model_admin
        super().__init__(**kwargs)

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        if self.model_admin is None:
            raise UnfoldException(
                "UnfoldModelAdminViewMixin was not provided with 'model_admin' argument"
            )

        if not hasattr(self, "title"):
            raise UnfoldException(
                "UnfoldModelAdminViewMixin was not provided with 'title' attribute"
            )

        self.request.current_app = self.model_admin.admin_site.name

        context = super().get_context_data(**kwargs)
        context.update(
            {
                **self.model_admin.admin_site.each_context(self.request),
                "title": self.title,
                "model_admin": self.model_admin,
            }
        )

        return context


class BaseAutocompleteView(ListView):
    paginate_by = 20

    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> JsonResponse:
        super().get(request, *args, **kwargs)
        context = self.get_context_data()

        return JsonResponse(
            {
                "results": [
                    {
                        "id": str(obj.pk),
                        "text": str(obj),
                    }
                    for obj in context["object_list"]
                ],
                "pagination": {
                    "more": context["page_obj"].has_next(),
                },
            }
        )


DEPENDENT_PARENT_PARAM = "dependent_parent"


class DependentAutocompleteJsonView(AutocompleteJsonView):
    """Apply one configured ForeignKey filter before Django's autocomplete search."""

    source_model_admin = None

    def process_request(self, request: HttpRequest):
        result = super().process_request(request)
        if self.source_model_admin is None:
            raise PermissionDenied

        # The custom URL is owned by one source ModelAdmin. Do not permit a
        # caller to substitute another source model or autocomplete field.
        if result[2].model is not self.source_model_admin.model:
            raise PermissionDenied

        dependency = self.source_model_admin.get_autocomplete_dependency_config(
            result[2].name
        )
        if dependency is None:
            raise PermissionDenied
        parent_name = dependency["depends_on"]
        lookup = dependency["lookup"]
        if "__" in lookup:
            raise PermissionDenied

        try:
            self.source_parent_field = self.source_model_admin.model._meta.get_field(
                parent_name
            )
            self.target_parent_field = result[1].model._meta.get_field(lookup)
        except FieldDoesNotExist as exc:
            raise PermissionDenied from exc
        if (
            not isinstance(self.source_parent_field, models.ForeignKey)
            or not isinstance(self.target_parent_field, models.ForeignKey)
            or self.target_parent_field.remote_field.model
            is not self.source_parent_field.remote_field.model
        ):
            raise PermissionDenied
        return result

    def get_queryset(self) -> QuerySet:
        queryset = self.model_admin.get_queryset(self.request)
        queryset = queryset.complex_filter(self.source_field.get_limit_choices_to())

        parent_value = self.request.GET.get(DEPENDENT_PARENT_PARAM)
        if not parent_value:
            return queryset.none()
        try:
            parent_value = self.source_parent_field.target_field.to_python(parent_value)
        except (TypeError, ValueError, ValidationError):
            return queryset.none()

        queryset = queryset.filter(**{self.target_parent_field.name: parent_value})
        queryset, search_use_distinct = self.model_admin.get_search_results(
            self.request, queryset, self.term
        )
        if search_use_distinct:
            queryset = queryset.distinct()
        return queryset
