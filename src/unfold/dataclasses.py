from dataclasses import dataclass
from typing import Dict, Optional

from .typing import ActionFunction


@dataclass(frozen=True)
class UnfoldAction:
    action_name: str
    method: ActionFunction
    description: str
    path: str
    attrs: Optional[Dict] = None
