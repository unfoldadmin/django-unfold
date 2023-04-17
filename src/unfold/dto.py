from dataclasses import dataclass
from typing import Callable


@dataclass(frozen=True)
class UnfoldAction:
    action_name: str
    method: Callable
    description: str
    path: str
