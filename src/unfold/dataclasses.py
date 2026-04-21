from collections.abc import Callable, Iterable
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, TypedDict

from unfold.enums import ActionVariant

if TYPE_CHECKING:
    from unfold.forms import BaseDialogForm


class ActionDialog(TypedDict):
    title: str
    description: str
    form_class: type["BaseDialogForm"] | None
    form_submit_text: str | None


@dataclass
class Action:
    allowed_permissions: Iterable[str]
    short_description: str
    url_path: str
    attrs: dict[str, Any]
    icon: str | None = None
    dialog: ActionDialog | None = None


@dataclass
class UnfoldAction:
    action_name: str
    method: Action
    description: str
    path: str
    attrs: dict | None = None
    object_id: int | str | None = None
    icon: str | None = None
    variant: ActionVariant | None = ActionVariant.DEFAULT
    dialog: ActionDialog | None = None


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
