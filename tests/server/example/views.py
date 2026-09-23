from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import FormView, TemplateView

from example.forms import CrispyForm
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


class CrispyFormView(UnfoldModelAdminViewMixin, FormView):
    title = _("Crispy form")
    success_url = reverse_lazy("admin:crispy_form")
    permission_required = ("example.view_project",)
    template_name = "crispy_form.html"
    form_class = CrispyForm
