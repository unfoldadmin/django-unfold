from pytest_factoryboy import register

from .factories import ProjectFactory, TagFactory, TaskFactory, UserFactory
from .fixtures import *  # noqa: F403

register(TagFactory)
register(UserFactory)
register(ProjectFactory)
register(TaskFactory)
