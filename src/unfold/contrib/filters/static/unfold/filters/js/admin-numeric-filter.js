document.addEventListener("DOMContentLoaded", function () {
  Array.from(
    document.getElementsByClassName("admin-numeric-filter-slider")
  ).forEach(function (slider) {
    if (Array.from(slider.classList).includes("noUi-target")) {
      return;
    }

    const fromInput = slider
      .closest(".admin-numeric-filter-wrapper")
      .querySelectorAll(".admin-numeric-filter-wrapper-group input")[0];

    const toInput = slider
      .closest(".admin-numeric-filter-wrapper")
      .querySelectorAll(".admin-numeric-filter-wrapper-group input")[1];

    noUiSlider.create(slider, {
      start: [parseFloat(fromInput.value), parseFloat(toInput.value)],
      step: parseFloat(slider.getAttribute("data-step")),
      connect: true,
      format: wNumb({
        decimals: parseFloat(slider.getAttribute("data-decimals")),
      }),
      range: {
        min: parseFloat(slider.getAttribute("data-min")),
        max: parseFloat(slider.getAttribute("data-max")),
      },
    });

    /*************************************************************
     * Update slider when input values change
     *************************************************************/
    fromInput.addEventListener("keyup", function () {
      clearTimeout(this._sliderUpdateTimeout);
      this._sliderUpdateTimeout = setTimeout(() => {
        slider.noUiSlider.set([
          parseFloat(this.value),
          parseFloat(toInput.value),
        ]);
      }, 500);
    });

    toInput.addEventListener("keyup", function () {
      clearTimeout(this._sliderUpdateTimeout);
      this._sliderUpdateTimeout = setTimeout(() => {
        slider.noUiSlider.set([
          parseFloat(fromInput.value),
          parseFloat(this.value),
        ]);
      }, 500);
    });

    /*************************************************************
     * Updated inputs when slider is moved
     *************************************************************/
    slider.noUiSlider.on("update", function (values, handle) {
      const parent = this.target.closest(".admin-numeric-filter-wrapper");
      const from = parent.querySelectorAll(
        ".admin-numeric-filter-wrapper-group input"
      )[0];
      const to = parent.querySelectorAll(
        ".admin-numeric-filter-wrapper-group input"
      )[1];

      from.value = values[0];
      to.value = values[1];
    });
  });
});
