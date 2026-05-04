from django.views.generic import TemplateView

from unfold.views import UnfoldModelAdminViewMixin, UnfoldSiteViewMixin


class SiteExtraUrlView(UnfoldSiteViewMixin, TemplateView):
    title = "Site Extra URL"
    template_name = "site_extra_view.html"
    permission_required = (
        "example.view_user",
        "example.add_project",
    )


class ModelExtraUrlView(UnfoldModelAdminViewMixin, TemplateView):
    title = "Model Extra URL"
    template_name = "model_extra_view.html"
    permission_required = (
        "example.view_project",
        "example.add_project",
    )
