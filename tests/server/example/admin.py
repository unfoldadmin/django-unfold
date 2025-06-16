from django.contrib import admin, messages
from django.contrib.auth.admin import GroupAdmin as BaseGroupAdmin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group
from django.shortcuts import redirect
from django.urls import reverse_lazy

from unfold.admin import ModelAdmin, StackedInline
from unfold.decorators import action
from unfold.forms import AdminPasswordChangeForm, UserChangeForm, UserCreationForm
from unfold.sections import TableSection, TemplateSection

from .models import ActionUser, SectionUser, Tag, User

admin.site.unregister(Group)


class UserTagInline(StackedInline):
    model = User.tags.through
    per_page = 1
    collapsible = True


@admin.register(User)
class UserAdmin(BaseUserAdmin, ModelAdmin):
    form = UserChangeForm
    add_form = UserCreationForm
    change_password_form = AdminPasswordChangeForm
    inlines = [UserTagInline]


class RelatedTableSection(TableSection):
    verbose_name = "Related log entries"
    related_name = "logentry_set"
    columns = [
        "object_id",
    ]


class SomeTemplateSection(TemplateSection):
    template_name = "section_template.html"


@admin.register(SectionUser)
class SectionUserAdmin(UserAdmin):
    form = UserChangeForm
    add_form = UserCreationForm
    change_password_form = AdminPasswordChangeForm
    list_sections = [
        SomeTemplateSection,
        RelatedTableSection,
    ]


