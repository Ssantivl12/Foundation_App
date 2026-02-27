(function () {
    "use strict";

    function ready(callback) {
        if (document.readyState === "loading") {
            document.addEventListener("DOMContentLoaded", callback, { once: true });
        } else {
            callback();
        }
    }

    /* ============================================================
       SERVICES — chip / tag input
       ============================================================ */

    function parseServicesText(text) {
        if (!text || !text.trim()) return [];
        return text
            .split(/[\n,;]+/)
            .map(function (s) { return s.trim(); })
            .filter(Boolean);
    }

    function serializeChips(chips) {
        return chips.join("\n");
    }

    function initServicesWidget(textarea) {
        textarea.style.display = "none";

        var chips = parseServicesText(textarea.value);

        // Build DOM
        var container = document.createElement("div");
        container.className = "chip-input";

        var chipsArea = document.createElement("div");
        chipsArea.className = "chip-input__chips";

        var inputWrap = document.createElement("div");
        inputWrap.className = "chip-input__input-wrap";

        var input = document.createElement("input");
        input.type = "text";
        input.className = "chip-input__input";
        input.placeholder = "Agregar servicio…";
        input.setAttribute("autocomplete", "off");

        inputWrap.appendChild(input);
        container.appendChild(chipsArea);
        container.appendChild(inputWrap);

        // Insert before the hidden textarea
        textarea.parentNode.insertBefore(container, textarea);

        function sync() {
            textarea.value = serializeChips(chips);
        }

        function addChip(value) {
            var text = value.trim();
            if (!text) return;
            if (chips.indexOf(text) !== -1) return; // no duplicates
            chips.push(text);
            render();
            sync();
        }

        function removeChip(index) {
            chips.splice(index, 1);
            render();
            sync();
        }

        function render() {
            chipsArea.innerHTML = "";
            chips.forEach(function (chip, index) {
                var tag = document.createElement("span");
                tag.className = "chip";

                var text = document.createTextNode(chip + "\u00a0");
                tag.appendChild(text);

                var btn = document.createElement("button");
                btn.type = "button";
                btn.className = "chip__remove";
                btn.setAttribute("aria-label", "Eliminar " + chip);
                btn.innerHTML = "&times;";
                btn.addEventListener("click", function (e) {
                    e.stopPropagation();
                    removeChip(index);
                });

                tag.appendChild(btn);
                chipsArea.appendChild(tag);
            });
        }

        input.addEventListener("keydown", function (e) {
            if (e.key === "Enter" || e.key === "," || e.key === ";" || e.key === "Tab") {
                if (input.value.trim()) {
                    e.preventDefault();
                    addChip(input.value);
                    input.value = "";
                }
            } else if (e.key === "Backspace" && !input.value && chips.length) {
                removeChip(chips.length - 1);
            }
        });

        input.addEventListener("blur", function () {
            if (input.value.trim()) {
                addChip(input.value);
                input.value = "";
            }
        });

        // Click anywhere on container → focus input
        container.addEventListener("click", function () {
            input.focus();
        });

        render();
    }

    /* ============================================================
       OPERATING HOURS — structured day/slot widget
       ============================================================ */

    var DAYS = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"];

    var DAY_ALIASES = {
        "lunes": 0, "martes": 1,
        "miércoles": 2, "miercoles": 2,
        "jueves": 3, "viernes": 4,
        "sábado": 5, "sabado": 5,
        "domingo": 6,
    };

    function parseHoursText(text) {
        // Returns { 0: [{open, close}, ...], 1: [], ... }
        var result = {};
        for (var i = 0; i < 7; i++) result[i] = [];

        if (!text || !text.trim()) return result;

        var lines = text.split("\n");
        lines.forEach(function (line) {
            line = line.trim();
            if (!line) return;
            var colonIdx = line.indexOf(":");
            if (colonIdx < 0) return;

            var dayLabel = line.slice(0, colonIdx).trim().toLowerCase();
            var dayIdx = DAY_ALIASES[dayLabel];
            if (dayIdx === undefined) return;

            var rangesBlob = line.slice(colonIdx + 1).trim();
            if (!rangesBlob) return;

            rangesBlob.split(",").forEach(function (chunk) {
                var m = chunk.trim().match(/^(\d{2}:\d{2})\s*-\s*(\d{2}:\d{2})$/);
                if (m) {
                    result[dayIdx].push({ open: m[1], close: m[2] });
                }
            });
        });

        return result;
    }

    function serializeHours(hoursData) {
        return DAYS.map(function (label, idx) {
            var slots = hoursData[idx] || [];
            if (!slots.length) return label + ":";
            var ranges = slots.map(function (s) { return s.open + "-" + s.close; }).join(", ");
            return label + ": " + ranges;
        }).join("\n");
    }

    function initHoursWidget(textarea) {
        textarea.style.display = "none";

        var hoursData = parseHoursText(textarea.value);

        function sync() {
            textarea.value = serializeHours(hoursData);
        }

        var widget = document.createElement("div");
        widget.className = "hours-widget";

        function buildWidget() {
            widget.innerHTML = "";

            DAYS.forEach(function (dayLabel, dayIdx) {
                var row = document.createElement("div");
                row.className = "hours-row";

                var label = document.createElement("span");
                label.className = "hours-row__day";
                label.textContent = dayLabel;
                row.appendChild(label);

                var slotsEl = document.createElement("div");
                slotsEl.className = "hours-row__slots";

                var slots = hoursData[dayIdx] || [];

                slots.forEach(function (slot, slotIdx) {
                    var slotEl = document.createElement("div");
                    slotEl.className = "hours-slot";

                    var openInput = document.createElement("input");
                    openInput.type = "time";
                    openInput.className = "hours-slot__time";
                    openInput.value = slot.open;
                    openInput.setAttribute("aria-label", "Apertura " + dayLabel);
                    openInput.addEventListener("change", function () {
                        hoursData[dayIdx][slotIdx].open = openInput.value;
                        sync();
                    });

                    var sep = document.createElement("span");
                    sep.className = "hours-slot__sep";
                    sep.setAttribute("aria-hidden", "true");
                    sep.textContent = "–";

                    var closeInput = document.createElement("input");
                    closeInput.type = "time";
                    closeInput.className = "hours-slot__time";
                    closeInput.value = slot.close;
                    closeInput.setAttribute("aria-label", "Cierre " + dayLabel);
                    closeInput.addEventListener("change", function () {
                        hoursData[dayIdx][slotIdx].close = closeInput.value;
                        sync();
                    });

                    var removeBtn = document.createElement("button");
                    removeBtn.type = "button";
                    removeBtn.className = "hours-slot__remove";
                    removeBtn.setAttribute("aria-label", "Eliminar turno");
                    removeBtn.innerHTML = "&times;";
                    removeBtn.addEventListener("click", function () {
                        hoursData[dayIdx].splice(slotIdx, 1);
                        sync();
                        buildWidget();
                    });

                    slotEl.appendChild(openInput);
                    slotEl.appendChild(sep);
                    slotEl.appendChild(closeInput);
                    slotEl.appendChild(removeBtn);
                    slotsEl.appendChild(slotEl);
                });

                var addBtn = document.createElement("button");
                addBtn.type = "button";
                addBtn.className = "hours-row__add";
                addBtn.setAttribute("aria-label", "Agregar turno para " + dayLabel);
                addBtn.textContent = "+ Turno";
                addBtn.addEventListener("click", function () {
                    if (!hoursData[dayIdx]) hoursData[dayIdx] = [];
                    hoursData[dayIdx].push({ open: "08:00", close: "17:00" });
                    sync();
                    buildWidget();
                });

                row.appendChild(slotsEl);
                row.appendChild(addBtn);
                widget.appendChild(row);
            });
        }

        textarea.parentNode.insertBefore(widget, textarea);
        buildWidget();
        sync(); // ensure textarea is in text format on load
    }

    /* ============================================================
       INIT
       ============================================================ */

    ready(function () {
        document.querySelectorAll(".js-services-textarea").forEach(initServicesWidget);
        document.querySelectorAll(".js-hours-textarea").forEach(initHoursWidget);
    });
})();
