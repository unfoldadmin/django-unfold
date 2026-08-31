import re
from http import HTTPStatus

import pytest
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.core.exceptions import ImproperlyConfigured
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from example.admin import UserAdmin, UserTagInline
from example.models import (
    Category,
    Invoice,
    InvoiceItem,
    InvoiceItemPart,
    InvoiceItemPartNote,
    Post,
    TagNote,
    TagUserNote,
)

from unfold.admin import TabularInline
from unfold.mixins.nested_inlines_model_admin import iter_nested_formsets

from .factories import TagFactory

User = get_user_model()

USER_DATA = {
    "is_active": True,
    "is_staff": True,
    "is_superuser": True,
    "username": "admin@example.com",
    "email": "admin@example.com",
    "date_joined_0": "2026-01-01",
    "date_joined_1": "00:00:00",
    "User_tags-TOTAL_FORMS": "0",
    "User_tags-INITIAL_FORMS": "0",
}

# Management data of the third level formset rendered below the first
# invoiceitem_set form.
INVOICE_ITEM_PART_DATA = {
    "invoice_set-0-invoiceitem_set-0-invoiceitempart_set-TOTAL_FORMS": "0",
    "invoice_set-0-invoiceitem_set-0-invoiceitempart_set-INITIAL_FORMS": "0",
}


@pytest.mark.django_db
def test_inline_pagination(client, admin_user):
    tags_count = 50
    client.force_login(admin_user)

    for i in range(tags_count):
        tag = TagFactory(name=f"Tag {i}")
        admin_user.tags.add(tag)

    response = client.get(reverse("admin:example_user_change", args=(admin_user.pk,)))

    assert response.status_code == HTTPStatus.OK
    assert f"{tags_count} user-tag relationships" in response.content.decode()


@pytest.mark.django_db
def test_inline_pagination_no_relationships(client, admin_user):
    client.force_login(admin_user)
    response = client.get(reverse("admin:example_user_change", args=(admin_user.pk,)))
    assert response.status_code == HTTPStatus.OK

    assert "user-tag" not in response.content.decode()


@pytest.mark.django_db
def test_inline_pagination_one_relationship(client, admin_user):
    tag = TagFactory(name="Tag 1")
    admin_user.tags.add(tag)
    client.force_login(admin_user)

    response = client.get(reverse("admin:example_user_change", args=(admin_user.pk,)))
    assert response.status_code == HTTPStatus.OK
    assert "user-tag" not in response.content.decode()


@pytest.mark.django_db
def test_inline_collapsible(client, admin_user):
    tag = TagFactory(name="Tag 1")
    admin_user.tags.add(tag)
    client.force_login(admin_user)

    response = client.get(reverse("admin:example_user_change", args=(admin_user.pk,)))
    assert response.status_code == HTTPStatus.OK
    assert (
        "x-on:click=\"['h3', 'strong'].includes($event.target.tagName.toLowerCase()) && (openRow = !openRow)\""
        in response.content.decode()
    )


@pytest.mark.django_db(transaction=True)
def test_nested_inline_create_parent_object(client, admin_user):
    client.force_login(admin_user)

    data = {
        **USER_DATA,
        "invoice_set-TOTAL_FORMS": "1",
        "invoice_set-INITIAL_FORMS": "0",
        "invoice_set-0-name": "Test Invoice",
        "invoice_set-0-invoiceitem_set-TOTAL_FORMS": "0",
        "invoice_set-0-invoiceitem_set-INITIAL_FORMS": "0",
    }

    client.post(
        reverse("admin:example_user_change", args=(admin_user.pk,)),
        data=data,
        follow=True,
    )

    assert Invoice.objects.count() == 1
    assert Invoice.objects.first().name == "Test Invoice"
    assert Invoice.objects.first().user == admin_user


@pytest.mark.django_db
def test_nested_inline_create_nested_object(client, admin_user):
    client.force_login(admin_user)

    data = {
        **USER_DATA,
        "invoice_set-TOTAL_FORMS": "1",
        "invoice_set-INITIAL_FORMS": "0",
        "invoice_set-0-name": "Test Invoice",
        "invoice_set-0-invoiceitem_set-TOTAL_FORMS": "1",
        "invoice_set-0-invoiceitem_set-INITIAL_FORMS": "0",
        "invoice_set-0-invoiceitem_set-0-name": "Test Invoice Item",
        **INVOICE_ITEM_PART_DATA,
    }
    client.post(reverse("admin:example_user_change", args=(admin_user.pk,)), data=data)

    assert Invoice.objects.count() == 1
    assert Invoice.objects.first().name == "Test Invoice"
    assert Invoice.objects.first().user == admin_user
    assert InvoiceItem.objects.count() == 1
    assert InvoiceItem.objects.first().name == "Test Invoice Item"
    assert InvoiceItem.objects.first().invoice == Invoice.objects.first()


@pytest.mark.django_db
def test_nested_inline_validate_nested_object(
    client, admin_user, invoice_factory, invoice_item_factory
):
    client.force_login(admin_user)

    invoice = invoice_factory(user=admin_user, name="Test Invoice")
    invoice_item = invoice_item_factory(invoice=invoice, name="Test Invoice Item")

    data = {
        **USER_DATA,
        "_continue": "1",
        "invoice_set-TOTAL_FORMS": "1",
        "invoice_set-INITIAL_FORMS": "0",
        "invoice_set-0-name": invoice.name,
        "invoice_set-0-id": invoice.pk,
        "invoice_set-0-invoiceitem_set-TOTAL_FORMS": "1",
        "invoice_set-0-invoiceitem_set-INITIAL_FORMS": "0",
        "invoice_set-0-invoiceitem_set-0-name": "",
        "invoice_set-0-invoiceitem_set-0-id": invoice_item.pk,
    }

    response = client.post(
        reverse("admin:example_user_change", args=(admin_user.pk,)),
        data=data,
        follow=True,
    )
    assert InvoiceItem.objects.count() == 1
    assert InvoiceItem.objects.first().name == "Test Invoice Item"
    assert "This field is required." in response.content.decode()


