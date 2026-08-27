import json
from http import HTTPStatus

import pytest
from django.contrib.admin.sites import site
from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied
from django.test import Client, RequestFactory
from django.urls import reverse
from example.admin import AddressAdmin, CityAdmin, CountryAdmin, StateAdmin
from example.models import Address, City, Country, Person, PersonLocation, State

from unfold.admin import GenericTabularInline, ModelAdmin, TabularInline
from unfold.sites import UnfoldAdminSite
from unfold.views import DependentAutocompleteJsonView
from unfold.widgets import DependentAutocompleteSelect


@pytest.fixture
def geography(db):
    united_states = Country.objects.create(name="United States")
    states = {
        "california": State.objects.create(country=united_states, name="California"),
        "texas": State.objects.create(country=united_states, name="Texas"),
    }
    cities = {
        "san_francisco": City.objects.create(
            state=states["california"], name="San Francisco"
        ),
        "los_angeles": City.objects.create(
            state=states["california"], name="Los Angeles"
        ),
        "houston": City.objects.create(state=states["texas"], name="Houston"),
    }
    return {
        "united_states": united_states,
        "states": states,
        "cities": cities,
    }


@pytest.fixture
def dependent_admin_client(db):
    user = get_user_model().objects.create_superuser(
        "admin", "admin@example.com", "password"
    )
    client = Client()
    client.force_login(user)
    return client


def dependent_params(field_name, parent, **extra):
    return {
        "term": "",
        "app_label": "example",
        "model_name": "address",
        "field_name": field_name,
        "dependent_parent": str(parent.pk),
        **extra,
    }


def result_texts(response):
    return [result["text"] for result in response.json()["results"]]


def test_dependent_autocomplete_media_loads_after_jquery_init():
    field = Address._meta.get_field("selected_state")
    widget = DependentAutocompleteSelect(
        field,
        site,
        parent_field_name="selected_country",
        source_admin=AddressAdmin(Address, site),
    )
    rendered_js = str(widget.media["js"])

    assert rendered_js.index("jquery.init.js") < rendered_js.index(
        "dependent-autocomplete.js"
    )


def test_shorthand_dependency_is_normalized():
    class ShorthandAdmin(ModelAdmin):
        autocomplete_dependencies = {"selected_city": "selected_state"}

    model_admin = ShorthandAdmin(Address, UnfoldAdminSite())

    assert model_admin.get_autocomplete_dependency_config("selected_city") == {
        "depends_on": "selected_state",
        "lookup": "selected_state",
    }


@pytest.mark.django_db
def test_dependent_autocomplete_filters_by_configured_lookup(
    dependent_admin_client, geography
):
    united_states = geography["united_states"]
    california = geography["states"]["california"]
    url = reverse("admin:example_address_dependent_autocomplete")

    state_response = dependent_admin_client.get(
        url,
        dependent_params("selected_state", united_states),
    )
    city_response = dependent_admin_client.get(
        url,
        dependent_params("selected_city", california),
    )
    search_response = dependent_admin_client.get(
        url,
        dependent_params("selected_city", california, term="San"),
    )

    assert state_response.status_code == HTTPStatus.OK
    assert result_texts(state_response) == ["California", "Texas"]
    assert result_texts(city_response) == ["Los Angeles", "San Francisco"]
    assert result_texts(search_response) == ["San Francisco"]


@pytest.mark.django_db
def test_empty_parent_returns_no_results(dependent_admin_client, geography):
    response = dependent_admin_client.get(
        reverse("admin:example_address_dependent_autocomplete"),
        dependent_params(
            "selected_state", geography["united_states"], dependent_parent=""
        ),
    )

    assert response.status_code == HTTPStatus.OK
    assert result_texts(response) == []


@pytest.mark.django_db
def test_unconfigured_field_on_dependent_url_is_forbidden(
    dependent_admin_client, geography
):
    response = dependent_admin_client.get(
        reverse("admin:example_address_dependent_autocomplete"),
        dependent_params("backup_city", geography["states"]["california"]),
    )

    assert response.status_code == HTTPStatus.FORBIDDEN


@pytest.mark.django_db
def test_mismatched_source_model_on_dependent_url_is_forbidden(
    dependent_admin_client, geography
):
    response = dependent_admin_client.get(
        reverse("admin:example_address_dependent_autocomplete"),
        {
            "term": "",
            "app_label": "example",
            "model_name": "personlocation",
            "field_name": "selected_city",
            "dependent_parent": str(geography["states"]["california"].pk),
        },
    )

    assert response.status_code == HTTPStatus.FORBIDDEN


