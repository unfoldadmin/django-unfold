document.addEventListener('DOMContentLoaded', function() {
    Array.from(document.getElementsByClassName('admin-numeric-filter-slider')).forEach(function(slider) {
        if (Array.from(slider.classList).includes("noUi-target")) {
            return;
        }

        var from = parseFloat(slider.closest('.admin-numeric-filter-wrapper').querySelectorAll('.admin-numeric-filter-wrapper-group input')[0].value);
        var to = parseFloat(slider.closest('.admin-numeric-filter-wrapper').querySelectorAll('.admin-numeric-filter-wrapper-group input')[1].value);

        noUiSlider.create(slider, {
            start: [from, to],
            step: parseFloat(slider.getAttribute('data-step')),
            connect: true,
            format: wNumb({
                decimals: parseFloat(slider.getAttribute('data-decimals'))
            }),
            range: {
                'min': parseFloat(slider.getAttribute('data-min')),
                'max': parseFloat(slider.getAttribute('data-max'))
            }
        });

        slider.noUiSlider.on('update', function(values, handle) {
            var parent = this.target.closest('.admin-numeric-filter-wrapper');
            var from = parent.querySelectorAll('.admin-numeric-filter-wrapper-group input')[0];
            var to = parent.querySelectorAll('.admin-numeric-filter-wrapper-group input')[1];

            parent.querySelectorAll('.admin-numeric-filter-slider-tooltip-from')[0].innerHTML = values[0];
            parent.querySelectorAll('.admin-numeric-filter-slider-tooltip-to')[0].innerHTML = values[1];

            from.value = values[0];
            to.value = values[1];
        });
    });
});
