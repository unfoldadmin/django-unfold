from collections.abc import Iterable
from typing import Any, Protocol


class ActionFunction(Protocol):
    """
    Type that specifies functions that are used as actions (annotated with @actions decorator)
    These are functions (__call__) and have 4 additional attributes
    (allowed_permissions, short_description, url_path and attrs)
    """

    allowed_permissions: Iterable[str]
    short_description: str
    url_path: str
    attrs: dict[str, Any]
    icon: str | None = None

    def __call__(self, *args, **kwargs):
        pass


FieldsetsType = (
    list[tuple[str | None, dict[str, Any]]] | tuple[tuple[str | None, dict[str, Any]]]
)
