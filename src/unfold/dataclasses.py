from dataclasses import dataclass
from typing import Callable, Optional, Union

from unfold.enums import ActionVariant

from .typing import ActionFunction


@dataclass(frozen=True)
class UnfoldAction:
    action_name: str
    method: ActionFunction
    description: str
    path: str
    attrs: Optional[dict] = None
    object_id: Optional[Union[int, str]] = None
    icon: Optional[str] = None
    variant: Optional[ActionVariant] = ActionVariant.DEFAULT


@dataclass
class Favicon:
    href: Union[str, Callable]
    rel: Optional[str] = None
    type: Optional[str] = None
    sizes: Optional[str] = None


@dataclass
class DropdownItem:
    title: str
    link: Union[str, Callable]
    icon: Optional[str] = None
