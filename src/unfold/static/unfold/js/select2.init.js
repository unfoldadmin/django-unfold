{
	const $ = django.jQuery;

	$.fn.djangoCustomSelect2 = function () {
		$.each(this, (_index, element) => {
			if (element.id.match(/__prefix__/)) {
				return;
			}

			if ($(element).hasClass("select2-hidden-accessible")) {
				return;
			}

			$(element).select2();
		});

		return this;
	};

	$.fn.djangoFilterSelect2 = function () {
		$.each(this, (_index, element) => {
			const formParent = this.closest('#filter-form');

			$(element).select2({
				closeOnSelect: !element.multiple,
				...(formParent.length ? { dropdownParent: formParent } : {}),
				ajax: {
					data: (params) => {
						return {
							term: params.term,
							page: params.page,
							app_label: element.dataset.appLabel,
							model_name: element.dataset.modelName,
							field_name: element.dataset.fieldName,
						};
					},
				},
			});
		});

		return this;
	};

	$(() => {
		$(".unfold-admin-autocomplete").djangoCustomSelect2();

		$(".unfold-filter-autocomplete").djangoFilterSelect2();

		document.addEventListener("formset:added", (event) => {
			$(event.target).find(".unfold-admin-autocomplete").djangoCustomSelect2();
		});
	});
}