@pytest.mark.django_db
def test_nested_inline_delete_parent_object(
    client, admin_user, invoice_factory, invoice_item_factory
):
    client.force_login(admin_user)
    invoice = invoice_factory(user=admin_user, name="Test Invoice")
    invoice_item = invoice_item_factory(invoice=invoice, name="Test Invoice Item")

    response = client.get(reverse("admin:example_user_change", args=(admin_user.pk,)))
    assert response.status_code == HTTPStatus.OK
    assert "Test Invoice" in response.content.decode()
    assert "Test Invoice Item" in response.content.decode()
    assert Invoice.objects.count() == 1
    assert InvoiceItem.objects.count() == 1

    data = {
        **USER_DATA,
        "_continue": "1",
        "invoice_set-TOTAL_FORMS": "1",
        "invoice_set-INITIAL_FORMS": "1",
        "invoice_set-0-name": "Test Invoice",
        "invoice_set-0-DELETE": True,
        "invoice_set-0-id": invoice.pk,
        "invoice_set-0-user": admin_user.pk,
        "invoice_set-0-invoiceitem_set-TOTAL_FORMS": "1",
        "invoice_set-0-invoiceitem_set-INITIAL_FORMS": "1",
        **INVOICE_ITEM_PART_DATA,
        "invoice_set-0-invoiceitem_set-0-name": "Test Invoice",
        "invoice_set-0-invoiceitem_set-0-id": invoice_item.pk,
        "invoice_set-0-invoiceitem_set-0-invoice": invoice.pk,
    }

    response = client.post(
        reverse("admin:example_user_change", args=(admin_user.pk,)),
        data=data,
        follow=True,
    )

    assert "Test Invoice" not in response.content.decode()
    assert Invoice.objects.count() == 0
    assert InvoiceItem.objects.count() == 0


@pytest.mark.django_db
def test_nested_inline_delete_nested_object(
    client, admin_user, invoice_factory, invoice_item_factory
):
    client.force_login(admin_user)
    invoice = invoice_factory(user=admin_user, name="Test Invoice")
    invoice_item = invoice_item_factory(invoice=invoice, name="Test Invoice Item")

    response = client.get(reverse("admin:example_user_change", args=(admin_user.pk,)))
    assert response.status_code == HTTPStatus.OK
    assert "Test Invoice" in response.content.decode()
    assert "Test Invoice Item" in response.content.decode()
    assert Invoice.objects.count() == 1
    assert InvoiceItem.objects.count() == 1

    data = {
        **USER_DATA,
        "_continue": "1",
        "invoice_set-TOTAL_FORMS": "1",
        "invoice_set-INITIAL_FORMS": "1",
        "invoice_set-0-name": "Test Invoice",
        "invoice_set-0-id": invoice.pk,
        "invoice_set-0-user": admin_user.pk,
        "invoice_set-0-invoiceitem_set-TOTAL_FORMS": "1",
        "invoice_set-0-invoiceitem_set-INITIAL_FORMS": "1",
        **INVOICE_ITEM_PART_DATA,
        "invoice_set-0-invoiceitem-name": "Test Invoice",
        "invoice_set-0-invoiceitem_set-0-DELETE": True,
        "invoice_set-0-invoiceitem_set-0-id": invoice_item.pk,
        "invoice_set-0-invoiceitem_set-0-invoice": invoice.pk,
    }

    response = client.post(
        reverse("admin:example_user_change", args=(admin_user.pk,)),
        data=data,
        follow=True,
    )
    assert "Test Invoice" in response.content.decode()
    assert "Test Invoice Item" not in response.content.decode()
    assert Invoice.objects.count() == 1
    assert InvoiceItem.objects.count() == 0


@pytest.mark.django_db
@pytest.mark.parametrize(
    "permissions, delete_invoice, delete_invoiceitem, invoice_count, invoiceitem_count",
    [
        [[], True, True, 1, 1],
        [["delete_invoice"], True, True, 1, 1],
        [["view_invoice", "delete_invoice"], True, False, 0, 0],
        [["view_invoice", "delete_invoice"], False, True, 1, 1],
        [["view_invoice", "delete_invoice", "delete_invoiceitem"], False, True, 1, 1],
        [
            [
                "view_invoice",
                "delete_invoice",
                "view_invoiceitem",
                "delete_invoiceitem",
            ],
            False,
            True,
            1,
            0,
        ],
    ],
)
def test_nested_inlines_delete(
    permissions,
    delete_invoice,
    delete_invoiceitem,
    invoice_count,
    invoiceitem_count,
    client,
    staff_user,
    invoice_factory,
    invoice_item_factory,
):
    client.force_login(staff_user)
    invoice = invoice_factory(user=staff_user, name="Test Invoice")
    invoice_item = invoice_item_factory(invoice=invoice, name="Test Invoice Item")

    for permission in permissions:
        staff_user.user_permissions.add(Permission.objects.get(codename=permission))

    assert Invoice.objects.count() == 1
    assert InvoiceItem.objects.count() == 1

    data = {
        **USER_DATA,
        "_continue": "1",
        "invoice_set-TOTAL_FORMS": "1",
        "invoice_set-INITIAL_FORMS": "1",
        "invoice_set-0-name": "Test Invoice",
        "invoice_set-0-id": invoice.pk,
        "invoice_set-0-user": staff_user.pk,
        "invoice_set-0-DELETE": delete_invoice,
        "invoice_set-0-invoiceitem_set-TOTAL_FORMS": "1",
        "invoice_set-0-invoiceitem_set-INITIAL_FORMS": "1",
        **INVOICE_ITEM_PART_DATA,
        "invoice_set-0-invoiceitem_set-0-name": "Invoice Item Value",
        "invoice_set-0-invoiceitem_set-0-id": invoice_item.pk,
        "invoice_set-0-invoiceitem_set-0-invoice": invoice.pk,
        "invoice_set-0-invoiceitem_set-0-DELETE": delete_invoiceitem,
    }

    client.post(
        reverse("admin:example_user_change", args=(staff_user.pk,)),
        data=data,
        follow=True,
    )

    assert Invoice.objects.count() == invoice_count
    assert InvoiceItem.objects.count() == invoiceitem_count


