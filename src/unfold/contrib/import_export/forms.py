from django.forms.fields import BooleanField
from import_export.forms import ExportForm as BaseExportForm
from import_export.forms import ImportForm as BaseImportForm
from import_export.forms import (
    SelectableFieldsExportForm as BaseSelectableFieldsExportForm,
)

from unfold.widgets import (
    SELECT_CLASSES,
    UnfoldAdminFileFieldWidget,
    UnfoldBooleanWidget,
)


class ImportForm(BaseImportForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["resource"].widget.attrs["class"] = " ".join(
            [self.fields["resource"].widget.attrs.get("class", ""), *SELECT_CLASSES]
        )
        self.fields["import_file"].widget = UnfoldAdminFileFieldWidget(
            attrs=self.fields["import_file"].widget.attrs
        )
        self.fields["format"].widget.attrs["class"] = " ".join(
            [self.fields["format"].widget.attrs.get("class", ""), *SELECT_CLASSES]
        )


class ExportForm(BaseExportForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["resource"].widget.attrs["class"] = " ".join(
            [self.fields["resource"].widget.attrs.get("class", ""), *SELECT_CLASSES]
        )
        self.fields["format"].widget.attrs["class"] = " ".join(
            [self.fields["format"].widget.attrs.get("class", ""), *SELECT_CLASSES]
        )


class SelectableFieldsExportForm(BaseSelectableFieldsExportForm):
    def __init__(self, formats, resources, **kwargs):
        super().__init__(formats, resources, **kwargs)
        self.fields["resource"].widget.attrs["class"] = " ".join(
            [self.fields["resource"].widget.attrs.get("class", ""), *SELECT_CLASSES]
        )
        self.fields["format"].widget.attrs["class"] = " ".join(
            [self.fields["format"].widget.attrs.get("class", ""), *SELECT_CLASSES]
        )

        for _key, field in self.fields.items():
            if isinstance(field, BooleanField):
                field.widget = UnfoldBooleanWidget()
