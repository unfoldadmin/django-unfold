from typing import Any

from django.contrib import admin
from django.http import HttpRequest
from django.template.loader import render_to_string

from unfold.views import DatasetChangeList


class BaseDataset:
    tab = False

    def __init__(
        self, request: HttpRequest, extra_context: dict[str, Any] | None
    ) -> None:
        self.request = request
        self.extra_context = extra_context

        self.model_admin_instance = self.model_admin(
            model=self.model, admin_site=admin.site
        )
        self.model_admin_instance.extra_context = self.extra_context

    @property
    def contents(self) -> str:
        return render_to_string(
            "unfold/helpers/dataset.html",
            request=self.request,
            context={
                "dataset": self,
                "cl": self.cl(),
                "opts": self.model._meta,
            },
        )

    def cl(self) -> DatasetChangeList:
        list_display = self.model_admin_instance.get_list_display(self.request)
        list_display_links = self.model_admin_instance.get_list_display_links(
            self.request, list_display
        )
        sortable_by = self.model_admin_instance.get_sortable_by(self.request)
        search_fields = self.model_admin_instance.get_search_fields(self.request)
        cl = DatasetChangeList(
            request=self.request,
            model=self.model,
            model_admin=self.model_admin_instance,
            list_display=list_display,
            list_display_links=list_display_links,
            list_filter=[],
            date_hierarchy=[],
            search_fields=search_fields,
            list_select_related=[],
            list_per_page=10,
            list_max_show_all=False,
            list_editable=[],
            sortable_by=sortable_by,
            search_help_text=[],
        )
        cl.formset = None

        return cl

    @property
    def model_name(self) -> str:
        return self.model._meta.model_name

    @property
    def model_verbose_name(self) -> str:
        return self.model._meta.verbose_name_plural
