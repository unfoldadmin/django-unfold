from typing import Any

from django.http import HttpRequest


class ComponentRegistry:
    _registry: dict[str, type] = {}

    @classmethod
    def register_class(cls, component_cls: type) -> None:
        if not issubclass(component_cls, BaseComponent):
            raise ValueError(
                f"Class '{component_cls.__name__}' must inherit from BaseComponent."
            )

        class_name = component_cls.__name__

        if class_name in cls._registry:
            raise ValueError(f"Class '{class_name}' is already registered.")

        cls._registry[class_name] = component_cls

    @classmethod
    def get_class(cls, class_name: str) -> type | None:
        return cls._registry.get(class_name)

    @classmethod
    def create_instance(cls, class_name: str, **kwargs: Any) -> Any:
        component_cls = cls.get_class(class_name)

        if component_cls is None:
            raise ValueError(f"Class '{class_name}' is not registered.")

        return component_cls(**kwargs)


def register_component(cls: type) -> type:
    ComponentRegistry.register_class(cls)
    return cls


class BaseComponent:
    def __init__(self, request: HttpRequest):
        self.request = request

    def get_context_data(self, **kwargs):
        return kwargs
