window.addEventListener("load", () => {
	fileInputUpdatePath();

	dateTimeShortcutsOverlay();

	renderCharts();

	filterForm();

	warnWithoutSaving();

	inlines();

	tabNavigation();

	scrollSidebarNav();

	crispyFormset();
});

function getCurrentTab() {
	const fragment = window.location.hash?.replace("#", "");

	if (!fragment) {
		return null;
	}

	if (!document.getElementById(`${fragment}-group`)) {
		return null;
	}

	return fragment;
}

/*************************************************************
 * Switch theme
 *************************************************************/
function theme(defaultTheme = "auto") {
	return {
		sidebarWidth: localStorage.getItem("sidebarWidth") || 288,
		sidebarOpen() {
			if (window.innerWidth <= 1280) {
				return false;
			} else {
				const sidebarOpenValue = localStorage.getItem("sidebarOpen");

				if (sidebarOpenValue === null) {
					return true;
				}
				return sidebarOpenValue !== "0";
			}
		},
		sidebarToggle() {
			this.sidebarOpen = !this.sidebarOpen;

			if (window.innerWidth > 1280) {
				localStorage.setItem("sidebarOpen", this.sidebarOpen ? "1" : "0");
			}
		},
		openModal: false,
		filterOpen: false,
		openAllApplications: false,
		adminTheme: Alpine.$persist(defaultTheme).as("adminTheme"),
		init() {
			this.$watch("openModal", (value) => {
				if (value) {
					document
						.getElementsByTagName("body")[0]
						.classList.add("overflow-hidden");
				} else {
					document
						.getElementsByTagName("body")[0]
						.classList.remove("overflow-hidden");
				}
			});

			this.$watch("filterOpen", (value) => {
				if (value) {
					document
						.getElementsByTagName("body")[0]
						.classList.add("overflow-hidden");
				} else {
					document
						.getElementsByTagName("body")[0]
						.classList.remove("overflow-hidden");
				}
			});

			this.$watch("openAllApplications", (value) => {
				if (value) {
					document
						.getElementsByTagName("body")[0]
						.classList.add("overflow-hidden");
				} else {
					document
						.getElementsByTagName("body")[0]
						.classList.remove("overflow-hidden");
				}
			});
		},
		switchTheme(theme) {
			this.adminTheme = theme;
		},
		themeBindings: {
			["x-resize.window"]() {
				if (window.innerWidth <= 1280) {
					this.sidebarOpen = false;
				} else {
					this.sidebarOpen =
						localStorage.getItem("sidebarOpen") === "0" ? false : true;
				}
			},
			["x-bind:class"]() {
				if (
					this.adminTheme === "dark" ||
					(this.adminTheme === "auto" &&
						window.matchMedia("(prefers-color-scheme: dark)").matches)
				) {
					return "dark";
				}

				if (this.adminTheme === "light") {
					return "light";
				}

				return "";
			},
			["x-on:keydown.window"](event) {
				const isInput =
					document.activeElement.tagName.toLowerCase() === "input" ||
					document.activeElement.tagName.toLowerCase() === "textarea" ||
					document.activeElement.isContentEditable;

				if (isInput) {
					return;
				}

				if (!event.metaKey && !event.ctrlKey && event.key === "[") {
					event.preventDefault();
					this.sidebarToggle();
				}

				if (!event.metaKey && !event.ctrlKey && event.key === "f") {
					const filterOpenButton = document.querySelector(
						".filter-open-button",
					);

					if (filterOpenButton) {
						this.filterOpen = !this.filterOpen;
					}
				}

				if (!event.metaKey && !event.ctrlKey && event.key === "c") {
					const addLink = document.querySelector(".addlink");

					if (addLink) {
						addLink.click();
					}
				}

				if ((event.metaKey || event.ctrlKey) && event.key === "e") {
					event.preventDefault();

					if (this.adminTheme === "light") {
						this.adminTheme = "dark";
					} else {
						this.adminTheme = "light";
					}
				}
			},
		},
	};
}

/*************************************************************
 * Scroll sidebar to active item
 *************************************************************/
