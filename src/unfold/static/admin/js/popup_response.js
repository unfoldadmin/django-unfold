{
	const initData = JSON.parse(
		document.getElementById("django-admin-popup-response-constants").dataset
			.popupResponse,
	);

	const newWindowName =
		window.name.replace(/^(change|add|delete|lookup)_/, "") + "__1";

	const shadowWindow = {
		name: newWindowName,
		location: window.parent.location,
		close: () => {},
	};

	switch (initData.action) {
		case "change":
			window.parent.dismissChangeRelatedObjectPopup(
				shadowWindow,
				initData.value,
				initData.obj,
				initData.new_value,
			);
			break;
		case "delete":
			window.parent.dismissDeleteRelatedObjectPopup(
				shadowWindow,
				initData.value,
			);
			break;
		default:
			window.parent.dismissAddRelatedObjectPopup(
				shadowWindow,
				initData.value,
				initData.obj,
				initData.optgroup,
			);
			break;
	}
}
