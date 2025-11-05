"use strict";
{
  const $ = django.jQuery;

  $.fn.djangoCustomSelect2 = function () {
    $.each(this, function (i, element) {
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
    $.each(this, function (i, element) {
      $(element).select2({
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

  $(function () {
    $(".unfold-admin-autocomplete").djangoCustomSelect2();

    $(".unfold-filter-autocomplete").djangoFilterSelect2();
  });
}
