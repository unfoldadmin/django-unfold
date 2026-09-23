from typing import Any

from django.http import HttpRequest
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _


def tabs_callback(request: HttpRequest) -> list[dict[str, Any]]:
    return [
        {
            "page": "users",
            "models": [
                {
                    "name": "example.user",
                },
            ],
            "items": [
                {
                    "title": _("Users"),
                    "link": reverse_lazy("admin:example_user_changelist"),
                },
                {
                    "title": _("Crispy form"),
                    "link": reverse_lazy("admin:crispy_form"),
                },
            ],
        }
    ]