@pytest.mark.django_db
def test_nested_inline_permissions(
    client, staff_user, invoice_factory, invoice_item_factory
):
    client.force_login(staff_user)
    invoice = invoice_factory(user=staff_user, name="Test Invoice")
    invoice_item_factory(invoice=invoice, name="Test Invoice Item")

    response = client.get(reverse("admin:example_user_change", args=(staff_user.pk,)))
    assert "Test Invoice" not in response.content.decode()
    assert "Test Invoice Item" not in response.content.decode()
    assert "invoice_set-0-DELETE" not in response.content.decode()
    assert "<span>Add another Invoice</span>" not in response.content.decode()

    staff_user.user_permissions.add(Permission.objects.get(codename="change_invoice"))
    response = client.get(reverse("admin:example_user_change", args=(staff_user.pk,)))
    assert "Test Invoice" in response.content.decode()
    assert "Test Invoice Item" not in response.content.decode()
    assert "invoice_set-0-DELETE" not in response.content.decode()
    assert "<span>Add another Invoice</span>" not in response.content.decode()

    staff_user.user_permissions.add(Permission.objects.get(codename="delete_invoice"))
    response = client.get(reverse("admin:example_user_change", args=(staff_user.pk,)))
    assert "Test Invoice" in response.content.decode()
    assert "Test Invoice Item" not in response.content.decode()
    assert "invoice_set-0-DELETE" in response.content.decode()
    assert "<span>Add another Invoice</span>" not in response.content.decode()

    staff_user.user_permissions.add(Permission.objects.get(codename="add_invoice"))
    response = client.get(reverse("admin:example_user_change", args=(staff_user.pk,)))
    assert "Test Invoice" in response.content.decode()
    assert "Test Invoice Item" not in response.content.decode()
    assert "invoice_set-0-DELETE" in response.content.decode()
    assert "<span>Add another Invoice</span>" in response.content.decode()

    staff_user.user_permissions.add(Permission.objects.get(codename="view_invoiceitem"))
    response = client.get(reverse("admin:example_user_change", args=(staff_user.pk,)))
    assert "Test Invoice Item" in response.content.decode()
    assert "invoice_set-0-invoiceitem_set-0-DELETE" not in response.content.decode()
    assert "<span>Add another Invoice item</span>" not in response.content.decode()

    staff_user.user_permissions.add(Permission.objects.get(codename="add_invoiceitem"))
    response = client.get(reverse("admin:example_user_change", args=(staff_user.pk,)))
    assert "Test Invoice Item" in response.content.decode()
    assert "invoice_set-0-invoiceitem_set-0-DELETE" not in response.content.decode()
    assert "<span>Add another Invoice item</span>" in response.content.decode()

    staff_user.user_permissions.add(
        Permission.objects.get(codename="delete_invoiceitem")
    )
    response = client.get(reverse("admin:example_user_change", args=(staff_user.pk,)))
    assert "Test Invoice Item" in response.content.decode()
    assert "invoice_set-0-invoiceitem_set-0-DELETE" in response.content.decode()
    assert "<span>Add another Invoice item</span>" in response.content.decode()


@pytest.mark.django_db
def test_nested_inline_change_invoiceitem_value(
    client, admin_user, invoice_factory, invoice_item_factory
):
    client.force_login(admin_user)
    invoice = invoice_factory(user=admin_user, name="Test Invoice")
    invoice_item = invoice_item_factory(invoice=invoice, name="Test Invoice Item")

    response = client.get(reverse("admin:example_user_change", args=(admin_user.pk,)))
    assert response.status_code == HTTPStatus.OK
    assert "Test Invoice Item" in response.content.decode()

    data = {
        **USER_DATA,
        "_continue": "1",
        "invoice_set-TOTAL_FORMS": "1",
        "invoice_set-INITIAL_FORMS": "1",
        "invoice_set-0-name": "Test Invoice",
        "invoice_set-0-id": invoice.pk,
        "invoice_set-0-user": admin_user.pk,
        "invoice_set-0-invoiceitem_set-TOTAL_FORMS": "1",
        "invoice_set-0-invoiceitem_set-INITIAL_FORMS": "1",
        **INVOICE_ITEM_PART_DATA,
        "invoice_set-0-invoiceitem_set-0-name": "Test Invoice Item2",
        "invoice_set-0-invoiceitem_set-0-id": invoice_item.pk,
        "invoice_set-0-invoiceitem_set-0-invoice": invoice.pk,
    }

    response = client.post(
        reverse("admin:example_user_change", args=(admin_user.pk,)),
        data=data,
        follow=True,
    )
    assert response.status_code == HTTPStatus.OK
    assert "Test Invoice Item2" in response.content.decode()
    invoice_item.refresh_from_db()
    assert invoice_item.name == "Test Invoice Item2"


