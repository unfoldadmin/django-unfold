from collections.abc import Callable
from typing import Any, ClassVar, cast

from django.db.models import Model, QuerySet
from django.forms import BaseModelFormSet, ModelForm, modelformset_factory

from unfold.forms import PaginationFormSetMixin


class NonrelatedInlineModelFormSet(PaginationFormSetMixin, BaseModelFormSet):
    provided_queryset: ClassVar[QuerySet | None] = None
    save_new_instance: ClassVar[Callable | None] = None

    def __init__(
        self,
        instance: Model | None = None,
        save_as_new: bool = False,
        **kwargs: Any,
    ) -> None:
        self.instance = instance
        super().__init__(provided_queryset=self.provided_queryset, **kwargs)

    @classmethod
    def get_default_prefix(cls: type[BaseModelFormSet]) -> str:
        if cls.model is None:
            raise ValueError("Model is not set")

        return f"{cls.model._meta.app_label}-{cls.model._meta.model_name}"

    def save_new(self, form: ModelForm, commit: bool = True):
        obj = super().save_new(form, commit=False)

        if self.instance is None:
            raise ValueError("Instance is not set")

        if self.save_new_instance is None:
            raise ValueError("save_new_instance is not set")

        self.save_new_instance(self.instance, obj)

        if commit:
            obj.save()

        return obj


def nonrelated_inline_formset_factory(
    model: type[Model],
    queryset: QuerySet | None = None,
    formset: type[NonrelatedInlineModelFormSet] = NonrelatedInlineModelFormSet,
    save_new_instance: Callable | None = None,
    **kwargs: Any,
) -> type[NonrelatedInlineModelFormSet]:
    inline_formset = cast(
        type[NonrelatedInlineModelFormSet],
        modelformset_factory(model, formset=formset, **kwargs),
    )

    inline_formset.provided_queryset = queryset
    inline_formset.save_new_instance = save_new_instance
    return inline_formset
