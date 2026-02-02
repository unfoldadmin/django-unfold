from typing import Any

from django.contrib import messages
from django.contrib.admin import helpers
from django.contrib.admin.views import main
from django.contrib.admin.views.main import IGNORED_PARAMS
from django.http import HttpRequest, HttpResponseRedirect
from django.template.response import TemplateResponse
from django.utils.translation import gettext_lazy as _


class DatasetModelAdminMixin:
    def changeform_view(
        self,
        request: HttpRequest,
        object_id: str | None = None,
        form_url: str = "",
        extra_context: dict[str, Any] | None = None,
    ) -> TemplateResponse:
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

        if request.method == "POST" and "dataset" in request.POST:
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
                if item.id == request.POST["dataset"]:
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
