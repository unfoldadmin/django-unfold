from pytest_factoryboy import register

from .factories import TagFactory, UserFactory
from .fixtures import *  # noqa: F403

register(TagFactory)
register(UserFactory)
