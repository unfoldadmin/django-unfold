from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import FormView

from example.forms import CrispyForm
from unfold.views import UnfoldModelAdminViewMixin


class CrispyFormView(UnfoldModelAdminViewMixin, FormView):
    title = _("Crispy form")
    success_url = reverse_lazy("admin:crispy_form")
    permission_required = ("example.view_project",)
    template_name = "crispy_form.html"
    form_class = CrispyForm
