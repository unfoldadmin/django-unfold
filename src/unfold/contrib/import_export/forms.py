from django.forms import Form, HiddenInput
from django.forms.fields import BooleanField
from django.utils.translation import gettext_lazy as _
from import_export.forms import ExportForm as BaseExportForm
from import_export.forms import ImportForm as BaseImportForm
from import_export.forms import (
    SelectableFieldsExportForm as BaseSelectableFieldsExportForm,
)

from unfold.widgets import (
    UnfoldAdminFileFieldWidget,
    UnfoldAdminSelectWidget,
    UnfoldBooleanWidget,
)


class ImportExportWidgetsMixin(Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if not isinstance(self.fields["resource"].widget, HiddenInput):
            self.fields["resource"].widget = UnfoldAdminSelectWidget(
                choices=self.fields["resource"].choices  # ty:ignore[unresolved-attribute]
            )

        format_choices = self.fields["format"].choices  # ty:ignore[unresolved-attribute]

        # Provide better label for default choice
        if len(format_choices) > 1 and format_choices[0][1] == "---":
            format_choices[0] = ("", _("Select format"))

        self.fields["format"].widget = UnfoldAdminSelectWidget(
            choices=format_choices,
            attrs={
                "class": self.fields["format"].widget.attrs.get("class", ""),
                "readonly": True if len(format_choices) == 1 else False,
            },
        )


class ImportForm(ImportExportWidgetsMixin, BaseImportForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["import_file"].widget = UnfoldAdminFileFieldWidget(
            attrs=self.fields["import_file"].widget.attrs
        )


class ExportForm(ImportExportWidgetsMixin, BaseExportForm):
    pass


class SelectableFieldsExportForm(
    ImportExportWidgetsMixin, BaseSelectableFieldsExportForm
):
    def __init__(self, formats, resources, **kwargs):
        super().__init__(formats, resources, **kwargs)

        for _key, field in self.fields.items():
            if isinstance(field, BooleanField):
                field.widget = UnfoldBooleanWidget()
