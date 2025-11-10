from typing import Any

from django.contrib.admin import helpers
from django.contrib.admin.views import main
from django.contrib.admin.views.main import IGNORED_PARAMS
from django.http import HttpRequest
from django.template.response import TemplateResponse


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
        selected = request.POST.getlist(helpers.ACTION_CHECKBOX_NAME)

        if (
            request.method == "POST"
            and selected
            and "dataset" in request.POST
            and helpers.ACTION_CHECKBOX_NAME in request.POST
        ):
            dataset = None
            for item in rendered_datasets:
                if item.id == request.POST["dataset"]:
                    dataset = item

            response = dataset.model_admin_instance.response_action(
                request, queryset=dataset.cl.get_queryset(request)
            )

            if response:
                return response

        return super().changeform_view(request, object_id, form_url, extra_context)
