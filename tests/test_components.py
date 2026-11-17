import pytest
from django.http import HttpRequest
from django.test import RequestFactory

from unfold.components import BaseComponent, ComponentRegistry, register_component


class DummyComponent(BaseComponent):
    def __init__(self, request, foo=None):
        super().__init__(request)
        self.foo = foo

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["foo"] = self.foo
        return ctx


def test_components_base_component_context():
    component = BaseComponent(RequestFactory().get("/"))
    result = component.get_context_data(test=1)

    assert result == {
        "test": 1,
    }


def test_components_register_and_get_class():
    class AnotherDummyComponent(BaseComponent):
        pass

    ComponentRegistry.register_class(AnotherDummyComponent)
    fetched = ComponentRegistry.get_class("AnotherDummyComponent")
    assert fetched is AnotherDummyComponent


def test_components_register_component_decorator():
    @register_component
    class DecoratedComponent(BaseComponent):
        pass

    found = ComponentRegistry.get_class("DecoratedComponent")
    assert found is not None
    assert issubclass(found, BaseComponent)


def test_components_create_instance_success():
    class MyComponent(BaseComponent):
        def __init__(self, request, hello=None):
            super().__init__(request)
            self.hello = hello

    ComponentRegistry.register_class(MyComponent)
    request = RequestFactory().get("/")

    instance = ComponentRegistry.create_instance(
        "MyComponent", request=request, hello="hi"
    )
    assert isinstance(instance, MyComponent)
    assert instance.hello == "hi"
    assert instance.request is request


def test_components_create_instance_not_registered():
    with pytest.raises(ValueError) as exc:
        ComponentRegistry.create_instance("UnknownComponent", request=HttpRequest())

    assert "is not registered" in str(exc.value)


def test_components_register_class_must_subclass_basecomponent():
    class NotAComponent:
        pass

    with pytest.raises(ValueError) as exc:
        ComponentRegistry.register_class(NotAComponent)

    assert "must inherit from BaseComponent" in str(exc.value)


def test_components_register_class_duplicate():
    class RepeatedComponent(BaseComponent):
        pass

    ComponentRegistry.register_class(RepeatedComponent)
    with pytest.raises(ValueError) as exc:
        ComponentRegistry.register_class(RepeatedComponent)

    assert "is already registered" in str(exc.value)