function scrollSidebarNav() {
	const sidebarNav = document.getElementById("nav-sidebar-apps");

	if (!sidebarNav) {
		return;
	}

	const instance = SimpleBar.instances.get(sidebarNav);
	const activeItem = sidebarNav.querySelector("a.active");

	if (!instance || !activeItem) {
		return;
	}

	function isActiveItemVisible() {
		const sidebarRect = sidebarNav.getBoundingClientRect();
		const itemRect = activeItem.getBoundingClientRect();

		return (
			itemRect.top >= sidebarRect.top && itemRect.bottom <= sidebarRect.bottom
		);
	}

	if (instance && !isActiveItemVisible()) {
		instance.getScrollElement().scroll(0, activeItem.offsetTop);
	}
}

/*************************************************************
 * Move not visible tab items to dropdown
 *************************************************************/
function tabNavigation() {
	const itemsDropdown = document.getElementById("tabs-dropdown");
	const itemsList = document.getElementById("tabs-items");
	const widths = [];

	if (!itemsDropdown || !itemsList) {
		return;
	}

	handleTabNavigationResize();

	window.addEventListener("resize", () => {
		handleTabNavigationResize();
	});

	function handleTabNavigationResize() {
		const contentWidth = document.getElementById("content").offsetWidth;
		const tabsWidth = document.getElementById("tabs-wrapper").scrollWidth;
		const availableWidth =
			itemsList.parentElement.offsetWidth - itemsList.offsetWidth - 48;

		if (tabsWidth > contentWidth) {
			const lastTabItem = itemsList ? itemsList.lastElementChild : null;

			if (lastTabItem) {
				widths.push(lastTabItem.offsetWidth);
				itemsList.removeChild(lastTabItem);
				itemsDropdown.appendChild(lastTabItem);

				// If there is still not enough space, move the last item to the dropdown again
				if (
					document.getElementById("content").offsetWidth <
					document.getElementById("tabs-wrapper").scrollWidth
				) {
					handleTabNavigationResize();
				}
			}
		} else if (
			widths.length > 0 &&
			widths[widths.length - 1] < availableWidth
		) {
			const lastTabItem = itemsDropdown ? itemsDropdown.lastElementChild : null;

			if (lastTabItem) {
				itemsDropdown.removeChild(lastTabItem);
				itemsList.appendChild(lastTabItem);
				widths.pop();
			}
		}

		// Show/hide dropdown based on the number of items in dropdown
		if (itemsDropdown.childElementCount === 0) {
			itemsDropdown.parentElement.classList.add("hidden");
		} else {
			itemsDropdown.parentElement.classList.remove("hidden");
		}
	}
}

/*************************************************************
 * Alpine.sort.js callback after sorting
 *************************************************************/
function sortRecords(e) {
	e.from.querySelectorAll(`.form-group.original`).forEach((row, index) => {
		input = row.querySelector(`input[name$=-${e.from.dataset.orderingField}]`);
		input.value = index;
	});

	e.from
		.querySelectorAll(
			`td.field-${e.from.dataset.orderingField} input[name$=-${e.from.dataset.orderingField}]`,
		)
		.forEach((input, index) => {
			input.value = index;
		});
}

/*************************************************************
 * Alpine.sort.js callback before moving records
 *************************************************************/
const moveRecords = (e) => {
	if (
		(e.related.classList.contains("template") ||
			e.related.classList.contains("form-actions")) &&
		e.willInsertAfter
	) {
		return false;
	}
};

/*************************************************************
 * Search form
 *************************************************************/
function searchForm() {
	return {
		applyShortcut(event) {
			if (
				event.key === "/" &&
				document.activeElement.tagName.toLowerCase() !== "input" &&
				document.activeElement.tagName.toLowerCase() !== "textarea" &&
				!document.activeElement.isContentEditable
			) {
				event.preventDefault();
				this.$refs.searchInput.focus();
			}
		},
	};
}

/*************************************************************
 * Search command
 *************************************************************/