@admin.register(ActionUser)
class ActionsUserAdmin(BaseUserAdmin, ModelAdmin):
    form = UserChangeForm
    add_form = UserCreationForm
    change_password_form = AdminPasswordChangeForm
    actions_list = [
        "changelist_action",
        "changelist_action_mixed_permissions_true",
        "changelist_action_mixed_permissions_false",
        "changelist_action_mixed_permissions_perm_not_granted",
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
        "changelist_row_action_mixed_permissions_true",
        "changelist_row_action_mixed_permissions_false",
        "changelist_row_action_mixed_permissions_perm_not_granted",
        "changelist_row_action_permission_true",
        "changelist_row_action_permission_false",
        "changelist_row_action_multiple_different_permissions",
    ]
    actions_detail = [
        "changeform_action",
        "changeform_action_mixed_permissions_true",
        "changeform_action_mixed_permissions_false",
        "changeform_action_mixed_permissions_perm_not_granted",
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
        "submit_line_action_mixed_permissions_true",
        "submit_line_action_mixed_permissions_false",
        "submit_line_action_mixed_permissions_perm_not_granted",
        "submit_line_action_permission_true",
        "submit_line_action_permission_false",
        "submit_line_action_multiple_different_permissions",
    ]

    ######################################################################
    # Changelist actions
    ######################################################################
    @action(description="Changelist action dropdown")
    def changelist_action_dropdown(self, request):
        messages.success(request, "Changelist action dropdown successfully executed")
        return redirect(reverse_lazy("admin:example_user_changelist"))

    @action(description="Changelist action")
    def changelist_action(self, request):
        messages.success(request, "Changelist action successfully executed")
        return redirect(reverse_lazy("admin:example_user_changelist"))

    @action(
        description="Changelist action with mixed permissions true",
        permissions=["changelist_action_true", "example.view_user"],
    )
    def changelist_action_mixed_permissions_true(self, request):
        messages.success(
            request,
            "Changelist action with mixed permissions true successfully executed",
        )
        return redirect(reverse_lazy("admin:example_user_changelist"))

    @action(
        description="Changelist action with mixed permissions false",
        permissions=["changelist_action_false", "example.view_user"],
    )
    def changelist_action_mixed_permissions_false(self, request):
        messages.success(
            request,
            "Changelist action with mixed permissions false successfully executed",
        )
        return redirect(reverse_lazy("admin:example_user_changelist"))

    @action(
        description="Changelist action with mixed permissions perm not granted",
        permissions=["changelist_action_true", "example.delete_user"],
    )
    def changelist_action_mixed_permissions_perm_not_granted(self, request):
        messages.success(
            request,
            "Changelist action with mixed permissions perm not granted successfully executed",
        )
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
        description="Changelist row action with mixed permissions true",
        permissions=["changelist_row_action_true", "example.view_user"],
    )
    def changelist_row_action_mixed_permissions_true(self, request, object_id):
        messages.success(
            request,
            "Changelist row action with mixed permissions true successfully executed",
        )
        return redirect(reverse_lazy("admin:example_user_changelist"))

    @action(
        description="Changelist row action with mixed permissions false",
        permissions=["changelist_row_action_false", "example.view_user"],
    )
    def changelist_row_action_mixed_permissions_false(self, request, object_id):
        messages.success(
            request,
            "Changelist row action with mixed permissions false successfully executed",
        )
        return redirect(reverse_lazy("admin:example_user_changelist"))

    @action(
        description="Changelist row action with mixed permissions perm not granted",
        permissions=["changelist_row_action_true", "example.delete_user"],
    )
    def changelist_row_action_mixed_permissions_perm_not_granted(
        self, request, object_id
    ):
        messages.success(
            request,
            "Changelist row action with mixed permissions perm not granted successfully executed",
        )
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
    def changelist_row_action_multiple_different_permissions(self, request, object_id):
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
    @action(
        description="Changeform action dropdown",
        permissions=["changeform_action_dropdown"],
    )
    def changeform_action_dropdown(self, request, object_id):
        messages.success(request, "Changeform action dropdown successfully executed")
        return redirect(reverse_lazy("admin:example_user_changelist"))

    def has_changeform_action_dropdown_permission(self, request, object_id):
        return True

    @action(
        description="Changeform action with mixed permissions true",
        permissions=["example.view_user", "changeform_action_true"],
    )
    def changeform_action_mixed_permissions_true(self, request, object_id):
        messages.success(
            request,
            "Changeform action with mixed permissions true successfully executed",
        )
        return redirect(reverse_lazy("admin:example_user_changelist"))

    @action(
        description="Changeform action with mixed permissions false",
        permissions=["example.view_user", "changeform_action_false"],
    )
    def changeform_action_mixed_permissions_false(self, request, object_id):
        messages.success(
            request,
            "Changeform action with mixed permissions false successfully executed",
        )
        return redirect(reverse_lazy("admin:example_user_changelist"))

    @action(
        description="Changeform action with mixed permissions perm not granted",
        permissions=["example.delete_user", "changeform_action_true"],
    )
    def changeform_action_mixed_permissions_perm_not_granted(self, request, object_id):
        messages.success(
            request,
            "Changeform action with mixed permissions perm not granted successfully executed",
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
        description="Submit line action with mixed permissions true",
        permissions=["submit_line_action_true", "example.view_user"],
    )
    def submit_line_action_mixed_permissions_true(self, request, obj):
        messages.success(
            request,
            "Submit line action with mixed permissions true successfully executed",
        )
        return redirect(reverse_lazy("admin:example_user_changelist"))

    @action(
        description="Submit line action with mixed permissions false",
        permissions=["submit_line_action_false", "example.view_user"],
    )
    def submit_line_action_mixed_permissions_false(self, request, obj):
        messages.success(
            request,
            "Submit line action with mixed permissions false successfully executed",
        )
        return redirect(reverse_lazy("admin:example_user_changelist"))

    @action(
        description="Submit line action with mixed permissions perm not granted",
        permissions=["submit_line_action_true", "example.delete_user"],
    )
    def submit_line_action_mixed_permissions_perm_not_granted(self, request, obj):
        messages.success(
            request,
            "Submit line action with mixed permissions perm not granted successfully executed",
        )
        return redirect(reverse_lazy("admin:example_user_changelist"))

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


@admin.register(Group)
class GroupAdmin(BaseGroupAdmin, ModelAdmin):
    pass


@admin.register(Tag)
class TagAdmin(ModelAdmin):
    pass
