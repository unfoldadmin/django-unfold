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
    $(".admin-autocomplete").djangoCustomSelect2();
  });
}
