from django.contrib.auth.mixins import PermissionRequiredMixin

from .exceptions import UnfoldException


class UnfoldModelAdminViewMixin(PermissionRequiredMixin):
    """
    Prepares views to be displayed in admin
    """

    def get_context_data(self, **kwargs):
        if "model_admin" not in self.kwargs:
            raise UnfoldException(
                "UnfoldModelAdminViewMixin was not provided with 'model_admin' argument"
            )
        model_admin = self.kwargs["model_admin"]
        context_data = super().get_context_data(
            **kwargs, **model_admin.admin_site.each_context(self.request)
        )
        return context_data
