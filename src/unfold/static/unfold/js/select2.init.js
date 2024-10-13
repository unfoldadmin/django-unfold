"use strict";
{
  const $ = django.jQuery;

  $.fn.djangoCustomSelect2 = function () {
    $.each(this, function (i, element) {
      $(element).select2();
    });
    return this;
  };

  $(function () {
    $(".unfold-admin-autocomplete.admin-autocomplete").djangoCustomSelect2();
  });
}
