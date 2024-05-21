from import_export.forms import ExportForm as ExportFormBase
from import_export.forms import ImportForm as ImportFormBase
from unfold.widgets import UnfoldAdminFileFieldWidget, UnfoldAdminSelectWidget


class ImportForm(ImportFormBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        resource_widget = self.fields["resource"].widget
        if len(resource_widget.choices) > 0:
            self.fields["resource"].widget = UnfoldAdminSelectWidget(
                attrs=resource_widget.attrs, choices=resource_widget.choices
            )
        else:
            self.fields.pop("resource")
        self.fields["import_file"].widget = UnfoldAdminFileFieldWidget()
        format_widget = self.fields["format"].widget
        self.fields["format"].widget = UnfoldAdminSelectWidget(
            attrs=format_widget.attrs, choices=format_widget.choices
        )


class ExportForm(ExportFormBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        format_widget = self.fields["format"].widget
        self.fields["format"].widget = UnfoldAdminSelectWidget(
            attrs=format_widget.attrs, choices=format_widget.choices
        )
