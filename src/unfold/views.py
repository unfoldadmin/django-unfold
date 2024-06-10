from typing import Any, Dict

from django.contrib.auth.mixins import PermissionRequiredMixin

from .exceptions import UnfoldException


class UnfoldModelAdminViewMixin(PermissionRequiredMixin):
    """
    Prepares views to be displayed in admin
    """

    model_admin = None

    def __init__(self, model_admin, **kwargs):
        self.model_admin = model_admin
        super().__init__(**kwargs)

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
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
