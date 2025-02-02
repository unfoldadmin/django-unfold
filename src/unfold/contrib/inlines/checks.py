from django.contrib.admin.checks import InlineModelAdminChecks
from django.contrib.admin.options import InlineModelAdmin
from django.core.checks import CheckMessage
from django.db.models import Model


class NonrelatedModelAdminChecks(InlineModelAdminChecks):
    def _check_exclude_of_parent_model(
        self, obj: InlineModelAdmin, parent_model: Model
    ) -> list[CheckMessage]:
        return []

    def _check_relation(
        self, obj: InlineModelAdmin, parent_model: Model
    ) -> list[CheckMessage]:
        return []
