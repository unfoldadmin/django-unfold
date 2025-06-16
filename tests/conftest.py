from pytest_factoryboy import register

from .factories import TagFactory
from .fixtures import *  # noqa: F403

register(TagFactory)
