from import_export.forms import ImportExportFormBase as BaseImportExportFormBase
from unfold.widgets import SELECT_CLASSES, UnfoldAdminFileFieldWidget


class ImportForm(BaseImportExportFormBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["resource"].widget = UnfoldAdminFileFieldWidget()
        self.fields["format"].widget.attrs["class"] = " ".join(SELECT_CLASSES)


class ExportForm(BaseImportExportFormBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["format"].widget.attrs["class"] = " ".join(SELECT_CLASSES)
