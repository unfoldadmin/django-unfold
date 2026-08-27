"use strict";
{
	const $ = django.jQuery;

	function fieldNameForParent(child, parentField) {
		const parts = child.name.split("-");
		parts[parts.length - 1] = parentField;
		return parts.join("-");
	}

	function resolveParent(child) {
		const parentName = child.dataset.dependentAutocompleteParent;
		const parentId = "id_" + fieldNameForParent(child, parentName);
		return document.getElementById(parentId);
	}

	function parameter(data, name) {
		if (typeof data !== "string") {
			return data && Object.prototype.hasOwnProperty.call(data, name)
				? data[name]
				: null;
		}
		const match = new RegExp("(?:^|&)" + name + "=([^&]*)").exec(data);
		return match
			? decodeURIComponent(match[1].replace(/\+/g, " "))
			: null;
	}

	function pathFor(url) {
		const link = document.createElement("a");
		link.href = url;
		return link.pathname;
	}

	function childForRequest(settings, data) {
		const fieldName = parameter(data, "field_name");
		const endpoint = pathFor(settings.url);
		const candidates = $("select[data-dependent-autocomplete-parent]").filter(
			function () {
				return (
					$(this).attr("data-field-name") === fieldName &&
					pathFor($(this).attr("data-ajax--url")) === endpoint
				);
			},
		);
		const active = candidates.filter(function () {
			return $(this)
				.next(".select2-container")
				.hasClass("select2-container--open");
		});
		return active.first().length ? active.first() : candidates.first();
	}

	$(function () {
		$.ajaxPrefilter(function (options) {
			const $child = childForRequest(options, options.data || {});
			if (!$child.length) {
				return;
			}
			const element = $child[0];
			const parentElement = resolveParent(element);
			const parentValue = parentElement ? parentElement.value : "";
			if (typeof options.data === "string") {
				options.data +=
					(options.data ? "&" : "") +
					$.param({ dependent_parent: parentValue });
			} else {
				options.data = $.extend({}, options.data, {
					dependent_parent: parentValue,
				});
			}
		});

		function clearDependentChildren(parent, cleared) {
			cleared = cleared || [];
			if (cleared.indexOf(parent) !== -1) {
				return;
			}
			cleared.push(parent);
			$("select[data-dependent-autocomplete-parent]").each(function () {
				const parentElement = resolveParent(this);
				if (parentElement === parent) {
					$(this).val(null).trigger("change");
					clearDependentChildren(this, cleared);
				}
			});
		}

		$(document).on(
			"change",
			"select:not(.admin-autocomplete)",
			function () {
				clearDependentChildren(this);
			},
		);

		$(document).on(
			"select2:select select2:clear",
			"select.admin-autocomplete",
			function () {
				clearDependentChildren(this);
			},
		);
	});
}
