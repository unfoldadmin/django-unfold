from typing import override

from django.apps import AppConfig


class DefaultAppConfig(AppConfig):
    name = "unfold.contrib.convert"
    label = "unfold_convert"

    @override
    def ready(self) -> None:
        from unfold.contrib.convert.convert_model_admin import (
            convert_model_admin_to_unfold,
        )

        convert_model_admin_to_unfold()
