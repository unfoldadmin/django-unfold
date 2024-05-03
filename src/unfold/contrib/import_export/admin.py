from django import forms
from django.utils.translation import gettext_lazy as _
from import_export.admin import ExportActionModelAdmin as BaseExportActionModelAdmin
from unfold.admin import ActionForm
from unfold.widgets import SELECT_CLASSES


def export_action_form_factory(formats):
    class _ExportActionForm(ActionForm):
        file_format = forms.ChoiceField(
            label=" ",
            choices=formats,
            required=False,
            widget=forms.Select(
                {"class": " ".join([*SELECT_CLASSES, "ml-3", "!w-auto", "lg:!w-40"])}
            ),
        )

    _ExportActionForm.__name__ = "ExportActionForm"

    return _ExportActionForm


class ExportActionModelAdmin(BaseExportActionModelAdmin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        choices = []
        formats = self.get_export_formats()
        if formats:
            for i, f in enumerate(formats):
                choices.append((str(i), f().get_title()))

        if len(formats) > 1:
            choices.insert(0, ("", _("Select format")))

        self.action_form = export_action_form_factory(choices)
