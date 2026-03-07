from http import HTTPStatus

import pytest
from django.contrib.auth.models import Permission
from django.urls import reverse
from example.models import Invoice, InvoiceItem

from .factories import TagFactory

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
    }
    client.post(reverse("admin:example_user_change", args=(admin_user.pk,)), data=data)

    assert Invoice.objects.count() == 1
    assert Invoice.objects.first().name == "Test Invoice"
    assert Invoice.objects.first().user == admin_user
    assert InvoiceItem.objects.count() == 1
    assert InvoiceItem.objects.first().name == "Test Invoice Item"
    assert InvoiceItem.objects.first().invoice == Invoice.objects.first()


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
