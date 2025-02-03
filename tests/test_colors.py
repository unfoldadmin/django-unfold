from django.contrib.auth.models import AnonymousUser
from django.test.client import RequestFactory
from django.test.utils import override_settings

from unfold.settings import CONFIG_DEFAULTS
from unfold.sites import UnfoldAdminSite


@override_settings(
    UNFOLD={
        **CONFIG_DEFAULTS,
        **{
            "COLORS": {
                "primary": {
                    50: "#f0f9ff",
                    100: "#e0f2fe",
                    200: "#bae6fd",
                    300: "#7dd3fc",
                    400: "#38bdf8",
                    500: "#0ea5e9",
                    600: "#0284c7",
                    700: "#0369a1",
                    800: "#075985",
                    900: "#0c4a6e",
                    950: "#082f49",
                }
            },
        },
    }
)
def test_colors_hex_to_rgb():
    admin_site = UnfoldAdminSite()
    request = RequestFactory().get("/rand")
    request.user = AnonymousUser()
    context = admin_site.each_context(request)

    assert "colors" in context
    assert "primary" in context["colors"]

    assert context["colors"]["primary"][50] == "240 249 255"
    assert context["colors"]["primary"][100] == "224 242 254"
    assert context["colors"]["primary"][200] == "186 230 253"
    assert context["colors"]["primary"][300] == "125 211 252"
    assert context["colors"]["primary"][400] == "56 189 248"
    assert context["colors"]["primary"][500] == "14 165 233"
    assert context["colors"]["primary"][600] == "2 132 199"
    assert context["colors"]["primary"][700] == "3 105 161"
    assert context["colors"]["primary"][800] == "7 89 133"
    assert context["colors"]["primary"][900] == "12 74 110"
    assert context["colors"]["primary"][950] == "8 47 73"


@override_settings(
    UNFOLD={
        **CONFIG_DEFAULTS,
        **{
            "COLORS": {
                "primary": {
                    50: "240 249 255",
                    100: "224 242 254",
                    200: "186 230 253",
                    300: "125 211 252",
                    400: "56 189 248",
                    500: "14 165 233",
                    600: "2 132 199",
                    700: "3 105 161",
                    800: "7 89 133",
                    900: "12 74 110",
                    950: "8 47 73",
                }
            },
        },
    }
)
def test_colors_rgb():
    admin_site = UnfoldAdminSite()
    request = RequestFactory().get("/rand")
    request.user = AnonymousUser()
    context = admin_site.each_context(request)
    assert "colors" in context
    assert "primary" in context["colors"]

    assert context["colors"]["primary"][50] == "240 249 255"
    assert context["colors"]["primary"][100] == "224 242 254"
    assert context["colors"]["primary"][200] == "186 230 253"
    assert context["colors"]["primary"][300] == "125 211 252"
    assert context["colors"]["primary"][400] == "56 189 248"
    assert context["colors"]["primary"][500] == "14 165 233"
    assert context["colors"]["primary"][600] == "2 132 199"
    assert context["colors"]["primary"][700] == "3 105 161"
    assert context["colors"]["primary"][800] == "7 89 133"
    assert context["colors"]["primary"][900] == "12 74 110"
    assert context["colors"]["primary"][950] == "8 47 73"


@override_settings(
    UNFOLD={
        **CONFIG_DEFAULTS,
        **{
            "COLORS": {
                "primary": {
                    50: "rgb(240, 249, 255)",
                    100: "rgb(224, 242, 254)",
                    200: "rgb(186, 230, 253)",
                    300: "rgb(125, 211, 252)",
                    400: "rgb(56, 189, 248)",
                    500: "rgb(14, 165, 233)",
                    600: "rgb(2, 132, 199)",
                    700: "rgb(3, 105, 161)",
                    800: "rgb(7, 89, 133)",
                    900: "rgb(12, 74, 110)",
                    950: "rgb(8, 47, 73)",
                }
            },
        },
    }
)
def test_colors_full_rgb_conversion():
    admin_site = UnfoldAdminSite()
    request = RequestFactory().get("/rand")
    request.user = AnonymousUser()
    context = admin_site.each_context(request)
    assert "colors" in context
    assert "primary" in context["colors"]

    assert context["colors"]["primary"][50] == "240 249 255"
    assert context["colors"]["primary"][100] == "224 242 254"
    assert context["colors"]["primary"][200] == "186 230 253"
    assert context["colors"]["primary"][300] == "125 211 252"
    assert context["colors"]["primary"][400] == "56 189 248"
    assert context["colors"]["primary"][500] == "14 165 233"
    assert context["colors"]["primary"][600] == "2 132 199"
    assert context["colors"]["primary"][700] == "3 105 161"
    assert context["colors"]["primary"][800] == "7 89 133"
    assert context["colors"]["primary"][900] == "12 74 110"
    assert context["colors"]["primary"][950] == "8 47 73"