@pytest.mark.django_db
@pytest.mark.parametrize(
    "permissions, result",
    [
        [[], "Test Invoice Item"],
        [["change_invoice"], "Test Invoice Item"],
        [["change_invoiceitem"], "Test Invoice Item"],
        [["change_invoice"], "Test Invoice Item"],
        [["change_invoice", "add_invoiceitem"], "Test Invoice Item"],
        [["change_invoice", "change_invoiceitem"], "Updated Invoice Item Value"],
    ],
)
def test_nested_inline_permissions_change(
    permissions, result, client, staff_user, invoice_factory, invoice_item_factory
):
    client.force_login(staff_user)
    invoice = invoice_factory(user=staff_user, name="Test Invoice")
    invoice_item = invoice_item_factory(invoice=invoice, name="Test Invoice Item")

    for permission in permissions:
        staff_user.user_permissions.add(Permission.objects.get(codename=permission))

    data = {
        **USER_DATA,
        "_continue": "1",
        "invoice_set-TOTAL_FORMS": "1",
        "invoice_set-INITIAL_FORMS": "1",
        "invoice_set-0-name": "Test Invoice",
        "invoice_set-0-id": invoice.pk,
        "invoice_set-0-user": staff_user.pk,
        "invoice_set-0-invoiceitem_set-TOTAL_FORMS": "1",
        "invoice_set-0-invoiceitem_set-INITIAL_FORMS": "1",
        **INVOICE_ITEM_PART_DATA,
        "invoice_set-0-invoiceitem_set-0-name": "Updated Invoice Item Value",
        "invoice_set-0-invoiceitem_set-0-id": invoice_item.pk,
        "invoice_set-0-invoiceitem_set-0-invoice": invoice.pk,
    }

    client.post(
        reverse("admin:example_user_change", args=(staff_user.pk,)),
        data=data,
        follow=True,
    )

    invoice_item.refresh_from_db()
    assert invoice_item.name == result


@pytest.mark.django_db
@pytest.mark.parametrize(
    "permissions,result",
    [
        [[], 0],
        [["change_invoice"], 0],
        [["add_invoiceitem"], 0],
        [["change_invoiceitem"], 0],
        [["change_invoice", "change_invoiceitem"], 0],
        [["change_invoice", "add_invoiceitem"], 1],
    ],
)
def test_nested_inline_add(permissions, result, client, staff_user, invoice_factory):
    client.force_login(staff_user)
    invoice = invoice_factory(user=staff_user, name="Test Invoice")

    for permission in permissions:
        staff_user.user_permissions.add(Permission.objects.get(codename=permission))

    assert InvoiceItem.objects.count() == 0
    data = {
        **USER_DATA,
        "_continue": "1",
        "invoice_set-TOTAL_FORMS": "1",
        "invoice_set-INITIAL_FORMS": "1",
        "invoice_set-0-name": "Test Invoice",
        "invoice_set-0-id": invoice.pk,
        "invoice_set-0-user": staff_user.pk,
        "invoice_set-0-invoiceitem_set-TOTAL_FORMS": "1",
        "invoice_set-0-invoiceitem_set-INITIAL_FORMS": "0",
        "invoice_set-0-invoiceitem_set-0-name": "New Invoice Item Value",
    }

    client.post(
        reverse("admin:example_user_change", args=(staff_user.pk,)),
        data=data,
        follow=True,
    )

    assert InvoiceItem.objects.count() == result


@pytest.mark.django_db
def test_nested_inline_without_parent_permissions(
    client, staff_user, invoice_factory, invoice_item_factory
):
    client.force_login(staff_user)

    invoice = invoice_factory(
        user=staff_user,
        name="Parent Test Invoice",
    )
    invoice_item_factory(invoice=invoice, name="Nested Test Invoice Item")

    # User does not have an access to anything
    response = client.get(reverse("admin:example_user_change", args=(staff_user.pk,)))
    assert "Parent Test Invoice" not in response.content.decode()
    assert "Nested Test Invoice Item" not in response.content.decode()
    assert "<span>Add another Invoice item</span>" not in response.content.decode()
    assert "<span>Add another Invoice</span>" not in response.content.decode()

    # User has an access to add or change parent and nested objects
    staff_user.user_permissions.add(
        Permission.objects.get(codename="view_invoice"),
        Permission.objects.get(codename="add_invoice"),
        Permission.objects.get(codename="change_invoice"),
        Permission.objects.get(codename="add_invoiceitem"),
        Permission.objects.get(codename="change_invoiceitem"),
    )
    response = client.get(reverse("admin:example_user_change", args=(staff_user.pk,)))
    assert "Parent Test Invoice" in response.content.decode()
    assert "Nested Test Invoice Item" in response.content.decode()
    assert "<span>Add another Invoice item</span>" in response.content.decode()
    assert "<span>Add another Invoice</span>" in response.content.decode()

    # User does have an access to nested but not to parent
    staff_user.user_permissions.remove(
        Permission.objects.get(codename="add_invoice"),
        Permission.objects.get(codename="change_invoice"),
    )
    response = client.get(reverse("admin:example_user_change", args=(staff_user.pk,)))
    assert "Parent Test Invoice</div>" in response.content.decode()
    assert 'value="Nested Test Invoice Item"' in response.content.decode()
    assert "<span>Add another Invoice item</span>" in response.content.decode()
    assert "<span>Add another Invoice</span>" not in response.content.decode()

    # User does not have an access to main object
    staff_user.user_permissions.add(
        Permission.objects.get(codename="add_invoice"),
        Permission.objects.get(codename="change_invoice"),
    )
    staff_user.user_permissions.remove(
        Permission.objects.get(codename="change_user"),
        Permission.objects.get(codename="add_user"),
    )
    response = client.get(reverse("admin:example_user_change", args=(staff_user.pk,)))

    assert "Parent Test Invoice</div>" in response.content.decode()
    assert "Nested Test Invoice Item</div>" in response.content.decode()
    assert 'value="Parent Test Invoice"' not in response.content.decode()
    assert 'value="Nested Test Invoice Item"' not in response.content.decode()
    assert "<span>Add another Invoice item</span>" not in response.content.decode()
    assert "<span>Add another Invoice</span>" not in response.content.decode()


@pytest.mark.django_db
def test_nested_inline_without_parent(client, admin_user):
    client.force_login(admin_user)

    assert InvoiceItem.objects.count() == 0

    data = {
        **USER_DATA,
        "_continue": "1",
        "invoice_set-TOTAL_FORMS": "1",
        "invoice_set-INITIAL_FORMS": "0",
        "invoice_set-0-name": "",
        "invoice_set-0-invoiceitem_set-TOTAL_FORMS": "1",
        "invoice_set-0-invoiceitem_set-INITIAL_FORMS": "0",
        "invoice_set-0-invoiceitem_set-0-name": "Updated Invoice Item Value",
    }

    response = client.post(
        reverse("admin:example_user_change", args=(admin_user.pk,)),
        data=data,
        follow=True,
    )

    assert InvoiceItem.objects.count() == 0
    assert "Please correct the errors below." in response.content.decode()
    assert (
        "You can not create nested object without parent" in response.content.decode()
    )


