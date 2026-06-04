class ThemeUnfold extends Jedison.Theme {
	constructor(formClasses = null) {
		super();

		this.formClasses = formClasses;
		this.buttonClasses = [
			"border",
			"border-base-200",
			"bg-primary-600",
			"border-transparent",
			"text-white",
			"cursor-pointer",
			"font-medium",
			"inline-flex",
			"group",
			"items-center",
			"gap-1",
			"mt-3",
			"px-3",
			"py-2",
			"relative",
			"rounded-default",
			"justify-center",
			"whitespace-nowrap",
			"hover:bg-primary-600/80",
		];
	}

	getMultipleControl(config = {}) {
		const multipleControl = super.getMultipleControl(config);
		const { container } = multipleControl;

		container.classList.add(
			...["flex", "flex-col", "gap-3", "max-w-2xl", "w-full"],
		);

		return multipleControl;
	}

	getAddPropertyButton(config) {
		const btn = super.getAddPropertyButton(config);
		btn.classList.add(...this.buttonClasses, "w-full");
		return btn;
	}

	getLabel(config) {
		const labelObj = super.getLabel(config);
		this.addCssClasses(labelObj.label, "label");

		return labelObj;
	}

	getInputControl(config) {
		const control = super.getInputControl(config);
		const { input, container, messages, description } = control;
		this.addCssClasses(input, "text_input");

		container.classList.add(...["group", "relative"]);
		container.appendChild(messages);
		container.appendChild(description);
		return control;
	}

	getSelectControl(config) {
		const control = super.getSelectControl(config);
		const { input, container, messages, description } = control;

		this.addCssClasses(input, "select");

		container.classList.add(...["group", "relative", "select-wrapper"]);
		container.appendChild(messages);
		container.appendChild(description);
		return control;
	}

	getTextareaControl(config) {
		const control = super.getTextareaControl(config);
		const { input, container, messages, description } = control;

		this.addCssClasses(input, "textarea");

		container.classList.add(["group", "relative"]);
		container.appendChild(messages);
		container.appendChild(description);
		return control;
	}

	getCheckboxControl(config) {
		const control = super.getCheckboxControl(config);
		const { container, formGroup, input, description, messages } = control;

		formGroup.classList.add("flex", "items-center", "gap-2", "*:mb-0");

		this.addCssClasses(input, "checkbox");

		container.classList.add("group");
		container.appendChild(messages);
		container.appendChild(description);
		return control;
	}

	getErrorFeedback(config) {
		const html = document.createElement("div");

		html.classList.add("jedi-error-message");
		html.textContent = config.message;

		return html;
	}

	addCssClasses(el, name) {
		this.formClasses[name].split(/\s+/).forEach((cls) => {
			if (cls) el.classList.add(cls);
		});

		return el;
	}
}
