from collections.abc import Callable
from typing import Any

from django.db.models import Model, QuerySet
from django.forms import BaseModelFormSet, ModelForm, modelformset_factory

from unfold.forms import PaginationFormSetMixin


class NonrelatedInlineModelFormSet(PaginationFormSetMixin, BaseModelFormSet):
    def __init__(
        self,
        instance: Model | None = None,
        save_as_new: bool = False,
        **kwargs: Any,
    ) -> None:
        self.instance = instance
        super().__init__(**kwargs)
        self.queryset = self.provided_queryset

    @classmethod
    def get_default_prefix(cls: BaseModelFormSet) -> str:
        return f"{cls.model._meta.app_label}-{cls.model._meta.model_name}"

    def save_new(self, form: ModelForm, commit: bool = True):
        obj = super().save_new(form, commit=False)
        self.save_new_instance(self.instance, obj)

        if commit:
            obj.save()

        return obj


def nonrelated_inline_formset_factory(
    model: Model,
    queryset: QuerySet | None = None,
    formset: BaseModelFormSet = NonrelatedInlineModelFormSet,
    save_new_instance: Callable | None = None,
    **kwargs: Any,
) -> BaseModelFormSet:
    inline_formset = modelformset_factory(model, formset=formset, **kwargs)
    inline_formset.provided_queryset = queryset
    inline_formset.save_new_instance = save_new_instance
    return inline_formset