@pytest.mark.django_db
def test_invalid_parent_pk_returns_no_results(dependent_admin_client, geography):
    response = dependent_admin_client.get(
        reverse("admin:example_address_dependent_autocomplete"),
        dependent_params(
            "selected_state",
            geography["united_states"],
            dependent_parent="not-a-pk",
        ),
    )

    assert response.status_code == HTTPStatus.OK
    assert result_texts(response) == []


@pytest.mark.django_db
def test_dependent_autocomplete_preserves_search_distinct(
    dependent_admin_client, geography, monkeypatch
):
    def get_search_results(self, request, queryset, search_term):
        queryset, _use_distinct = ModelAdmin.get_search_results(
            self, request, queryset, search_term
        )
        return queryset, True

    monkeypatch.setattr(CityAdmin, "get_search_results", get_search_results)
    response = dependent_admin_client.get(
        reverse("admin:example_address_dependent_autocomplete"),
        dependent_params("selected_city", geography["states"]["california"]),
    )

    assert response.status_code == HTTPStatus.OK
    assert result_texts(response) == ["Los Angeles", "San Francisco"]


@pytest.mark.django_db
def test_normal_autocomplete_ignores_dependent_parent(
    dependent_admin_client, geography
):
    response = dependent_admin_client.get(
        reverse("admin:autocomplete"),
        {
            "term": "Los",
            "app_label": "example",
            "model_name": "address",
            "field_name": "backup_city",
            "dependent_parent": str(geography["states"]["california"].pk),
        },
    )

    assert response.status_code == HTTPStatus.OK
    assert result_texts(response) == ["Los Angeles"]


@pytest.mark.django_db
def test_dependent_autocomplete_requires_permissions(geography):
    user = get_user_model().objects.create_user(
        "staff", "staff@example.com", "password", is_staff=True
    )
    client = Client()
    client.force_login(user)

    response = client.get(
        reverse("admin:example_address_dependent_autocomplete"),
        dependent_params("selected_state", geography["united_states"]),
    )

    assert response.status_code == HTTPStatus.FORBIDDEN


@pytest.mark.django_db
def test_change_form_preserves_chained_dependent_values(
    dependent_admin_client, geography
):
    states = geography["states"]
    cities = geography["cities"]
    address = Address.objects.create(
        selected_country=geography["united_states"],
        selected_state=states["california"],
        selected_city=cities["san_francisco"],
        street="1 Market Street",
    )

    response = dependent_admin_client.get(
        reverse("admin:example_address_change", args=[address.pk])
    )

    assert response.status_code == HTTPStatus.OK
    content = response.content.decode()
    assert (
        f'<option value="{states["california"].pk}" selected>California</option>'
        in content
    )
    assert (
        f'<option value="{cities["san_francisco"].pk}" selected>San Francisco</option>'
        in content
    )
    assert 'data-dependent-autocomplete-parent="selected_country"' in content
    assert 'data-dependent-autocomplete-parent="selected_state"' in content


@pytest.mark.parametrize(
    ("dependencies", "autocomplete_fields", "expected_ids"),
    [
        (["selected_city"], ["selected_city"], ["unfold.E001"]),
        ({"selected_city": "missing"}, ["selected_city"], ["unfold.E004"]),
        (
            {"selected_city": {"depends_on": "selected_state", "lookup": "name"}},
            ["selected_city"],
            ["unfold.E007"],
        ),
        (
            {
                "selected_city": {
                    "depends_on": "selected_state",
                    "lookup": "state__country",
                }
            },
            ["selected_city"],
            ["unfold.E008"],
        ),
        ({"selected_city": "selected_state"}, ["selected_state"], ["unfold.E003"]),
        ({"selected_city": "street"}, ["selected_city"], ["unfold.E005"]),
        (
            {"selected_city": {"depends_on": "selected_state", "lookup": "country"}},
            ["selected_city"],
            ["unfold.E006"],
        ),
        ({1: "selected_state"}, ["selected_city"], ["unfold.E002"]),
        ({"selected_city": 123}, ["selected_city"], ["unfold.E002"]),
        (
            {"selected_city": {"depends_on": "selected_state"}},
            ["selected_city"],
            ["unfold.E002"],
        ),
    ],
)
def test_invalid_autocomplete_dependencies_raise_system_checks(
    dependencies, autocomplete_fields, expected_ids
):
    class InvalidAdmin(ModelAdmin):
        pass

    InvalidAdmin.autocomplete_fields = autocomplete_fields
    InvalidAdmin.autocomplete_dependencies = dependencies

    model_admin = InvalidAdmin(Address, UnfoldAdminSite())
    errors = model_admin._check_autocomplete_dependencies()

    assert [error.id for error in errors] == expected_ids


