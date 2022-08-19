from django.apps import AppConfig
from django.contrib import admin
from django.contrib.admin import sites

from .sites import UnfoldAdminSite


class DefaultAppConfig(AppConfig):
    name = "unfold"

    def ready(self):
        site = UnfoldAdminSite()

        admin.site = site
        sites.site = site
