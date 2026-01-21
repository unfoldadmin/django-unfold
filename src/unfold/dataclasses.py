from collections.abc import Callable
from dataclasses import dataclass

from unfold.enums import ActionVariant
from unfold.typing import ActionFunction


@dataclass(frozen=True)
class UnfoldAction:
    action_name: str
    method: ActionFunction
    description: str
    path: str
    attrs: dict | None = None
    object_id: int | str | None = None
    icon: str | None = None
    variant: ActionVariant | None = ActionVariant.DEFAULT


@dataclass
class SearchResult:
    title: str
    description: str
    link: str
    icon: str | None


@dataclass
class Favicon:
    href: str | Callable
    rel: str | None = None
    type: str | None = None
    sizes: str | None = None


@dataclass
class DropdownItem:
    title: str
    link: str | Callable
    icon: str | None = None
    attrs: dict | None = None