@pytest.mark.django_db
def test_nested_inline_renders_all_levels(
    client, admin_user, invoice_factory, invoice_item_factory
):
    client.force_login(admin_user)
    invoice = invoice_factory(user=admin_user, name="Test Invoice")
    invoice_item_factory(invoice=invoice, name="Test Invoice Item")

    response = client.get(reverse("admin:example_user_change", args=(admin_user.pk,)))
    content = response.content.decode()

    assert response.status_code == HTTPStatus.OK
    assert "invoice_set-0-invoiceitem_set-0-invoiceitempart_set" in content
    assert (
        "invoice_set-0-invoiceitem_set-0-invoiceitempart_set-__prefix__"
        "-invoiceitempartnote_set" in content
    )


@pytest.mark.django_db
def test_nested_inline_create_third_level_object(
    client, admin_user, invoice_factory, invoice_item_factory
):
    client.force_login(admin_user)
    invoice = invoice_factory(user=admin_user, name="Test Invoice")
    invoice_item = invoice_item_factory(invoice=invoice, name="Test Invoice Item")

    data = {
        **USER_DATA,
        "invoice_set-TOTAL_FORMS": "1",
        "invoice_set-INITIAL_FORMS": "1",
        "invoice_set-0-id": invoice.pk,
        "invoice_set-0-user": admin_user.pk,
        "invoice_set-0-name": "Test Invoice",
        "invoice_set-0-invoiceitem_set-TOTAL_FORMS": "1",
        "invoice_set-0-invoiceitem_set-INITIAL_FORMS": "1",
        "invoice_set-0-invoiceitem_set-0-id": invoice_item.pk,
        "invoice_set-0-invoiceitem_set-0-invoice": invoice.pk,
        "invoice_set-0-invoiceitem_set-0-name": "Test Invoice Item",
        "invoice_set-0-invoiceitem_set-0-invoiceitempart_set-TOTAL_FORMS": "1",
        "invoice_set-0-invoiceitem_set-0-invoiceitempart_set-INITIAL_FORMS": "0",
        "invoice_set-0-invoiceitem_set-0-invoiceitempart_set-0-name": "Test Part",
        "invoice_set-0-invoiceitem_set-0-invoiceitempart_set"
        "-0-invoiceitempartnote_set-TOTAL_FORMS": "0",
        "invoice_set-0-invoiceitem_set-0-invoiceitempart_set"
        "-0-invoiceitempartnote_set-INITIAL_FORMS": "0",
    }

    client.post(reverse("admin:example_user_change", args=(admin_user.pk,)), data=data)

    assert InvoiceItemPart.objects.count() == 1
    assert InvoiceItemPart.objects.first().name == "Test Part"
    assert InvoiceItemPart.objects.first().item == invoice_item


@pytest.mark.django_db
def test_nested_inline_create_fourth_level_object(
    client, admin_user, invoice_factory, invoice_item_factory
):
    client.force_login(admin_user)
    invoice = invoice_factory(user=admin_user, name="Test Invoice")
    invoice_item = invoice_item_factory(invoice=invoice, name="Test Invoice Item")

    part_prefix = "invoice_set-0-invoiceitem_set-0-invoiceitempart_set"
    note_prefix = f"{part_prefix}-0-invoiceitempartnote_set"

    data = {
        **USER_DATA,
        "invoice_set-TOTAL_FORMS": "1",
        "invoice_set-INITIAL_FORMS": "1",
        "invoice_set-0-id": invoice.pk,
        "invoice_set-0-user": admin_user.pk,
        "invoice_set-0-name": "Test Invoice",
        "invoice_set-0-invoiceitem_set-TOTAL_FORMS": "1",
        "invoice_set-0-invoiceitem_set-INITIAL_FORMS": "1",
        "invoice_set-0-invoiceitem_set-0-id": invoice_item.pk,
        "invoice_set-0-invoiceitem_set-0-invoice": invoice.pk,
        "invoice_set-0-invoiceitem_set-0-name": "Test Invoice Item",
        f"{part_prefix}-TOTAL_FORMS": "1",
        f"{part_prefix}-INITIAL_FORMS": "0",
        f"{part_prefix}-0-name": "Test Part",
        f"{note_prefix}-TOTAL_FORMS": "1",
        f"{note_prefix}-INITIAL_FORMS": "0",
        f"{note_prefix}-0-name": "Test Note",
    }

    client.post(reverse("admin:example_user_change", args=(admin_user.pk,)), data=data)

    assert InvoiceItemPart.objects.count() == 1
    assert InvoiceItemPartNote.objects.count() == 1
    assert InvoiceItemPartNote.objects.first().name == "Test Note"
    assert InvoiceItemPartNote.objects.first().part == InvoiceItemPart.objects.first()


