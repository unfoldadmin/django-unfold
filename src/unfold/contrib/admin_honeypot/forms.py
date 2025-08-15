from django import forms

from unfold.forms import AuthenticationForm


class HoneypotLoginForm(AuthenticationForm):
    def clean(self):
        """
        Always raise the default error message, because we don't
        care what they entered here.
        """
        raise forms.ValidationError(
            self.error_messages["invalid_login"],
            code="invalid_login",
            params={"username": self.username_field.verbose_name},
        )
