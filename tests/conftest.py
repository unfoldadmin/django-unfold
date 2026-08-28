from pytest_factoryboy import register

from .factories import (
    CategoryFactory,
    InvoiceFactory,
    InvoiceItemFactory,
    InvoiceItemPartFactory,
    InvoiceItemPartNoteFactory,
    LabelFactory,
    ProfileFactory,
    ProjectFactory,
    TagFactory,
    TagNoteFactory,
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
register(InvoiceItemPartFactory)
register(InvoiceItemPartNoteFactory)
register(TagNoteFactory)
register(ProfileFactory)