function searchCommand() {
	return {
		el: document.getElementById("command-results"),
		items: undefined,
		totalItems: 0,
		currentIndex: 0,
		hasResponse: false,
		openCommandResults: false,
		searchTerm: "",
		commandHistory: JSON.parse(localStorage.getItem("commandHistory") || "[]"),
		handleOpen() {
			this.openCommandResults = true;
			this.toggleBodyOverflow();
			setTimeout(() => {
				this.$refs.searchInputCommand.focus();
			}, 20);

			this.items = document.querySelectorAll("#command-history li");
			this.totalItems = this.items.length;
		},
		handleShortcut(event) {
			if (
				event.key === "k" &&
				(event.metaKey || event.ctrlKey) &&
				document.activeElement.tagName.toLowerCase() !== "input" &&
				document.activeElement.tagName.toLowerCase() !== "textarea" &&
				!document.activeElement.isContentEditable
			) {
				event.preventDefault();
				this.handleOpen();
			}
		},
		handleClear() {
			if (this.$refs.searchInputCommand.value === "") {
				this.toggleBodyOverflow();
				this.openCommandResults = false;
				this.el.innerHTML = "";
				this.searchTerm = "";
				this.items = undefined;
				this.totalItems = 0;
				this.currentIndex = 0;
			} else {
				this.$refs.searchInputCommand.value = "";
			}
		},
		handleOutsideClick() {
			this.toggleBodyOverflow();
			this.$refs.searchInputCommand.value = "";
			this.searchTerm = "";
			this.openCommandResults = false;
			this.items = undefined;
			this.totalItems = 0;
			this.currentIndex = 0;
		},
		handleContentLoaded(event) {
			if (
				event.target.id !== "command-results" &&
				event.target.id !== "command-results-list"
			) {
				return;
			}

			this.hasResponse = event.detail.xhr.response.length > 0;

			const commandResultsList = document.getElementById(
				"command-results-list",
			);

			if (commandResultsList) {
				this.items = commandResultsList.querySelectorAll("li");
				this.totalItems = this.items.length;
			} else {
				this.items = undefined;
				this.totalItems = 0;
			}

			if (event.target.id === "command-results") {
				this.currentIndex = 0;

				if (this.items) {
					this.totalItems = this.items.length;
				} else {
					this.totalItems = 0;
				}
			}

			if (!this.hasResponse && this.commandHistory.length > 0) {
				this.currentIndex = 0;
				this.items = document.querySelectorAll("#command-history li");
				this.totalItems = this.items.length;
				document.getElementById("command-results-note").innerHTML = "";
			}

			this.searchTerm = this.$refs.searchInputCommand.value;
		},
		toggleBodyOverflow() {
			document
				.getElementsByTagName("body")[0]
				.classList.toggle("overflow-hidden");
		},
		scrollToActiveItem() {
			const item = this.items[this.currentIndex - 1];

			if (item) {
				item.scrollIntoView({
					behavior: "smooth",
					block: "nearest",
				});
			}
		},
		nextItem() {
			if (this.currentIndex < this.totalItems) {
				this.currentIndex++;
				this.scrollToActiveItem();
			}
		},
		prevItem() {
			if (this.currentIndex > 1) {
				this.currentIndex--;
				this.scrollToActiveItem();
			}
		},
		selectItem(addHistory, openInNewTab = false) {
			const link = this.items[this.currentIndex - 1].querySelector("a");
			const data = {
				title: link.dataset.title,
				description: link.dataset.description,
				link: link.href,
				favorite: false,
			};

			if (addHistory) {
				this.addToHistory(data);
			}

			if (openInNewTab) {
				window.open(link.href, "_blank");
			} else {
				window.location = link.href;
			}
		},
		addToHistory(data) {
			let commandHistory = JSON.parse(
				localStorage.getItem("commandHistory") || "[]",
			);

			for (const [index, item] of commandHistory.entries()) {
				if (item.link === data.link) {
					commandHistory.splice(index, 1);
				}
			}

			commandHistory.unshift(data);
			commandHistory = commandHistory.slice(0, 10);
			this.commandHistory = commandHistory;
			localStorage.setItem("commandHistory", JSON.stringify(commandHistory));
		},
		removeFromHistory(event, index) {
			event.preventDefault();

			const commandHistory = JSON.parse(
				localStorage.getItem("commandHistory") || "[]",
			);
			commandHistory.splice(index, 1);
			this.commandHistory = commandHistory;
			localStorage.setItem("commandHistory", JSON.stringify(commandHistory));
		},
		toggleFavorite(event, index) {
			event.preventDefault();

			const commandHistory = JSON.parse(
				localStorage.getItem("commandHistory") || "[]",
			);

			commandHistory[index].favorite = !commandHistory[index].favorite;
			this.commandHistory = commandHistory.sort(
				(a, b) => Number(b.favorite) - Number(a.favorite),
			);
			localStorage.setItem("commandHistory", JSON.stringify(commandHistory));
		},
	};
}