@pytest.mark.django_db
def test_nested_inline_delete_third_level_object(
    client,
    admin_user,
    invoice_factory,
    invoice_item_factory,
    invoice_item_part_factory,
):
    client.force_login(admin_user)
    invoice = invoice_factory(user=admin_user, name="Test Invoice")
    invoice_item = invoice_item_factory(invoice=invoice, name="Test Invoice Item")
    part = invoice_item_part_factory(item=invoice_item, name="Test Part")

    part_prefix = "invoice_set-0-invoiceitem_set-0-invoiceitempart_set"

    data = {
        **USER_DATA,
        "_continue": "1",
        "invoice_set-TOTAL_FORMS": "1",
        "invoice_set-INITIAL_FORMS": "1",
        "invoice_set-0-id": invoice.pk,
        "invoice_set-0-user": admin_user.pk,
        "invoice_set-0-name": "Test Invoice",
        "invoice_set-0-invoiceitem_set-TOTAL_FORMS": "1",
        "invoice_set-0-invoiceitem_set-INITIAL_FORMS": "1",
        "invoice_set-0-invoiceitem_set-0-id": invoice_item.pk,
        "invoice_set-0-invoiceitem_set-0-invoice": invoice.pk,
        "invoice_set-0-invoiceitem_set-0-name": "Test Invoice Item",
        f"{part_prefix}-TOTAL_FORMS": "1",
        f"{part_prefix}-INITIAL_FORMS": "1",
        f"{part_prefix}-0-id": part.pk,
        f"{part_prefix}-0-item": invoice_item.pk,
        f"{part_prefix}-0-name": "Test Part",
        f"{part_prefix}-0-DELETE": True,
        f"{part_prefix}-0-invoiceitempartnote_set-TOTAL_FORMS": "0",
        f"{part_prefix}-0-invoiceitempartnote_set-INITIAL_FORMS": "0",
    }

    response = client.post(
        reverse("admin:example_user_change", args=(admin_user.pk,)),
        data=data,
        follow=True,
    )

    assert response.status_code == HTTPStatus.OK
    assert InvoiceItem.objects.count() == 1
    assert InvoiceItemPart.objects.count() == 0


@pytest.mark.django_db
def test_nested_inline_deep_level_requires_parent(
    client, admin_user, invoice_factory, invoice_item_factory
):
    """A record can not be created below a parent which is not saved itself."""
    client.force_login(admin_user)
    invoice = invoice_factory(user=admin_user, name="Test Invoice")
    invoice_item_factory(invoice=invoice, name="Test Invoice Item")

    part_prefix = "invoice_set-0-invoiceitem_set-0-invoiceitempart_set"

    data = {
        **USER_DATA,
        "invoice_set-TOTAL_FORMS": "1",
        "invoice_set-INITIAL_FORMS": "0",
        "invoice_set-0-name": "",
        "invoice_set-0-invoiceitem_set-TOTAL_FORMS": "1",
        "invoice_set-0-invoiceitem_set-INITIAL_FORMS": "0",
        "invoice_set-0-invoiceitem_set-0-name": "",
        f"{part_prefix}-TOTAL_FORMS": "1",
        f"{part_prefix}-INITIAL_FORMS": "0",
        f"{part_prefix}-0-name": "Orphan part",
        f"{part_prefix}-0-invoiceitempartnote_set-TOTAL_FORMS": "0",
        f"{part_prefix}-0-invoiceitempartnote_set-INITIAL_FORMS": "0",
    }

    response = client.post(
        reverse("admin:example_user_change", args=(admin_user.pk,)), data=data
    )

    assert response.status_code == HTTPStatus.OK
    assert InvoiceItemPart.objects.count() == 0
    assert (
        "You can not create nested object without parent" in response.content.decode()
    )


@pytest.mark.django_db
def test_nested_inline_file_field_makes_form_multipart(client, admin_user):
    """
    A file field in a nested inline has to switch the whole change form to
    multipart, otherwise the uploaded file never reaches the server.
    """
    client.force_login(admin_user)

    # No invoice exists and the inline has no extra forms, so the file field is
    # only reachable through the template form used for adding records.
    assert admin_user.invoice_set.count() == 0

    response = client.get(reverse("admin:example_user_change", args=(admin_user.pk,)))

    assert response.status_code == HTTPStatus.OK
    assert response.context_data["has_file_field"] is True
    assert 'enctype="multipart/form-data"' in response.content.decode()


@pytest.mark.django_db
def test_nested_inline_file_field_upload(
    client, admin_user, invoice_factory, invoice_item_factory
):
    """A file uploaded into a nested inline reaches the model."""
    client.force_login(admin_user)
    invoice = invoice_factory(user=admin_user, name="Test Invoice")
    item = invoice_item_factory(invoice=invoice, name="Test Invoice Item")

    part_prefix = "invoice_set-0-invoiceitem_set-0-invoiceitempart_set"

    data = {
        **USER_DATA,
        "invoice_set-TOTAL_FORMS": "1",
        "invoice_set-INITIAL_FORMS": "1",
        "invoice_set-0-id": invoice.pk,
        "invoice_set-0-user": admin_user.pk,
        "invoice_set-0-name": "Test Invoice",
        "invoice_set-0-invoiceitem_set-TOTAL_FORMS": "1",
        "invoice_set-0-invoiceitem_set-INITIAL_FORMS": "1",
        "invoice_set-0-invoiceitem_set-0-id": item.pk,
        "invoice_set-0-invoiceitem_set-0-invoice": invoice.pk,
        "invoice_set-0-invoiceitem_set-0-name": "Test Invoice Item",
        f"{part_prefix}-TOTAL_FORMS": "1",
        f"{part_prefix}-INITIAL_FORMS": "0",
        f"{part_prefix}-0-name": "Test Part",
        f"{part_prefix}-0-attachment": SimpleUploadedFile("note.txt", b"content"),
        f"{part_prefix}-0-invoiceitempartnote_set-TOTAL_FORMS": "0",
        f"{part_prefix}-0-invoiceitempartnote_set-INITIAL_FORMS": "0",
    }

    client.post(reverse("admin:example_user_change", args=(admin_user.pk,)), data=data)

    part = InvoiceItemPart.objects.get()
    assert part.name == "Test Part"
    assert part.attachment.name.startswith("parts/note")
    part.attachment.delete(save=False)


@pytest.mark.django_db
def test_nested_inline_through_m2m(client, admin_user, tag_factory):
    """
    An inline rendering a many-to-many intermediary model can nest inlines of
    the model on the other side of that relation.
    """
    tag = tag_factory(name="Tag 1")
    admin_user.tags.add(tag)
    client.force_login(admin_user)

    response = client.get(reverse("admin:example_user_change", args=(admin_user.pk,)))
    content = response.content.decode()

    assert response.status_code == HTTPStatus.OK
    assert "User_tags-0-tagnote_set-TOTAL_FORMS" in content


