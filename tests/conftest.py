from pytest_factoryboy import register

from .factories import (
    CategoryFactory,
    InvoiceFactory,
    InvoiceItemFactory,
    LabelFactory,
    ProjectFactory,
    TagFactory,
    TaskFactory,
    UserFactory,
)
from .fixtures import *  # noqa: F403

register(TagFactory)
register(UserFactory)
register(ProjectFactory)
register(TaskFactory)
register(LabelFactory)
register(CategoryFactory)
register(InvoiceFactory)
register(InvoiceItemFactory)
