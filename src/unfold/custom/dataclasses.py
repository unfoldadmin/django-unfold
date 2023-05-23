from dataclasses import dataclass

from unfold.custom.typing import ActionFunction


@dataclass(frozen=True)
class UnfoldAction:
    action_name: str
    method: ActionFunction
    description: str
    path: str
