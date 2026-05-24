class ThemeUnfold extends Jedison.Theme {
	constructor(formClasses = null) {
		super();

		this.formClasses = formClasses;
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

		container.classList.add("group");
		container.appendChild(messages);
		container.appendChild(description);
		return control;
	}

	getSelectControl(config) {
		const control = super.getSelectControl(config);
		const { input, container, messages, description } = control;

		this.addCssClasses(input, "select");

		container.classList.add("group");
		container.appendChild(messages);
		container.appendChild(description);
		return control;
	}

	getTextareaControl(config) {
		const control = super.getTextareaControl(config);
		const { input, container, messages, description } = control;

		this.addCssClasses(input, "textarea");

		container.classList.add("group");
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
