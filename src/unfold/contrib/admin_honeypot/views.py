from admin_honeypot.views import AdminHoneypot as BaseAdminHoneypotView
from django.urls import reverse
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.utils.translation import gettext as _

from unfold.sites import UnfoldAdminSite

from .forms import HoneypotLoginForm

def get_unfold_context(request):
    """Get unfold admin context without inheriting from UnfoldAdminSite"""
    unfold_site = UnfoldAdminSite()
    return unfold_site.each_context(request)

class AdminHoneypot(BaseAdminHoneypotView):
    template_name = 'admin_honeypot/login.html'
    form_class = HoneypotLoginForm
        
    def get_context_data(self, **kwargs):
        context = super(AdminHoneypot, self).get_context_data(**kwargs)
        path = self.request.get_full_path()
        unfold_context = get_unfold_context(self.request)

        context.update({
            'app_path': path,
            REDIRECT_FIELD_NAME: reverse('unfold.contrib.admin_honeypot:index'),
            'title': _('Log in'),
            'colors': unfold_context.get('colors'),
        })
        return context
    
    def get_form(self, form_class=form_class):
        return form_class(self.request, **self.get_form_kwargs())
