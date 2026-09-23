from typing import Any

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Fieldset, Layout
from django import forms
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

from unfold.layout import Button, FieldsetSubheader, Hr, Submit
from unfold.widgets import (
    UnfoldAdminCheckboxSelectMultipleWidget,
    UnfoldAdminDateWidget,
    UnfoldAdminEmailInputWidget,
    UnfoldAdminExpandableTextareaWidget,
    UnfoldAdminFileFieldWidget,
    UnfoldAdminImageFieldWidget,
    UnfoldAdminIntegerFieldWidget,
    UnfoldAdminMoneyWidget,
    UnfoldAdminRadioSelectWidget,
    UnfoldAdminSelect2Widget,
    UnfoldAdminSelectMultipleWidget,
    UnfoldAdminSplitDateTimeWidget,
    UnfoldAdminTextareaWidget,
    UnfoldAdminTextInputWidget,
    UnfoldAdminTimeWidget,
    UnfoldAdminURLInputWidget,
    UnfoldBooleanSwitchWidget,
    UnfoldBooleanWidget,
)

User = get_user_model()


class CrispyForm(forms.Form):
    name = forms.CharField(
        max_length=100,
        label=_("Name"),
        required=True,
        widget=UnfoldAdminTextInputWidget(),
    )
    email = forms.EmailField(
        label=_("Email"),
        required=True,
        widget=UnfoldAdminEmailInputWidget(),
    )
    age = forms.IntegerField(
        label=_("Age"),
        required=True,
        min_value=18,
        max_value=120,
        widget=UnfoldAdminIntegerFieldWidget(),
    )
    url = forms.URLField(
        label=_("URL"),
        required=True,
        widget=UnfoldAdminURLInputWidget(),
    )
    salary = forms.DecimalField(
        label=_("Salary"),
        required=True,
        help_text=_("Enter your salary"),
        widget=UnfoldAdminMoneyWidget(),
    )
    title = forms.CharField(
        label=_("Title"),
        required=True,
        widget=UnfoldAdminExpandableTextareaWidget(),
    )
    message = forms.CharField(
        label=_("Message"),
        required=True,
        widget=UnfoldAdminTextareaWidget(),
    )
    subscribe = forms.BooleanField(
        label=_("Subscribe to newsletter"),
        required=True,
        initial=True,
        help_text=_("Toggle to receive our newsletter with updates and offers"),
        widget=UnfoldBooleanSwitchWidget,
    )
    notifications = forms.BooleanField(
        label=_("Receive notifications"),
        required=True,
        initial=False,
        help_text=_("Toggle to receive notifications about your inquiry status"),
        widget=UnfoldBooleanWidget,
    )
    department = forms.ChoiceField(
        label=_("Department"),
        choices=[
            ("sales", _("Sales")),
            ("marketing", _("Marketing")),
            ("development", _("Development")),
            ("hr", _("Human Resources")),
            ("other", _("Other")),
        ],
        required=True,
        help_text=_("Select the department to contact"),
        widget=UnfoldAdminRadioSelectWidget,
    )
    category = forms.ChoiceField(
        label=_("Category"),
        choices=[
            ("general", _("General Inquiry")),
            ("support", _("Technical Support")),
            ("feedback", _("Feedback")),
            ("other", _("Other")),
        ],
        required=True,
        help_text=_("Select the category of your message"),
        widget=UnfoldAdminCheckboxSelectMultipleWidget,
    )
    priority = forms.TypedChoiceField(
        label=_("Priority"),
        choices=[
            (1, _("Low")),
            (2, _("Medium")),
            (3, _("High")),
        ],
        coerce=int,
        required=True,
        initial=2,
        help_text=_("Select the priority of your message"),
        widget=UnfoldAdminSelect2Widget,
    )
    multi_select = forms.MultipleChoiceField(
        label=_("Select Multiple Options"),
        choices=[
            (
                "option_a",
                _(
                    "Option A – Receive timely updates on race schedules, driver announcements, and changes in race venues throughout the season."
                ),
            ),
            (
                "option_b",
                _(
                    "Option B – Get exclusive insights into detailed team strategies, pit stop analytics, and pre-race analyses from experts."
                ),
            ),
            (
                "option_c",
                _(
                    "Option C – Access extensive behind-the-scenes footage, in-depth interviews with top drivers, and special team documentaries."
                ),
            ),
            (
                "option_d",
                _(
                    "Option D – Join VIP events and participate in interactive fan voting for awards with additional community activities."
                ),
            ),
            (
                "option_e",
                _(
                    "Option E – Subscribe to technical analysis, expert commentary, and comprehensive engineering breakdowns of the latest F1 cars."
                ),
            ),
            (
                "option_f",
                _(
                    "Option F – Be the first to know about special promotions, early bird ticket sales, and new official merchandise launches."
                ),
            ),
            (
                "option_g",
                _(
                    "Option G – Receive personalized notifications about your favorite teams, their race results, and tailored race-day summaries."
                ),
            ),
            (
                "option_h",
                _(
                    "Option H – Get early access to new platform features, closed beta program invitations, and direct feedback opportunities."
                ),
            ),
        ],
        required=False,
        help_text=_("You can select more than one option"),
        widget=UnfoldAdminSelectMultipleWidget,
    )
    date = forms.DateField(
        label=_("Date"),
        required=True,
        widget=UnfoldAdminDateWidget,
    )
    time = forms.TimeField(
        label=_("Time"),
        required=True,
        widget=UnfoldAdminTimeWidget,
    )
    datetime = forms.SplitDateTimeField(
        label=_("Date and Time"),
        required=True,
        widget=UnfoldAdminSplitDateTimeWidget,
    )
    file = forms.FileField(
        label=_("File"),
        required=True,
        widget=UnfoldAdminFileFieldWidget,
    )
    image = forms.ImageField(
        label=_("Image"),
        required=True,
        widget=UnfoldAdminImageFieldWidget,
    )

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_class = "form-horizontal"
        self.helper.add_input(Submit("submit", _("Submit")))
        self.helper.add_input(Submit("submit", _("Submit 2")))
        self.helper.add_input(Button("submit", _("Submit 3"), css_class="bg-red-500"))
        self.helper.attrs = {
            "novalidate": "novalidate",
        }
        self.helper.layout = Layout(
            Fieldset(
                _("Custom horizontal form"),
                "name",
                "email",
                "age",
                "url",
                "salary",
                FieldsetSubheader(_("Another header")),
                "title",
                "message",
                "subscribe",
                css_class="mb-4",
            ),
            Hr(),
            Fieldset(
                _("Another horizontal form"),
                "subscribe",
                "notifications",
                "department",
                "category",
                "date",
                "time",
                "datetime",
                css_class="mb-4",
            ),
        )
