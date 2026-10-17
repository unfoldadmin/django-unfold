from typing import Any

from django.contrib import messages
from django.contrib.admin import ModelAdmin, helpers
from django.contrib.admin.exceptions import DisallowedModelAdminToField
from django.contrib.admin.options import TO_FIELD_VAR
from django.contrib.admin.utils import unquote
from django.contrib.admin.views import main
from django.contrib.admin.views.main import IGNORED_PARAMS
from django.core.exceptions import PermissionDenied
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.utils.translation import gettext_lazy as _

from unfold.datasets import BaseDataset


class DatasetModelAdminMixin(ModelAdmin):
    change_form_datasets: list[type[BaseDataset]] | tuple[type[BaseDataset], ...] = ()

    def changeform_view(
        self,
        request: HttpRequest,
        object_id: str | None = None,
        form_url: str = "",
        extra_context: dict[str, Any] | None = None,
    ) -> HttpResponse:
        self.request = request
        extra_context = extra_context or {}
        datasets = self.get_changeform_datasets(request)

        # Monkeypatch IGNORED_PARAMS to add dataset page and search arguments into ignored params
        ignored_params = []
        for dataset in datasets:
            ignored_params.append(f"{dataset.model._meta.model_name}-q")
            ignored_params.append(f"{dataset.model._meta.model_name}-p")
            ignored_params.append("_changelist_filters")

        main.IGNORED_PARAMS = (*IGNORED_PARAMS, *ignored_params)

        rendered_datasets = []
        for dataset in datasets:
            rendered_datasets.append(
                dataset(
                    request=request,
                    extra_context={
                        "object": object_id,
                    },
                )
            )

        extra_context["datasets"] = rendered_datasets

        if request.method == "POST" and "_dataset" in request.POST:
            self._check_dataset_action_permissions(request, object_id)

            selected = request.POST.getlist(helpers.ACTION_CHECKBOX_NAME)

            if not selected or helpers.ACTION_CHECKBOX_NAME not in request.POST:
                messages.warning(
                    request,
                    _(
                        "Items must be selected in order to perform actions on them. No items have been changed."
                    ),
                )
                return HttpResponseRedirect(request.get_full_path())

            dataset = None
            for item in rendered_datasets:
                if item.id == request.POST["_dataset"]:
                    dataset = item

            if not dataset:
                messages.warning(
                    request,
                    _("Dataset not found. No action performed."),
                )
                return HttpResponseRedirect(request.get_full_path())

            response = dataset.model_admin_instance.response_action(
                request, queryset=dataset.cl.get_queryset(request)
            )

            if response:
                return response

        return super().changeform_view(request, object_id, form_url, extra_context)

    def get_changeform_datasets(
        self, request: HttpRequest
    ) -> list[type[BaseDataset]] | tuple[type[BaseDataset], ...]:
        return self.change_form_datasets

    def _check_dataset_action_permissions(
        self, request: HttpRequest, object_id: str | None
    ) -> None:
        to_field = request.POST.get(TO_FIELD_VAR, request.GET.get(TO_FIELD_VAR))

        if to_field and not self.to_field_allowed(request, to_field):
            raise DisallowedModelAdminToField(
                f"The field {to_field} cannot be referenced."
            )

        if request.method == "POST" and "_saveasnew" in request.POST:
            object_id = None

        if _add := object_id is None:
            if not self.has_add_permission(request):
                raise PermissionDenied

            obj = None
        else:
            obj = self.get_object(request, unquote(object_id), to_field)

        if not self.has_view_or_change_permission(request, obj):
            raise PermissionDenied
