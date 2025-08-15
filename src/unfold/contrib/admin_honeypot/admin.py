from admin_honeypot.admin import LoginAttemptAdmin as BaseLoginAttemptAdmin
from admin_honeypot.models import LoginAttempt
from django.contrib import admin

from unfold.admin import ModelAdmin

if admin.site.is_registered(LoginAttempt):
    admin.site.unregister(LoginAttempt)


class LoginAttemptAdmin(ModelAdmin, BaseLoginAttemptAdmin):
    def __init__(self, model, admin_site):
        super().__init__(model, admin_site)


admin.site.register(LoginAttempt, LoginAttemptAdmin)
