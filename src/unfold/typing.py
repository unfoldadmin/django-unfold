from typing import Any, Dict, Iterable, List, Protocol, Tuple, Union


class ActionFunction(Protocol):
    """
    Type that specifies functions that are used as actions (annotated with @actions decorator)
    These are functions (__call__) and have 4 additional attributes
    (allowed_permissions, short_description, url_path and attrs)
    """

    allowed_permissions: Iterable[str]
    short_description: str
    url_path: str
    attrs: Dict[str, Any]

    def __call__(self, *args, **kwargs):
        pass


FieldsetsType = List[Tuple[Union[str, None], Dict[str, Any]]]
