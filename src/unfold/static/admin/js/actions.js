/*global gettext, interpolate, ngettext, Actions*/
"use strict";
{
  function show(options, selector) {
    options.parent.querySelectorAll(selector).forEach(function (el) {
      el.classList.remove("hidden");
    });
  }

  function hide(options, selector) {
    options.parent.querySelectorAll(selector).forEach(function (el) {
      el.classList.add("hidden");
    });
  }

  function showQuestion(options) {
    hide(options, options.acrossClears);
    show(options, options.acrossQuestions);
    hide(options, options.allContainer);
  }

  function showClear(options) {
    show(options, options.acrossClears);
    hide(options, options.acrossQuestions);
    options.parent
      .querySelector(options.actionContainer)
      .classList.remove(options.selectedClass);
    show(options, options.allContainer);
    hide(options, options.counterContainer);
  }

  function reset(options) {
    hide(options, options.acrossClears);
    hide(options, options.acrossQuestions);
    hide(options, options.allContainer);
    show(options, options.counterContainer);
  }

  function clearAcross(options) {
    reset(options);
    const acrossInputs = options.parent.querySelectorAll(options.acrossInput);
    acrossInputs.forEach(function (acrossInput) {
      acrossInput.value = 0;
      acrossInput.dispatchEvent(new Event("input"));
    });
    options.parent
      .querySelector(options.actionContainer)
      .classList.remove(options.selectedClass);
  }

  function checker(actionCheckboxes, options, checked) {
    if (checked) {
      showQuestion(options);
    } else {
      reset(options);
    }
    actionCheckboxes.forEach(function (el) {
      el.checked = checked;
      el.closest("tr").classList.toggle(options.selectedClass, checked);
    });
  }

  function updateCounter(actionCheckboxes, options) {
    const sel = Array.from(actionCheckboxes).filter(function (el) {
      return el.checked;
    }).length;
    const counter = options.parent.querySelector(options.counterContainer);
    // data-actions-icnt is defined in the generated HTML
    // and contains the total amount of objects in the queryset
    const actions_icnt = Number(counter.dataset.actionsIcnt);
    counter.textContent = interpolate(
      ngettext(
        "%(sel)s of %(cnt)s selected",
        "%(sel)s of %(cnt)s selected",
        sel
      ),
      {
        sel: sel,
        cnt: actions_icnt,
      },
      true
    );
    const allToggle = options.parent.querySelector(".action-toggle");
    allToggle.checked = sel === actionCheckboxes.length;
    if (allToggle.checked) {
      showQuestion(options);
    } else {
      clearAcross(options);
    }
  }

  const defaults = {
    actionContainer: "div.actions",
    counterContainer: "span.action-counter",
    allContainer: "div.actions span.all",
    acrossInput: "div.actions input.select-across",
    acrossQuestions: "div.actions span.question",
    acrossClears: "div.actions span.clear",
    allToggleId: "action-toggle",
    selectedClass: "selected",
  };

  window.Actions = function (actionCheckboxes, options) {
    options = Object.assign({}, defaults, options);
    let list_editable_changed = false;
    let lastChecked = null;
    let shiftPressed = false;

    document.addEventListener("keydown", (event) => {
      shiftPressed = event.shiftKey;
    });

    document.addEventListener("keyup", (event) => {
      shiftPressed = event.shiftKey;
    });

    const allToggle = options.parent.querySelector(".action-toggle");
    allToggle.addEventListener("click", function (event) {
      checker(actionCheckboxes, options, this.checked);
      updateCounter(actionCheckboxes, options);
    });

    options.parent
      .querySelectorAll(options.acrossQuestions + " a")
      .forEach(function (el) {
        el.addEventListener("click", function (event) {
          event.preventDefault();
          const acrossInputs = options.parent.querySelectorAll(
            options.acrossInput
          );
          acrossInputs.forEach(function (acrossInput) {
            acrossInput.value = 1;
            acrossInput.dispatchEvent(new Event("input"));
          });
          showClear(options);
        });
      });

    options.parent
      .querySelectorAll(options.acrossClears + " a")
      .forEach(function (el) {
        el.addEventListener("click", function (event) {
          event.preventDefault();
          options.parent.querySelector(".action-toggle").checked = false;
          clearAcross(options);
          checker(actionCheckboxes, options, false);
          updateCounter(actionCheckboxes, options);
        });
      });

    function affectedCheckboxes(target, withModifier) {
      const multiSelect = lastChecked && withModifier && lastChecked !== target;
      if (!multiSelect) {
        return [target];
      }
      const checkboxes = Array.from(actionCheckboxes);
      const targetIndex = checkboxes.findIndex((el) => el === target);
      const lastCheckedIndex = checkboxes.findIndex((el) => el === lastChecked);
      const startIndex = Math.min(targetIndex, lastCheckedIndex);
      const endIndex = Math.max(targetIndex, lastCheckedIndex);
      const filtered = checkboxes.filter(
        (el, index) => startIndex <= index && index <= endIndex
      );
      return filtered;
    }

    const resultList = options.parent.querySelector(".result-list").tBodies;
    Array.from(resultList).forEach(function (el) {
      el.addEventListener("change", function (event) {
        const target = event.target;
        if (target.classList.contains("action-select")) {
          const checkboxes = affectedCheckboxes(target, shiftPressed);
          checker(checkboxes, options, target.checked);
          updateCounter(actionCheckboxes, options);
          lastChecked = target;
        } else {
          list_editable_changed = true;
        }
      });
    });

    options.parent
      .querySelector("button[name=index]")
      .addEventListener("click", function (event) {
        if (list_editable_changed) {
          const confirmed = confirm(
            gettext(
              "You have unsaved changes on individual editable fields. If you run an action, your unsaved changes will be lost."
            )
          );
          if (!confirmed) {
            event.preventDefault();
          }
        }
      });

    const el = options.parent.querySelector("input[name=_save]");

    // The button does not exist if no fields are editable.
    if (el) {
      el.addEventListener("click", function (event) {
        if (document.querySelector("[name=action]").value) {
          const text = list_editable_changed
            ? gettext(
                "You have selected an action, but you haven’t saved your changes to individual fields yet. Please click OK to save. You’ll need to re-run the action."
              )
            : gettext(
                "You have selected an action, and you haven’t made any changes on individual fields. You’re probably looking for the Go button rather than the Save button."
              );
          if (!confirm(text)) {
            event.preventDefault();
          }
        }
      });
    }

    // Sync counter when navigating to the page, such as through the back
    // button.
    window.addEventListener("pageshow", (event) =>
      updateCounter(actionCheckboxes, options)
    );
  };

  // Call function fn when the DOM is loaded and ready. If it is already
  // loaded, call the function now.
  // http://youmightnotneedjquery.com/#ready
  function ready(fn) {
    if (document.readyState !== "loading") {
      fn();
    } else {
      document.addEventListener("DOMContentLoaded", fn);
    }
  }

  ready(function () {
    document.querySelectorAll(".result-list-wrapper").forEach(function (el) {
      const actionsEls = el.querySelectorAll("tr input.action-select");

      if (actionsEls.length > 0) {
        Actions(actionsEls, {
          parent: el,
        });
      }
    });
  });
}
