from typing import TypedDict

from django.db.models import Model


class ConfigModelEntry(TypedDict):
    model: str
    model_class: Model
    title: str
    link: str
    active: bool
