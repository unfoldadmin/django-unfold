from django.template import Context, Template
from django.test import RequestFactory, override_settings
from django.test.html import parse_html

from unfold.settings import CONFIG_DEFAULTS


@override_settings(UNFOLD={**CONFIG_DEFAULTS})
def test_preserve_filters():
    factory = RequestFactory()
    request = factory.post(
        "/example-url/",
        {
            "csrfmiddlewaretoken": "dummy_csrf_token",
            "filter": "name",
            "custom_param": "value",
        },
    )
    request.GET = {
        "sort": "asc",
        "page": "2",
        "date__year": "2024",  # Simulate a date-hierarchy filter
        "date__month": "11",
    }

    # Create a context with the request
    context = Context({"request": request})

    # Template with the custom tag
    template = Template("{% load unfold %}{% preserve_filters %}")

    # Render the template
    output_html = template.render(context)

    # Expected HTML output
    expected_html = (
        '<input name="sort" type="hidden" value="asc">'
        '<input name="page" type="hidden" value="2">'
        '<input name="date__year" type="hidden" value="2024">'
        '<input name="date__month" type="hidden" value="11">'
        '<input name="filter" type="hidden" value="name">'
        '<input name="custom_param" type="hidden" value="value">'
    )

    # Assert the output matches the expected HTML
    assert parse_html(output_html) == parse_html(
        expected_html
    ), f"Expected: {expected_html}, got: {output_html}"
