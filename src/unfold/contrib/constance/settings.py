UNFOLD_CONSTANCE_ADDITIONAL_FIELDS = {
    str: [
        "django.forms.CharField",
        {
            "widget": "unfold.widgets.UnfoldAdminTextInputWidget",
        },
    ],
    int: [
        "django.forms.IntegerField",
        {
            "widget": "unfold.widgets.UnfoldAdminIntegerFieldWidget",
        },
    ],
    bool: [
        "django.forms.BooleanField",
        {
            "widget": "unfold.widgets.UnfoldBooleanSwitchWidget",
        },
    ],
    "file_field": [
        "django.forms.fields.FileField",
        {
            "widget": "unfold.widgets.UnfoldAdminFileFieldWidget",
        },
    ],
    "image_field": [
        "django.forms.fields.ImageField",
        {
            "widget": "unfold.widgets.UnfoldAdminImageFieldWidget",
        },
    ],
}
