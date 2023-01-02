from django.forms import Widget


class WysiwygWidget(Widget):
    template_name = "unfold/forms/wysiwyg.html"

    class Media:
        css = {"all": ("unfold/forms/css/trix.css",)}
        js = (
            "unfold/forms/js/trix.js",
            "unfold/forms/js/trix.config.js",
        )
