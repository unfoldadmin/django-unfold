from django.contrib import admin
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.http import HttpRequest
from unfold.decorators import action
from reversion_compare.admin import CompareMethodsMixin, BaseCompareVersionAdmin


class CompareVersionAdmin(CompareMethodsMixin, BaseCompareVersionAdmin):
    change_list_template = "admin\change_list.html"
    recover_list_template = "reversion\recover_list.html"
    recover_form_template = "reversion\recover_form.html"
    revision_form_template = "reversion\revision_form.html"
    object_history_template = "reversion-compare\object_history.html"
    compare_template = "reversion-compare\compare.html"
    compare_raw_template = "reversion-compare\compare_raw.html"

    actions_list = ["changelist_global_action_reversion_recover"]

    @action(description=_("Recover"), url_path="recover/")
    def changelist_global_action_reversion_recover(self, request: HttpRequest):
        # return redirect(self.get_urls)
        return redirect(reverse_lazy(self.recoverlist_view))