/*************************************************************
 * Warn without saving
 *************************************************************/
const warnWithoutSaving = () => {
	let formChanged = false;
	const form = document.querySelector("form.warn-unsaved-form");

	const checkFormChanged = () => {
		const elements = document.querySelectorAll(
			"form.warn-unsaved-form input, form.warn-unsaved-form select, form.warn-unsaved-form textarea",
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
function dateTimeShortcutsOverlay() {
	const observer = new MutationObserver((mutations) => {
		for (const mutationRecord of mutations) {
			const display = mutationRecord.target.style.display;
			const hasOpenAttribute = mutationRecord.target.hasAttribute("open");
			const overlay = document.getElementById("modal-overlay");

			if (display === "block" || hasOpenAttribute) {
				overlay.style.display = "block";
			} else {
				overlay.style.display = "none";
			}
		}
	});

	const findCalendars = () => {
		for (const target of document.querySelectorAll(".calendarbox, .clockbox")) {
			observer.observe(target, {
				attributes: true,
				attributeFilter: ["style", "open"],
			});
		}
	};

	new MutationObserver(findCalendars).observe(document.body, {
		childList: true,
		subtree: true,
	});

	findCalendars();
}

/*************************************************************
 * File upload path
 *************************************************************/
function fileInputUpdatePath() {
	function checkInputChanged() {
		for (const input of document.querySelectorAll("input[type=file]")) {
			if (input.hasChangeListener) {
				continue;
			}

			input.addEventListener("change", (e) => {
				const parts = e.target.value.split("\\");
				const placeholder =
					input.parentNode.parentNode.parentNode.querySelector(
						"input[type=text]",
					);
				placeholder.setAttribute("value", parts[parts.length - 1]);
			});

			input.hasChangeListener = true;
		}
	}

	new MutationObserver(() => {
		checkInputChanged();
	}).observe(document.body, {
		childList: true,
		subtree: true,
	});

	checkInputChanged();
}

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
		pie: {
			borderWidth: 0,
		},
		doughnut: {
			borderWidth: 0,
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
			display: (context) => {
				if (["pie", "doughnut", "radar"].includes(context.chart.config.type)) {
					return false;
				}

				return true;
			},
			border: {
				dash: [5, 5],
				dashOffset: 2,
				width: 0,
			},
			ticks: {
				color: "#9ca3af",
				display: true,
				maxTicksLimit: (context) =>
					context.chart.data.datasets.find((dataset) => dataset.maxTicksXLimit)
						?.maxTicksXLimit,
			},
			grid: {
				display: true,
				tickWidth: 0,
			},
		},
		y: {
			display: (context) => {
				if (["pie", "doughnut", "radar"].includes(context.chart.config.type)) {
					return false;
				}

				return true;
			},
			border: {
				dash: [5, 5],
				dashOffset: 5,
				width: 0,
			},
			ticks: {
				color: "#9ca3af",
				display: (context) =>
					context.chart.data.datasets.some((dataset) => {
						return (
							Object.hasOwn(dataset, "displayYAxis") && dataset.displayYAxis
						);
					}),
				callback: function (value) {
					const suffix = this.chart.data.datasets.find(
						(dataset) => dataset.suffixYAxis,
					)?.suffixYAxis;
					if (suffix) {
						return `${value} ${suffix}`;
					}
					return value;
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

		const borderColor = hasDarkClass ? baseColorDark : baseColorLight;

		for (const chart of charts) {
			if (chart.options.scales.x) {
				chart.options.scales.x.grid.color = borderColor;
			}

			if (chart.options.scales.y) {
				chart.options.scales.y.grid.color = borderColor;
			}

			if (chart.options.scales.r) {
				chart.options.scales.r.grid.color = borderColor;
			}
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
				if (Array.isArray(dataset?.[colorProp])) {
					for (const [index, prop] of dataset?.[colorProp].entries()) {
						if (prop.startsWith("var(")) {
							const cssVar = prop.match(/var\((.*?)\)/)[1];
							const color = getComputedStyle(document.documentElement)
								.getPropertyValue(cssVar)
								.trim();
							dataset[colorProp][index] = color;
						}
					}
				} else if (dataset?.[colorProp]?.startsWith("var(")) {
					const cssVar = dataset[colorProp].match(/var\((.*?)\)/)[1];
					const color = getComputedStyle(document.documentElement)
						.getPropertyValue(cssVar)
						.trim();
					dataset[colorProp] = color;
				}
			};

			processColor("borderColor");
			processColor("backgroundColor");
		}

		CHART_OPTIONS = { ...DEFAULT_CHART_OPTIONS };
		if (type === "radar") {
			CHART_OPTIONS.scales = {
				r: {
					ticks: {
						backdropColor: "transparent",
					},
					pointLabels: {
						color: "#9ca3af",
						font: {
							size: 12,
						},
					},
				},
			};
		}
		Chart.defaults.font.family = "Inter";
		Chart.defaults.font.size = 12;

		charts.push(
			new Chart(ctx, {
				type: type || "bar",
				data: parsedData,
				options: options ? JSON.parse(options) : { ...CHART_OPTIONS },
			}),
		);
	}

	changeDarkModeSettings();

	watchClassChanges("html", () => {
		changeDarkModeSettings();
	});
};

/*************************************************************
 * Inlines
 *************************************************************/
function inlines() {
	/**
	 * Replacing: https://github.com/django/django/blob/main/django/contrib/admin/static/admin/js/inlines.js
	 *
	 * Expected HTML structure:
	 *
	 * <div class="formset-wrapper">
	 *     ... management form ...
	 *     <div class="formset">
	 *         <div class="form-group">
	 *             <div class="form-row">inputs</div>
	 *             <div class="form-nested">nested inlines if exists</div>
	 *         </div>
	 *
	 *         ... another form group ...
	 *
	 *         <div class="form-actions">
	 *             <div class="add-row">Add record button</div>
	 *         </div>
	 *     </div>
	 * </div>
	 */
	document.querySelectorAll(".add-row").forEach((el) => {
		el.addEventListener("click", addInlineTemplateHandler);
	});

	document.querySelectorAll(".delete-template").forEach((el) => {
		el.addEventListener("click", deleteInlineTemplateHandler);
	});
}

function deleteInlineTemplateHandler(e) {
	const formset = e.target.closest(".formset");
	const options = JSON.parse(formset.dataset.inlineFormset).options;
	const formsetWrapper = e.target.closest(".formset-wrapper");
	const minNumForms = formsetWrapper.querySelector(
		"input[type=hidden][name$='MIN_NUM_FORMS']",
	);
	const totalForms = formsetWrapper.querySelector(
		"input[type=hidden][name$='TOTAL_FORMS']",
	);
	const maxNumForms = formsetWrapper.querySelector(
		"input[type=hidden][name$='MAX_NUM_FORMS']",
	);
	const rowToDelete = e.target.closest(".form-group");

	if (parseInt(totalForms.value) == parseInt(minNumForms.value)) {
		return;
	}

	let reindex = false;
	formset
		.querySelectorAll(":scope > .form-group:not(.empty-form)")
		.forEach((row, index) => {
			if (rowToDelete.isSameNode(row)) {
				reindex = true;
			}

			if (!rowToDelete.isSameNode(row) && reindex) {
				const content = row.querySelector(":scope > .form-row");

				content.innerHTML = content.innerHTML.replaceAll(
					`${options.prefix}-${index}`,
					`${options.prefix}-${index - 1}`,
				);

				// Reindex nested formset
				const nestedFormset = row.querySelector(":scope .form-nested");
				if (nestedFormset) {
					nestedFormset.innerHTML = nestedFormset.innerHTML.replaceAll(
						`${options.prefix}-${index}`,
						`${options.prefix}-${index - 1}`,
					);
				}
			}
		});

	const rowToDeleteParent = rowToDelete.parentElement;
	rowToDelete.remove();
	updateStackedCounter(rowToDeleteParent);

	// Update total forms count
	totalForms.value = parseInt(
		formset.querySelectorAll(":scope > .form-group:not(.empty-form)").length,
		10,
	);

	// Apply delete event
	formset.querySelectorAll(".delete-template").forEach((el) => {
		el.removeEventListener("click", deleteInlineTemplateHandler);
		el.addEventListener("click", deleteInlineTemplateHandler);
	});

	// Show add button
	if (parseInt(totalForms.value, 10) < parseInt(maxNumForms.value, 10)) {
		formset.querySelector(".add-row").classList.remove("hidden");
	}

	applyLastClass(formset);
	checkFormsetEmpty(formset);

	document.dispatchEvent(
		new CustomEvent("formset:removed", {
			detail: {
				formsetName: options.prefix,
			},
		}),
	);
}

function addInlineTemplateHandler(e) {
	e.preventDefault();

	const formset = e.target.closest(".formset");
	const formsetWrapper = e.target.closest(".formset-wrapper");
	const totalForms = formsetWrapper.querySelector(
		"input[type=hidden][name$='TOTAL_FORMS']",
	);
	const maxNumForms = formsetWrapper.querySelector(
		"input[type=hidden][name$='MAX_NUM_FORMS']",
	);
	const template = formset.querySelector(":scope >.empty-form");
	const index = formset.querySelectorAll(":scope > .form-group").length - 1;
	const options = JSON.parse(formset.dataset.inlineFormset).options;
	const row = template.cloneNode(true);

	row.classList.remove("empty-form");

	if (parseInt(totalForms.value, 10) >= parseInt(maxNumForms.value, 10)) {
		return;
	}

	// Insert new row BEFORE template row which is always last in formset
	formset.insertBefore(row, template);
	applyLastClass(formset);
	checkFormsetEmpty(formset);

	// Stacked inlines are having a counter in title
	updateStackedCounter(row.parentElement);

	// Replace __prefix__ in RECENTLY ADDED row
	const formRow = row.querySelector(":scope > .form-row");
	formRow.innerHTML = formRow.innerHTML.replaceAll(/__prefix__/g, index);

	// Update hidden TOTAL_FORMS input value
	totalForms.value = parseInt(totalForms.value, 10) + 1;

	// Hide add row button if it is not possible to add more rows
	if (totalForms.value === maxNumForms.value) {
		e.target.parentElement.classList.add("hidden");
	}

	// Call special `formsetGroup:added` event to reinitialize inlines
	row.dispatchEvent(
		new CustomEvent("formsetGroup:added", {
			bubbles: true,
			detail: {
				formsetName: options.prefix,
				row: row,
				index: index,
			},
		}),
	);
}

document.addEventListener("formsetGroup:added", (e) => {
	if (!e.detail.row) {
		return;
	}

	e.detail.row.innerHTML = e.detail.row.innerHTML.replaceAll(
		`${e.detail.formsetName}-__prefix__`,
		`${e.detail.formsetName}-${e.detail.index}`,
	);

	if (typeof DateTimeShortcuts !== "undefined") {
		document.querySelectorAll(".datetimeshortcuts").forEach((el) => {
			el.remove();
		});

		DateTimeShortcuts.init();
		dateTimeShortcutsOverlay();
	}

	e.detail.row.querySelector(":scope > .form-row").dispatchEvent(
		new CustomEvent("formset:added", {
			bubbles: true,
			detail: { formsetName: e.detail.formsetName },
		}),
	);

	e.detail.row
		.querySelectorAll(".nested-formset > .form-group:not(.empty-form)")
		.forEach((formGroup) => {
			formGroup.querySelector(".form-row").dispatchEvent(
				new CustomEvent("formset:added", {
					bubbles: true,
					detail: { formsetName: e.detail.formsetName },
				}),
			);
		});

	e.detail.row.querySelectorAll(".add-row").forEach((el) => {
		el.addEventListener("click", addInlineTemplateHandler);
	});

	e.detail.row.querySelectorAll(".delete-template").forEach((el) => {
		el.addEventListener("click", deleteInlineTemplateHandler);
	});
});

function checkFormsetEmpty(formset) {
	const formGroups = formset.querySelectorAll(
		":scope > .form-group:not(.empty-form)",
	);

	if (formGroups.length === 0) {
		formset.classList.add("empty");
	} else {
		formset.classList.remove("empty");
	}
}

function applyLastClass(formset) {
	formset.querySelectorAll(":scope > .form-group").forEach((row) => {
		if (row.classList.contains("last")) {
			row.classList.remove("last");
		}

		if (
			row.nextElementSibling.classList.contains("empty-form") ||
			row.nextElementSibling.classList.contains("form-actions")
		) {
			row.classList.add("last");
		}
	});
}

function updateStackedCounter(rowsParent) {
	rowsParent
		.querySelectorAll(":scope > .form-group:not(.empty-form) > .form-row")
		.forEach((row, index) => {
			const counter = row.querySelector(".stacked-counter");

			if (counter) {
				counter.textContent = index + 1;
			}
		});
}

/*************************************************************
 * Reinitialize inlines after pagination AJAX request
 *************************************************************/
document.addEventListener("htmx:afterSettle", (e) => {
	e.target.querySelectorAll(".form-row").forEach((formRow) => {
		formRow.dispatchEvent(
			new CustomEvent("formset:added", {
				bubbles: true,
				detail: {
					formsetName: JSON.parse(e.target.dataset.inlineFormset).options
						.prefix,
				},
			}),
		);
	});
});

/*************************************************************
 * Crispy formset
 *************************************************************/
function crispyFormsetReindex(formsetId) {
	document
		.querySelectorAll(`#${formsetId} .dynamic-form`)
		.forEach((row, index) => {
			const newIndex =
				document.querySelectorAll(`#${formsetId} .original-form`).length +
				index;

			["id", "name", "for"].forEach((attr) => {
				row.querySelectorAll(`[${attr}]`).forEach((el) => {
					const val = el.getAttribute(attr);

					if (val) {
						el.setAttribute(attr, val.replace(/-\d+-/g, `-${newIndex}-`));
					}
				});
			});
		});
}

function crispyFormsetDelete(target) {
	const rows = target
		? target.querySelectorAll(".crispy-formset-delete")
		: document.querySelectorAll(".crispy-formset-delete");

	rows.forEach((el) => {
		el.addEventListener("click", () => {
			const formsetId = el.dataset.formsetId;
			const formTotalEl = document.querySelector(
				`#${formsetId} input[name*="TOTAL_FORMS"]`,
			);
			const formMinEl = document.querySelector(
				`#${formsetId} input[name*="MIN_NUM_FORMS"]`,
			);
			const totalForms = parseInt(formTotalEl.value, 10);
			const minNumForms = parseInt(formMinEl.value, 10);

			if (totalForms <= minNumForms) {
				return;
			}

			const rowToDelete = el.closest(".dynamic-form");

			rowToDelete.remove();
			formTotalEl.value = formTotalEl.value - 1;

			crispyFormsetReindex(formsetId);
			crispyFormsetToggleAdd(formsetId);
		});
	});
}

function crispyFormsetAdd(target) {
	const formsetId = target.dataset.formsetId;
	const formTotalEl = document.querySelector(
		`#${formsetId} input[name*="TOTAL_FORMS"]`,
	);
	const formCount = parseInt(formTotalEl.value, 10);

	const newForm = document
		.querySelector(`#${formsetId} .empty-form`)
		.cloneNode(true);

	newForm.classList.remove("empty-form", "hidden");
	newForm.classList.add("dynamic-form");
	newForm.innerHTML = newForm.innerHTML.replaceAll(/__prefix__/g, formCount);

	document.getElementById(`${formsetId}-rows`).insertBefore(newForm, null);

	formTotalEl.value = formCount + 1;

	newForm.dispatchEvent(
		new CustomEvent("formset:added", {
			bubbles: true,
		}),
	);

	crispyFormsetToggleAdd(formsetId);
}

function crispyFormsetToggleAdd(formsetId) {
	const totalForms = parseInt(
		document.querySelector(`#${formsetId} input[name*="TOTAL_FORMS"]`).value,
		10,
	);

	const maxNumForms = parseInt(
		document.querySelector(`#${formsetId} input[name*="MAX_NUM_FORMS"]`).value,
		10,
	);

	if (totalForms >= maxNumForms) {
		document
			.getElementById(`${formsetId}-add-row-wrapper`)
			.classList.add("hidden");
	} else {
		document
			.getElementById(`${formsetId}-add-row-wrapper`)
			.classList.remove("hidden");
	}
}

function crispyFormset() {
	document
		.querySelectorAll(".crispy-formset-add")
		.forEach((formsetAddButton) => {
			crispyFormsetToggleAdd(formsetAddButton.dataset.formsetId);

			formsetAddButton.addEventListener("click", () => {
				crispyFormsetAdd(formsetAddButton);
			});
		});

	crispyFormsetDelete();

	document.addEventListener("formset:added", (event) => {
		crispyFormsetDelete(event.target);
	});
}
