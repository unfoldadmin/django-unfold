from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Type
from django.template.loader import render_to_string

component_registry: Dict[str, Type["Component"]] = {}


def register(cls: Type["Component"]) -> Type["Component"]:
    component_registry[cls().template] = cls
    return cls


@dataclass
class Component:
    children: str = ""
    class_: Optional[str] = None

    def render(self) -> str:
        return render_to_string(self.template, self.get_context_data())

    def get_context_data(self):
        context = {
            "component": self,
            "class": self.class_
        }
        return context

    @property
    def template(self) -> str:
        raise NotImplementedError


@register
@dataclass
class Card(Component):
    title: str = ""
    subtitle: str = ""
    icon: Optional[str] = None
    label: Optional[str] = None
    footer: Optional[str] = None
    href: Optional[str] = None

    @property
    def template(self) -> str:
        return "unfold/components/card.html"


@register
@dataclass
class Container(Component):
    @property
    def template(self) -> str:
        return "unfold/components/container.html"


@register
@dataclass
class Flex(Component):
    col: bool = False

    @property
    def template(self) -> str:
        return "unfold/components/flex.html"


@register
@dataclass
class Button(Component):
    href: Optional[str] = None
    submit: bool = False
    variant: str = "default"
    attrs: Dict[str, Any] = field(default_factory=dict)

    @property
    def template(self) -> str:
        return "unfold/components/button.html"


@register
@dataclass
class Table(Component):
    card_included: bool = False
    striped: bool = False
    table: Dict[str, Any] = field(default_factory=dict)

    @property
    def template(self) -> str:
        return "unfold/components/table.html"
