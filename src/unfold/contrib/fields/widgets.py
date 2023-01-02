from django.forms import Widget


class WysiwygWidget(Widget):
    template_name = "unfold/fields/wysiwyg.html"

    class Media:
        css = {"all": ("unfold/fields/css/trix.css",)}
        js = (
            "unfold/fields/js/trix.js",
            "unfold/fields/js/trix.config.js",
        )
