UNFOLD_CONSTANCE_ADDITIONAL_FIELDS = {
    str: [
        "django.forms.CharField",
        {
            "widget": "unfold.widgets.UnfoldAdminTextInputWidget",
            "required": False,
        },
    ],
    int: [
        "django.forms.IntegerField",
        {
            "widget": "unfold.widgets.UnfoldAdminIntegerFieldWidget",
        },
    ],
    float: [
        "django.forms.FloatField",
        {
            "widget": "unfold.widgets.UnfoldAdminDecimalFieldWidget",
        },
    ],
    bool: [
        "django.forms.BooleanField",
        {
            "widget": "unfold.widgets.UnfoldBooleanSwitchWidget",
            "required": False,
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
