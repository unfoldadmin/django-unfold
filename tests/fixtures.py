import pytest
from django.contrib import admin, messages
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.shortcuts import redirect
from django.test import RequestFactory
from django.urls import reverse_lazy
from django.utils.timezone import now

from unfold.admin import ModelAdmin
from unfold.decorators import action
from unfold.forms import AdminPasswordChangeForm, UserChangeForm, UserCreationForm
from unfold.sites import UnfoldAdminSite

User = get_user_model()


@pytest.fixture
def admin_user():
    return User.objects.create_superuser(
        username="admin@example.com",
        email="admin@example.com",
        password="password",
        date_joined=now(),
    )


@pytest.fixture
def admin_request(admin_user):
    request = RequestFactory().get("/")
    request.user = admin_user
    return request


@pytest.fixture
def user_model_admin():
    return ModelAdmin(model=User, admin_site=UnfoldAdminSite())


@pytest.fixture
def user_changelist(admin_request, user_model_admin):
    return user_model_admin.get_changelist_instance(admin_request)


@pytest.fixture
def user_model_admin_with_actions():
    admin.site.unregister(User)

    @admin.register(User)
    class UserModelAdmin(BaseUserAdmin, ModelAdmin):
        form = UserChangeForm
        add_form = UserCreationForm
        change_password_form = AdminPasswordChangeForm

        actions_list = [
            "changelist_action",
            "changelist_action_permission_true",
            "changelist_action_permission_false",
            "changelist_action_multiple_different_permissions",
            {
                "title": "Changelist dropdown for actions",
                "items": [
                    "changelist_action_dropdown",
                ],
            },
        ]
        actions_row = [
            "changelist_row_action",
            "changelist_row_action_permission_true",
            "changelist_row_action_permission_false",
            "changelist_row_action_multiple_different_permissions",
        ]
        actions_detail = [
            "changeform_action",
            "changeform_action_permission_true",
            "changeform_action_permission_false",
            "changeform_action_multiple_different_permissions",
            {
                "title": "Changeform dropdown for actions",
                "items": [
                    "changeform_action_dropdown",
                ],
            },
        ]
        actions_submit_line = [
            "submit_line_action",
            "submit_line_action_permission_true",
            "submit_line_action_permission_false",
            "submit_line_action_multiple_different_permissions",
        ]

        ######################################################################
        # Changelist actions
        ######################################################################
        @action(description="Changelist action dropdown")
        def changelist_action_dropdown(self, request):
            messages.success(
                request, "Changelist action dropdown successfully executed"
            )
            return redirect(reverse_lazy("admin:example_user_changelist"))

        @action(description="Changelist action")
        def changelist_action(self, request):
            messages.success(request, "Changelist action successfully executed")
            return redirect(reverse_lazy("admin:example_user_changelist"))

        @action(
            description="Changelist action permission true",
            permissions=["changelist_action_true"],
        )
        def changelist_action_permission_true(self, request):
            messages.success(
                request, "Changelist action with true permission successfully executed"
            )
            return redirect(reverse_lazy("admin:example_user_changelist"))

        @action(
            description="Changelist action permission false",
            permissions=["changelist_action_false"],
        )
        def changelist_action_permission_false(self, request):
            messages.success(
                request, "Changelist action with false permission successfully executed"
            )
            return redirect(reverse_lazy("admin:example_user_changelist"))

        @action(
            description="Changelist action with multiple permissions",
            permissions=[
                "changelist_action_true",
                "changelist_action_false",
            ],
        )
        def changelist_action_multiple_different_permissions(self, request):
            messages.success(
                request,
                "Changelist action with multiple different permissions successfully executed",
            )
            return redirect(reverse_lazy("admin:example_user_changelist"))

        def has_changelist_action_true_permission(self, request):
            return True

        def has_changelist_action_false_permission(self, request):
            return False

        ######################################################################
        # Changelist row actions
        ######################################################################
        @action(description="Changelist row action")
        def changelist_row_action(self, request, object_id):
            messages.success(request, "Changelist row action successfully executed")
            return redirect(reverse_lazy("admin:example_user_changelist"))

        @action(
            description="Changelist row action permission true",
            permissions=["changelist_row_action_true"],
        )
        def changelist_row_action_permission_true(self, request, object_id):
            messages.success(
                request,
                "Changelist row action with true permission successfully executed",
            )
            return redirect(reverse_lazy("admin:example_user_changelist"))

        @action(
            description="Changelist row action permission false",
            permissions=["changelist_row_action_false"],
        )
        def changelist_row_action_permission_false(self, request, object_id):
            messages.success(
                request,
                "Changelist row action with false permission successfully executed",
            )
            return redirect(reverse_lazy("admin:example_user_changelist"))

        @action(
            description="Changelist row action with multiple permissions",
            permissions=[
                "changelist_row_action_true",
                "changelist_row_action_false",
            ],
        )
        def changelist_row_action_multiple_different_permissions(
            self, request, object_id
        ):
            messages.success(
                request,
                "Changelist row action with multiple different permissions successfully executed",
            )
            return redirect(reverse_lazy("admin:example_user_changelist"))

        def has_changelist_row_action_true_permission(self, request):
            return True

        def has_changelist_row_action_false_permission(self, request):
            return False

        ######################################################################
        # Changeform actions
        ######################################################################
        @action(description="Changeform action dropdown")
        def changeform_action_dropdown(self, request, object_id):
            messages.success(
                request, "Changeform action dropdown successfully executed"
            )
            return redirect(reverse_lazy("admin:example_user_changelist"))

        @action(description="Changeform action")
        def changeform_action(self, request, object_id):
            messages.success(request, "Changeform action successfully executed")
            return redirect(reverse_lazy("admin:example_user_changelist"))

        @action(
            description="Changeform action permission true",
            permissions=["changeform_action_true"],
        )
        def changeform_action_permission_true(self, request, object_id):
            messages.success(
                request,
                "Changeform action with true permission successfully executed",
            )
            return redirect(reverse_lazy("admin:example_user_changelist"))

        @action(
            description="Changeform action permission false",
            permissions=["changeform_action_false"],
        )
        def changeform_action_permission_false(self, request, object_id):
            messages.success(
                request,
                "Changeform action with false permission successfully executed",
            )
            return redirect(reverse_lazy("admin:example_user_changelist"))

        @action(
            description="Changeform action with multiple permissions",
            permissions=[
                "changeform_action_true",
                "changeform_action_false",
            ],
        )
        def changeform_action_multiple_different_permissions(self, request, object_id):
            messages.success(
                request,
                "Changeform action with multiple different permissions successfully executed",
            )
            return redirect(reverse_lazy("admin:example_user_changelist"))

        def has_changeform_action_true_permission(self, request, object_id):
            return True

        def has_changeform_action_false_permission(self, request, object_id):
            return False

        ######################################################################
        # Submit line actions
        ######################################################################
        @action(description="Submit line action")
        def submit_line_action(self, request, obj):
            messages.success(request, "Submit line action successfully executed")

        @action(
            description="Submit line action permission true",
            permissions=["submit_line_action_true"],
        )
        def submit_line_action_permission_true(self, request, obj):
            messages.success(
                request,
                "Submit line action with true permission successfully executed",
            )

        @action(
            description="Submit line action permission false",
            permissions=["submit_line_action_false"],
        )
        def submit_line_action_permission_false(self, request, obj):
            messages.success(
                request,
                "Submit line action with false permission successfully executed",
            )

        @action(
            description="Submit line action with multiple permissions",
            permissions=[
                "submit_line_action_true",
                "submit_line_action_false",
            ],
        )
        def submit_line_action_multiple_different_permissions(self, request, obj):
            messages.success(
                request,
                "Submit line action with multiple different permissions successfully executed",
            )
            return redirect(reverse_lazy("admin:example_user_changelist"))

        def has_submit_line_action_true_permission(self, request, object_id):
            return True

        def has_submit_line_action_false_permission(self, request, object_id):
            return False

    return UserModelAdmin(model=User, admin_site=UnfoldAdminSite())
