window.addEventListener("load", (e) => {
  fileInputUpdatePath();

  dateTimeShortcutsOverlay();

  renderCharts();

  filterForm();

  warnWithoutSaving();
});

/*************************************************************
 * Alpine.sort.js callback after sorting
 *************************************************************/
const sortRecords = (e) => {
  const orderingField = e.from.dataset.orderingField;

  const weightInputs = Array.from(
    e.from.querySelectorAll(`.has_original input[name$=-${orderingField}]`)
  );

  weightInputs.forEach((input, index) => {
    input.value = index;
  });
};

/*************************************************************
 * Warn without saving
 *************************************************************/
const warnWithoutSaving = () => {
  let formChanged = false;
  const form = document.querySelector("form.warn-unsaved-form");

  const checkFormChanged = () => {
    const elements = document.querySelectorAll(
      "form.warn-unsaved-form input, form.warn-unsaved-form select, form.warn-unsaved-form textarea"
    );

    for (const field of elements) {
      field.addEventListener("input", () => {
        formChanged = true;
      });
    }
  };

  if (!form) {
    return;
  }

  new MutationObserver((mutationsList, observer) => {
    checkFormChanged();
  }).observe(form, { attributes: true, childList: true, subtree: true });

  checkFormChanged();

  preventLeaving = (e) => {
    if (formChanged) {
      e.preventDefault();
    }
  };

  form.addEventListener("submit", (e) => {
    window.removeEventListener("beforeunload", preventLeaving);
  });

  window.addEventListener("beforeunload", preventLeaving);
};

/*************************************************************
 * Filter form
 *************************************************************/
const filterForm = () => {
  const filterForm = document.getElementById("filter-form");

  if (!filterForm) {
    return;
  }

  filterForm.addEventListener("formdata", (event) => {
    Array.from(event.formData.entries()).forEach(([key, value]) => {
      if (value === "") event.formData.delete(key);
    });
  });
};

/*************************************************************
 * Class watcher
 *************************************************************/
const watchClassChanges = (selector, callback) => {
  const body = document.querySelector(selector);

  const observer = new MutationObserver((mutationsList) => {
    for (const mutation of mutationsList) {
      if (
        mutation.type === "attributes" &&
        mutation.attributeName === "class"
      ) {
        callback();
      }
    }
  });

  observer.observe(body, { attributes: true, attributeFilter: ["class"] });
};

/*************************************************************
 * Calendar & clock
 *************************************************************/
const dateTimeShortcutsOverlay = () => {
  const observer = new MutationObserver((mutations) => {
    for (const mutationRecord of mutations) {
      const display = mutationRecord.target.style.display;
      const overlay = document.getElementById("modal-overlay");

      if (display === "block") {
        overlay.style.display = "block";
      } else {
        overlay.style.display = "none";
      }
    }
  });

  const targets = document.querySelectorAll(".calendarbox, .clockbox");

  for (const target of targets) {
    observer.observe(target, {
      attributes: true,
      attributeFilter: ["style"],
    });
  }
};

/*************************************************************
 * File upload path
 *************************************************************/
const fileInputUpdatePath = () => {
  const checkInputChanged = () => {
    for (const input of document.querySelectorAll("input[type=file]")) {
      if (input.hasChangeListener) {
        continue;
      }

      input.addEventListener("change", (e) => {
        const parts = e.target.value.split("\\");
        const placeholder =
          input.parentNode.parentNode.parentNode.querySelector(
            "input[type=text]"
          );
        placeholder.setAttribute("value", parts[parts.length - 1]);
      });

      input.hasChangeListener = true;
    }
  };

  new MutationObserver(() => {
    checkInputChanged();
  }).observe(document.body, {
    childList: true,
    subtree: true,
  });

  checkInputChanged();
};

/*************************************************************
 * Chart
 *************************************************************/
const DEFAULT_CHART_OPTIONS = {
  animation: false,
  barPercentage: 1,
  base: 0,
  grouped: false,
  maxBarThickness: 4,
  responsive: true,
  maintainAspectRatio: false,
  datasets: {
    bar: {
      borderRadius: 12,
      border: {
        width: 0,
      },
      borderSkipped: "middle",
    },
    line: {
      borderWidth: 2,
      pointBorderWidth: 0,
      pointStyle: false,
    },
  },
  plugins: {
    legend: {
      align: "end",
      display: false,
      position: "top",
      labels: {
        boxHeight: 5,
        boxWidth: 5,
        color: "#9ca3af",
        pointStyle: "circle",
        usePointStyle: true,
      },
    },
    tooltip: {
      enabled: true,
    },
  },
  scales: {
    x: {
      border: {
        dash: [5, 5],
        dashOffset: 2,
        width: 0,
      },
      ticks: {
        color: "#9ca3af",
        display: true,
      },
      grid: {
        display: true,
        tickWidth: 0,
      },
    },
    y: {
      border: {
        dash: [5, 5],
        dashOffset: 5,
        width: 0,
      },
      ticks: {
        display: false,
        font: {
          size: 13,
        },
      },
      grid: {
        lineWidth: (context) => {
          if (context.tick.value === 0) {
            return 1;
          }
          return 0;
        },
        tickWidth: 0,
      },
    },
  },
};

const renderCharts = () => {
  const charts = [];

  const changeDarkModeSettings = () => {
    const hasDarkClass = document
      .querySelector("html")
      .classList.contains("dark");

    const baseColorDark = getComputedStyle(document.documentElement)
      .getPropertyValue("--color-base-700")
      .trim();

    const baseColorLight = getComputedStyle(document.documentElement)
      .getPropertyValue("--color-base-300")
      .trim();

    const borderColor = hasDarkClass
      ? `rgb(${baseColorDark})`
      : `rgb(${baseColorLight})`;

    for (const chart of charts) {
      chart.options.scales.x.grid.color = borderColor;
      chart.options.scales.y.grid.color = borderColor;
      chart.update();
    }
  };

  for (const chart of document.querySelectorAll(".chart")) {
    const ctx = chart.getContext("2d");
    const data = chart.dataset.value;
    const type = chart.dataset.type;
    const options = chart.dataset.options;

    if (!data) {
      continue;
    }

    const parsedData = JSON.parse(chart.dataset.value);

    for (const key in parsedData.datasets) {
      const dataset = parsedData.datasets[key];
      const processColor = (colorProp) => {
        if (dataset?.[colorProp]?.startsWith("var(")) {
          const cssVar = dataset[colorProp].match(/var\((.*?)\)/)[1];
          const color = getComputedStyle(document.documentElement)
            .getPropertyValue(cssVar)
            .trim();
          dataset[colorProp] = `rgb(${color})`;
        }
      };

      processColor("borderColor");
      processColor("backgroundColor");
    }

    charts.push(
      new Chart(ctx, {
        type: type || "bar",
        data: parsedData,
        options: options ? JSON.parse(options) : DEFAULT_CHART_OPTIONS,
      })
    );
  }

  changeDarkModeSettings();

  watchClassChanges("html", () => {
    changeDarkModeSettings();
  });
};