@pytest.mark.django_db
def test_nested_inline_through_m2m_create(client, admin_user, tag_factory):
    tag = tag_factory(name="Tag 1")
    admin_user.tags.add(tag)
    through = admin_user.tags.through.objects.get(tag=tag)
    client.force_login(admin_user)

    data = {
        **USER_DATA,
        "User_tags-TOTAL_FORMS": "1",
        "User_tags-INITIAL_FORMS": "1",
        "User_tags-0-id": through.pk,
        "User_tags-0-user": admin_user.pk,
        "User_tags-0-tag": tag.pk,
        "User_tags-0-tagnote_set-TOTAL_FORMS": "1",
        "User_tags-0-tagnote_set-INITIAL_FORMS": "0",
        "User_tags-0-tagnote_set-0-name": "Tag note",
        "User_tags-0-tagusernote_set-TOTAL_FORMS": "0",
        "User_tags-0-tagusernote_set-INITIAL_FORMS": "0",
        "invoice_set-TOTAL_FORMS": "0",
        "invoice_set-INITIAL_FORMS": "0",
    }

    client.post(reverse("admin:example_user_change", args=(admin_user.pk,)), data=data)

    assert TagNote.objects.count() == 1
    assert TagNote.objects.first().name == "Tag note"
    assert TagNote.objects.first().tag == tag


@pytest.mark.django_db
def test_nested_inline_self_referential_respects_max_depth(client, admin_user):
    """
    A chain of inlines referring to itself is rendered as deep as
    `nested_inlines_max_depth` allows and not deeper.
    """
    client.force_login(admin_user)
    root = Category.objects.create(name="Root")
    child = Category.objects.create(name="Child", parent=root)
    Category.objects.create(name="Grandchild", parent=child)

    response = client.get(reverse("admin:example_categorytree_change", args=(root.pk,)))
    content = response.content.decode()

    assert response.status_code == HTTPStatus.OK
    assert "Child" in content
    assert "Grandchild" in content

    # CategoryTreeAdmin sets nested_inlines_max_depth = 4
    deepest = "children" + "-__prefix__-children" * 4
    assert f"{deepest}-TOTAL_FORMS" in content
    assert f"{deepest}-__prefix__-children" not in content


@pytest.mark.django_db
def test_nested_inline_self_referential_without_max_depth_raises(
    client, admin_user, monkeypatch
):
    """
    The system check reports self-referencing chains, this is the guard for the
    case where that check has been silenced.
    """
    from example.admin import CategoryTreeAdmin

    monkeypatch.setattr(CategoryTreeAdmin, "nested_inlines_max_depth", None)
    client.force_login(admin_user)
    category = Category.objects.create(name="Root")

    with pytest.raises(ImproperlyConfigured) as error:
        client.get(reverse("admin:example_categorytree_change", args=(category.pk,)))

    assert "is nested within itself" in str(error.value)


@pytest.mark.django_db
def test_nested_inline_named_relation_through_m2m(client, admin_user, tag_factory):
    """`nested_parent_field` picks the relation when several would fit."""
    tag = tag_factory(name="Tag 1")
    admin_user.tags.add(tag)
    client.force_login(admin_user)

    response = client.get(reverse("admin:example_user_change", args=(admin_user.pk,)))

    assert response.status_code == HTTPStatus.OK
    assert "User_tags-0-tagusernote_set-TOTAL_FORMS" in response.content.decode()


@pytest.mark.django_db
def test_nested_inline_ambiguous_relation_raises():
    """
    An intermediary model can point at several models, so the relation to
    traverse has to be unambiguous when it is not named explicitly.
    """

    class AmbiguousInline(TabularInline):
        model = TagUserNote

    model_admin = UserAdmin(User, admin.site)

    with pytest.raises(ImproperlyConfigured) as error:
        model_admin._get_nested_parent_field_name(User.tags.through, AmbiguousInline)

    assert "through more than one relation" in str(error.value)


@pytest.mark.django_db
def test_nested_inline_without_relation_is_not_reparented():
    """
    Traversing a relation of the parent model is only right for an intermediary
    model. Anywhere else an inline without a relation to its parent stays the
    configuration error it always was.
    """

    class PostInline(TabularInline):
        model = Post  # foreign key to User, none to Invoice

    model_admin = UserAdmin(User, admin.site)

    assert model_admin._get_nested_parent_field_name(Invoice, PostInline) is None


@pytest.mark.django_db
def test_nested_inline_through_m2m_create_with_new_parent_row(
    client, admin_user, tag_factory
):
    """A record can be added below a through row created by the same request."""
    tag = tag_factory(name="Tag 1")
    client.force_login(admin_user)

    data = {
        **USER_DATA,
        "User_tags-TOTAL_FORMS": "1",
        "User_tags-INITIAL_FORMS": "0",
        "User_tags-0-tag": tag.pk,
        "User_tags-0-tagnote_set-TOTAL_FORMS": "1",
        "User_tags-0-tagnote_set-INITIAL_FORMS": "0",
        "User_tags-0-tagnote_set-0-name": "Fresh note",
        "User_tags-0-tagusernote_set-TOTAL_FORMS": "0",
        "User_tags-0-tagusernote_set-INITIAL_FORMS": "0",
        "invoice_set-TOTAL_FORMS": "0",
        "invoice_set-INITIAL_FORMS": "0",
    }

    response = client.post(
        reverse("admin:example_user_change", args=(admin_user.pk,)), data=data
    )

    assert response.status_code == HTTPStatus.FOUND
    assert TagNote.objects.get().tag == tag