@pytest.mark.django_db
def test_inline_dependent_autocomplete_without_registered_model(
    dependent_admin_client, geography
):
    assert not site.is_registered(PersonLocation)
    url = reverse("admin:example_person_personlocationinline_dependent_autocomplete")
    california = geography["states"]["california"]

    response = dependent_admin_client.get(
        url,
        {
            "term": "",
            "app_label": "example",
            "model_name": "personlocation",
            "field_name": "selected_city",
            "dependent_parent": str(california.pk),
        },
    )

    assert response.status_code == HTTPStatus.OK
    assert result_texts(response) == ["Los Angeles", "San Francisco"]


@pytest.mark.django_db
def test_standalone_modeladmin_does_not_control_inline_config(geography):
    admin_site = UnfoldAdminSite(name="partial")
    admin_site.register(Country, CountryAdmin)
    admin_site.register(State, StateAdmin)
    admin_site.register(City, CityAdmin)

    class PartialLocationAdmin(ModelAdmin):
        autocomplete_fields = ["selected_state"]
        autocomplete_dependencies = {
            "selected_state": {
                "depends_on": "selected_country",
                "lookup": "country",
            },
        }

    class FullLocationInline(TabularInline):
        model = PersonLocation
        autocomplete_fields = ["selected_state", "selected_city"]
        autocomplete_dependencies = {
            "selected_state": {
                "depends_on": "selected_country",
                "lookup": "country",
            },
            "selected_city": {
                "depends_on": "selected_state",
                "lookup": "state",
            },
        }

    class HostAdmin(ModelAdmin):
        inlines = [FullLocationInline]

    admin_site.register(PersonLocation, PartialLocationAdmin)
    admin_site.register(Person, HostAdmin)

    inline = FullLocationInline(Person, admin_site)
    standalone = PartialLocationAdmin(PersonLocation, admin_site)
    user = get_user_model().objects.create_superuser(
        "inline-admin", "inline@example.com", "password"
    )
    factory = RequestFactory()
    params = {
        "term": "",
        "app_label": "example",
        "model_name": "personlocation",
        "field_name": "selected_city",
        "dependent_parent": str(geography["states"]["california"].pk),
    }

    def request():
        http_request = factory.get("/dependent-autocomplete/", params)
        http_request.user = user
        return http_request

    inline_response = DependentAutocompleteJsonView.as_view(
        admin_site=admin_site,
        source_model_admin=inline,
    )(request())

    assert inline.get_dependent_autocomplete_url_name() == (
        "example_person_fulllocationinline_dependent_autocomplete"
    )
    assert standalone.get_dependent_autocomplete_url_name() == (
        "example_personlocation_dependent_autocomplete"
    )
    assert inline_response.status_code == HTTPStatus.OK
    assert [
        result["text"] for result in json.loads(inline_response.content)["results"]
    ] == ["Los Angeles", "San Francisco"]
    with pytest.raises(PermissionDenied):
        DependentAutocompleteJsonView.as_view(
            admin_site=admin_site,
            source_model_admin=standalone,
        )(request())


def test_inline_autocomplete_dependencies_system_checks_run():
    class InvalidInline(TabularInline):
        model = PersonLocation
        autocomplete_fields = ["selected_city"]
        autocomplete_dependencies = {"selected_city": "missing"}

    inline = InvalidInline(Person, UnfoldAdminSite())
    errors = inline.check()

    assert "unfold.E004" in [error.id for error in errors]


def test_generic_inline_autocomplete_dependencies_system_checks_run():
    class InvalidGenericInline(GenericTabularInline):
        model = PersonLocation
        autocomplete_fields = ["selected_city"]
        autocomplete_dependencies = {"selected_city": "missing"}

    inline = InvalidGenericInline(Person, UnfoldAdminSite())
    errors = inline.check()

    assert "unfold.E004" in [error.id for error in errors]


def test_duplicate_inline_dependent_autocomplete_url_names():
    class LocationInline(TabularInline):
        model = PersonLocation
        autocomplete_fields = ["selected_state"]
        autocomplete_dependencies = {
            "selected_state": {
                "depends_on": "selected_country",
                "lookup": "country",
            },
        }

    class DuplicateInlineHost(ModelAdmin):
        inlines = [LocationInline, LocationInline]

    model_admin = DuplicateInlineHost(Person, UnfoldAdminSite())
    errors = model_admin.check()

    assert "unfold.E009" in [error.id for error in errors]
