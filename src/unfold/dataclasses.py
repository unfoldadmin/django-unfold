from dataclasses import dataclass
from typing import Dict, Optional, Union

from .typing import ActionFunction


@dataclass(frozen=True)
class UnfoldAction:
    action_name: str
    method: ActionFunction
    description: str
    path: str
    attrs: Optional[Dict] = None
    object_id: Optional[Union[int, str]] = None
