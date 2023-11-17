window.addEventListener("load", (e) => {
  submitSearch();

  fileInputUpdatePath();

  dateTimeShortcutsOverlay();

  renderCharts();
});

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
    mutations.forEach((mutationRecord) => {
      const display = mutationRecord.target.style.display;
      const overlay = document.getElementById("modal-overlay");

      if (display === "block") {
        overlay.style.display = "block";
      } else {
        overlay.style.display = "none";
      }
    });
  });

  const targets = document.querySelectorAll(".calendarbox, .clockbox");

  Array.from(targets).forEach((target) => {
    observer.observe(target, {
      attributes: true,
      attributeFilter: ["style"],
    });
  });
};

/*************************************************************
 * File upload path
 *************************************************************/
const fileInputUpdatePath = () => {
  Array.from(document.querySelectorAll("input[type=file]")).forEach((input) => {
    input.addEventListener("change", (e) => {
      const parts = e.target.value.split("\\");
      const placeholder =
        input.parentNode.parentNode.querySelector("input[type=text]");
      placeholder.setAttribute("value", parts[parts.length - 1]);
    });
  });
};

/*************************************************************
 * Search form on changelist view
 *************************************************************/
const submitSearch = () => {
  const searchbar = document.getElementById("searchbar");
  const searchbarSubmit = document.getElementById("searchbar-submit");

  if (searchbar !== null) {
    searchbar.addEventListener("keypress", (e) => {
      if (e.key === "Enter") {
        window.location = `?q=${e.target.value}`;
        e.preventDefault();
      } else {
      }
    });
  }

  if (searchbarSubmit !== null && searchbar !== null) {
    searchbarSubmit.addEventListener("click", (e) => {
      e.preventDefault();
      window.location = `?q=${searchbar.value}`;
    });
  }
};

/*************************************************************
 * Chart
 *************************************************************/
const CHART_OPTIONS = {
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
        lineWidth: function (context) {
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
  let charts = [];

  const changeDarkModeSettings = () => {
    const hasDarkClass = document
      .querySelector("html")
      .classList.contains("dark");

    charts.forEach((chart) => {
      chart.options.scales.x.grid.color = hasDarkClass ? "#374151" : "#d1d5db";
      chart.options.scales.y.grid.color = hasDarkClass ? "#374151" : "#d1d5db";
      chart.update();
    });
  };

  Array.from(document.querySelectorAll(".chart")).forEach((chart) => {
    const ctx = chart.getContext("2d");
    const data = chart.dataset.value;
    const type = chart.dataset.type;

    if (!data) {
      return;
    }

    charts.push(
      new Chart(ctx, {
        type: type || "bar",
        data: JSON.parse(chart.dataset.value),
        options: CHART_OPTIONS,
      })
    );
  });

  changeDarkModeSettings();

  watchClassChanges("html", () => {
    changeDarkModeSettings();
  });
};