@pytest.mark.django_db
def test_nested_inline_through_m2m_follows_changed_relation(
    client, admin_user, tag_factory
):
    """
    The nested records belong to the object the submitted data names, not to the
    one the relation pointed at while the form was rendered.
    """
    tag = tag_factory(name="Tag 1")
    another_tag = tag_factory(name="Tag 2")
    admin_user.tags.add(tag)
    through = admin_user.tags.through.objects.get(tag=tag)
    client.force_login(admin_user)

    data = {
        **USER_DATA,
        "User_tags-TOTAL_FORMS": "1",
        "User_tags-INITIAL_FORMS": "1",
        "User_tags-0-id": through.pk,
        "User_tags-0-user": admin_user.pk,
        "User_tags-0-tag": another_tag.pk,
        "User_tags-0-tagnote_set-TOTAL_FORMS": "1",
        "User_tags-0-tagnote_set-INITIAL_FORMS": "0",
        "User_tags-0-tagnote_set-0-name": "Tag note",
        "User_tags-0-tagusernote_set-TOTAL_FORMS": "0",
        "User_tags-0-tagusernote_set-INITIAL_FORMS": "0",
        "invoice_set-TOTAL_FORMS": "0",
        "invoice_set-INITIAL_FORMS": "0",
    }

    client.post(reverse("admin:example_user_change", args=(admin_user.pk,)), data=data)

    through.refresh_from_db()
    assert through.tag == another_tag
    assert TagNote.objects.get().tag == another_tag


@pytest.mark.django_db
def test_nested_inline_collapsed_by_default(
    client, admin_user, invoice_factory, invoice_item_factory, invoice_item_part_factory
):
    """
    A nested inline with the `collapse` class starts closed, which keeps a deep
    hierarchy readable.
    """
    client.force_login(admin_user)
    invoice = invoice_factory(user=admin_user, name="Test Invoice")
    item = invoice_item_factory(invoice=invoice, name="Test Invoice Item")
    invoice_item_part_factory(item=item, name="Test Part")

    response = client.get(reverse("admin:example_user_change", args=(admin_user.pk,)))
    content = response.content.decode()

    assert response.status_code == HTTPStatus.OK
    assert 'x-data="{ open: false }"' in content
    assert 'x-data="{ open: true }"' not in content
    assert 'x-on:click="open = !open"' in content


@pytest.mark.django_db
def test_nested_inline_with_errors_is_not_collapsed(
    client, admin_user, invoice_factory, invoice_item_factory, invoice_item_part_factory
):
    """Errors are never hidden behind a closed section."""
    client.force_login(admin_user)
    invoice = invoice_factory(user=admin_user, name="Test Invoice")
    item = invoice_item_factory(invoice=invoice, name="Test Invoice Item")
    part = invoice_item_part_factory(item=item, name="Test Part")

    part_prefix = "invoice_set-0-invoiceitem_set-0-invoiceitempart_set"

    data = {
        **USER_DATA,
        "invoice_set-TOTAL_FORMS": "1",
        "invoice_set-INITIAL_FORMS": "1",
        "invoice_set-0-id": invoice.pk,
        "invoice_set-0-user": admin_user.pk,
        "invoice_set-0-name": "Test Invoice",
        "invoice_set-0-invoiceitem_set-TOTAL_FORMS": "1",
        "invoice_set-0-invoiceitem_set-INITIAL_FORMS": "1",
        "invoice_set-0-invoiceitem_set-0-id": item.pk,
        "invoice_set-0-invoiceitem_set-0-invoice": invoice.pk,
        "invoice_set-0-invoiceitem_set-0-name": "Test Invoice Item",
        f"{part_prefix}-TOTAL_FORMS": "1",
        f"{part_prefix}-INITIAL_FORMS": "1",
        f"{part_prefix}-0-id": part.pk,
        f"{part_prefix}-0-item": item.pk,
        f"{part_prefix}-0-name": "",
        f"{part_prefix}-0-invoiceitempartnote_set-TOTAL_FORMS": "0",
        f"{part_prefix}-0-invoiceitempartnote_set-INITIAL_FORMS": "0",
    }

    response = client.post(
        reverse("admin:example_user_change", args=(admin_user.pk,)), data=data
    )
    content = response.content.decode()

    assert response.status_code == HTTPStatus.OK
    assert "This field is required." in content

    nested_formsets = {
        nested.formset.prefix: nested
        for nested in iter_nested_formsets(
            admin_formset.formset
            for admin_formset in response.context_data["inline_admin_formsets"]
        )
    }

    # The formset holding the error is rendered expanded, the sibling levels
    # keep collapsing.
    assert nested_formsets[part_prefix].is_collapsible is False
    assert (
        nested_formsets[f"{part_prefix}-0-invoiceitempartnote_set"].is_collapsible
        is True
    )


@pytest.mark.django_db
def test_top_level_collapsible_stacked_inline_has_no_orphan_alpine_binding(
    client, admin_user, tag_factory, monkeypatch
):
    """
    The `open` value only exists for a nested inline, so a top level one must
    not bind to it. It collapses through the surrounding `details` element.
    """
    monkeypatch.setattr(UserTagInline, "classes", ["collapse"])
    tag = tag_factory(name="Tag 1")
    admin_user.tags.add(tag)
    client.force_login(admin_user)

    response = client.get(reverse("admin:example_user_change", args=(admin_user.pk,)))
    content = response.content.decode()

    assert response.status_code == HTTPStatus.OK

    element = re.search(r'<div id="User_tags-data"[^>]*>', content)
    assert element is not None
    assert 'x-show="open"' not in element.group(0)


@pytest.mark.django_db
def test_nested_inline_media_is_rendered_and_not_kept_on_the_model_admin(
    client, admin_user, invoice_factory, invoice_item_factory
):
    """
    The media of the nested inlines reaches the page, and is collected per
    request rather than on the ModelAdmin, which is shared by every request.
    """
    client.force_login(admin_user)
    invoice = invoice_factory(user=admin_user, name="Test Invoice")
    invoice_item_factory(invoice=invoice, name="Test Invoice Item")

    response = client.get(reverse("admin:example_user_change", args=(admin_user.pk,)))

    assert response.status_code == HTTPStatus.OK
    assert not hasattr(UserAdmin, "nested_formset_media")

    rendered = str(response.context_data["media"])
    for admin_formset in response.context_data["inline_admin_formsets"]:
        for nested in iter_nested_formsets([admin_formset.formset]):
            for asset in nested.media.render_js():
                assert str(asset) in rendered
