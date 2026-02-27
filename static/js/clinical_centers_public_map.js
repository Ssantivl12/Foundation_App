(function () {
    "use strict";

    function ready(callback) {
        if (document.readyState === "loading") {
            document.addEventListener("DOMContentLoaded", callback, { once: true });
        } else {
            callback();
        }
    }

    function escapeHtml(str) {
        if (str == null) return "";
        return String(str)
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#39;");
    }

    /** Mini popup shown when clicking a marker. */
    function buildMiniPopup(center) {
        const services = Array.isArray(center.services) ? center.services : [];
        const shown = services.slice(0, 3);
        const extra = services.length - shown.length;

        const chipsHtml = shown.length
            ? '<div class="cpopup__services">' +
              shown.map((s) => `<span class="cpopup__chip">${escapeHtml(s)}</span>`).join("") +
              (extra > 0 ? `<span class="cpopup__chip cpopup__chip--more">+${extra}</span>` : "") +
              "</div>"
            : "";

        const contactHtml = [
            center.phone ? `<span>${escapeHtml(center.phone)}</span>` : "",
            center.email ? `<span>${escapeHtml(center.email)}</span>` : "",
        ]
            .filter(Boolean)
            .join("");

        return (
            '<div class="cpopup">' +
            `<p class="cpopup__name">${escapeHtml(center.name)}</p>` +
            (center.category ? `<p class="cpopup__category">${escapeHtml(center.category)}</p>` : "") +
            (contactHtml ? `<div class="cpopup__contact">${contactHtml}</div>` : "") +
            chipsHtml +
            `<button class="cpopup__btn" data-action="show-detail" data-center-id="${center.id}">Ver detalles →</button>` +
            "</div>"
        );
    }

    /** Operating hours table for the detail panel. */
    function buildHoursHtml(hoursLines) {
        if (!Array.isArray(hoursLines) || !hoursLines.length) return "";

        const rows = hoursLines
            .map((line) => {
                const colonIdx = line.indexOf(":");
                if (colonIdx < 0) return "";
                const day = escapeHtml(line.slice(0, colonIdx).trim());
                const hours = line.slice(colonIdx + 1).trim();
                const timeHtml = hours
                    ? escapeHtml(hours)
                    : '<span class="dh__closed">Cerrado</span>';
                return `<tr class="dh__row"><td class="dh__day">${day}</td><td class="dh__time">${timeHtml}</td></tr>`;
            })
            .filter(Boolean);

        return rows.length ? `<table class="dh">${rows.join("")}</table>` : "";
    }

    function initPublicCentersMap() {
        const mapElement = document.getElementById("public-centers-map");
        if (!mapElement) return;
        if (typeof L === "undefined") {
            console.warn("Leaflet no está cargado. Verifica el script del CDN.");
            return;
        }

        const defaultLat = Number.parseFloat(mapElement.dataset.defaultLat);
        const defaultLon = Number.parseFloat(mapElement.dataset.defaultLon);
        const defaultZoom = Number.parseInt(mapElement.dataset.defaultZoom, 10);
        const initialCategory = mapElement.dataset.initialCategory || "";

        const centersScript = document.getElementById("centers-data");
        const centers = centersScript ? JSON.parse(centersScript.textContent) : [];

        const statusElement = document.getElementById("public-map-status");
        const filterResultElement = document.getElementById("map-filter-result");
        const categorySelect = document.getElementById("category-filter");
        const resetButton = document.getElementById("category-filter-reset");
        const detailPanel = document.getElementById("center-detail");
        const detailClose = document.getElementById("detail-close");
        const detailBody = document.getElementById("detail-body");
        const detailNameEl = document.getElementById("detail-name");
        const detailCategoryEl = document.getElementById("detail-category");
        const mapLayout = document.getElementById("map-layout");

        // O(1) lookup: id → center data
        const centersById = Object.fromEntries(centers.map((c) => [String(c.id), c]));

        function setStatus(msg, isError = false) {
            if (!statusElement) return;
            statusElement.textContent = msg || "";
            statusElement.classList.toggle("is-error", Boolean(isError && msg));
        }

        function setFilterResult(msg, isError = false) {
            if (!filterResultElement) return;
            filterResultElement.textContent = msg || "";
            filterResultElement.classList.toggle("is-error", Boolean(isError && msg));
        }

        const centerPoint = [
            Number.isFinite(defaultLat) ? defaultLat : 0,
            Number.isFinite(defaultLon) ? defaultLon : 0,
        ];
        const zoomLevel = Number.isFinite(defaultZoom) ? defaultZoom : 5;

        const map = L.map(mapElement, { scrollWheelZoom: true }).setView(centerPoint, zoomLevel);

        // CartoDB Positron — clean, minimal, free, no API key required
        L.tileLayer("https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png", {
            attribution:
                '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>',
            subdomains: "abcd",
            maxZoom: 20,
        }).addTo(map);

        // User location marker
        const userMarker = L.marker(centerPoint, {
            icon: window.CenterIcons ? window.CenterIcons.user : undefined,
        });

        // ---- Detail panel ----

        let activeMarkerEntry = null;

        function resetActiveMarker() {
            if (activeMarkerEntry && window.CenterIcons) {
                activeMarkerEntry.marker.setIcon(window.CenterIcons.center);
                activeMarkerEntry = null;
            }
        }

        function closeDetail() {
            if (!detailPanel) return;
            detailPanel.classList.remove("is-open");
            if (mapLayout) mapLayout.classList.remove("map-layout--detail-open");
            resetActiveMarker();
            setTimeout(() => map.invalidateSize(), 280);
        }

        function showCenterDetail(center) {
            if (!detailPanel) return;

            // Populate header
            if (detailNameEl) detailNameEl.textContent = center.name;
            if (detailCategoryEl) detailCategoryEl.textContent = center.category || "";

            // Build body sections
            const parts = [];

            if (center.description) {
                parts.push(`<p class="cd-desc">${escapeHtml(center.description)}</p>`);
            }

            // Location
            const locParts = [center.address, center.district].filter(Boolean);
            if (locParts.length) {
                parts.push(
                    '<div class="cd-section">' +
                    '<p class="cd-section__label">Ubicación</p>' +
                    locParts.map((p) => `<p class="cd-section__value">${escapeHtml(p)}</p>`).join("") +
                    "</div>"
                );
            }

            // Contact
            const contactItems = [
                center.phone ? ["Teléfono", center.phone, false] : null,
                center.email ? ["Email", center.email, false] : null,
                center.website ? ["Sitio web", center.website, true] : null,
            ].filter(Boolean);
            if (contactItems.length) {
                const rows = contactItems.map(([label, val, isLink]) => {
                    const valHtml = isLink
                        ? `<a href="${escapeHtml(val)}" target="_blank" rel="noopener">${escapeHtml(val)}</a>`
                        : escapeHtml(val);
                    return (
                        '<div class="cd-contact-row">' +
                        `<span class="cd-contact-row__label">${escapeHtml(label)}</span>` +
                        `<span class="cd-contact-row__value">${valHtml}</span>` +
                        "</div>"
                    );
                });
                parts.push(
                    '<div class="cd-section"><p class="cd-section__label">Contacto</p>' +
                    rows.join("") +
                    "</div>"
                );
            }

            // Services
            const services = Array.isArray(center.services) ? center.services : [];
            if (services.length) {
                const chips = services
                    .map((s) => `<span class="cd-chip">${escapeHtml(s)}</span>`)
                    .join("");
                parts.push(
                    '<div class="cd-section"><p class="cd-section__label">Servicios</p>' +
                    `<div class="cd-chips">${chips}</div>` +
                    "</div>"
                );
            }

            // Operating hours
            const hoursHtml = buildHoursHtml(center.operating_hours);
            if (hoursHtml) {
                parts.push(
                    '<div class="cd-section"><p class="cd-section__label">Horarios</p>' +
                    hoursHtml +
                    "</div>"
                );
            }

            // Hours note
            if (center.hours_note) {
                parts.push(`<p class="cd-hours-note">${escapeHtml(center.hours_note)}</p>`);
            }

            if (detailBody) detailBody.innerHTML = parts.join("");

            // Show panel
            detailPanel.classList.add("is-open");
            if (mapLayout) mapLayout.classList.add("map-layout--detail-open");

            // Highlight active marker
            resetActiveMarker();
            const entry = markerEntries.find((e) => String(e.center.id) === String(center.id));
            if (entry && window.CenterIcons) {
                entry.marker.setIcon(window.CenterIcons.centerActive);
                activeMarkerEntry = entry;
            }

            // Give grid time to resize before adjusting map
            setTimeout(() => map.invalidateSize(), 280);
        }

        if (detailClose) detailClose.addEventListener("click", closeDetail);

        // Delegate "Ver detalles" button clicks inside popups
        mapElement.addEventListener("click", (e) => {
            const btn = e.target.closest("[data-action='show-detail']");
            if (btn) {
                const center = centersById[String(btn.dataset.centerId)];
                if (center) showCenterDetail(center);
            }
        });

        // ---- Markers ----

        const markerEntries = centers.reduce((acc, center) => {
            if (!Number.isFinite(center.latitude) || !Number.isFinite(center.longitude)) return acc;

            const marker = L.marker([center.latitude, center.longitude], {
                icon: window.CenterIcons ? window.CenterIcons.center : undefined,
            });

            // Permanent name label above the marker
            const label = center.name.length > 24 ? center.name.slice(0, 22) + "…" : center.name;
            marker.bindTooltip(label, {
                permanent: true,
                direction: "top",
                className: "center-name-label",
                offset: [0, -12],
            });

            // Mini popup on click
            marker.bindPopup(buildMiniPopup(center), {
                className: "center-popup",
                minWidth: 220,
                maxWidth: 290,
            });

            acc.push({ marker, center });
            return acc;
        }, []);

        if (!markerEntries.length) {
            setStatus("No hay centros clínicos registrados todavía.");
            setFilterResult("No hay centros registrados.", true);
        }

        // ---- Category filter ----

        function getCategoryLabel(categoryId) {
            if (!categorySelect) return "";
            const opt = Array.from(categorySelect.options).find((o) => o.value === categoryId);
            return opt ? opt.textContent.trim() : "";
        }

        function adjustView(bounds) {
            if (!bounds.length) { map.setView(centerPoint, zoomLevel); return; }
            if (bounds.length === 1) { map.setView(bounds[0], Math.max(defaultZoom || 5, 15)); return; }
            map.fitBounds(bounds, { padding: [20, 20] });
        }

        function applyFilter(categoryId = "") {
            const target = categoryId ? String(categoryId) : "";
            const bounds = [];
            let visibleCount = 0;

            markerEntries.forEach(({ marker, center }) => {
                const matches = !target || String(center.category_id || "") === target;
                const isVisible = map.hasLayer(marker);
                if (matches && !isVisible) marker.addTo(map);
                else if (!matches && isVisible) map.removeLayer(marker);
                if (matches) {
                    bounds.push([center.latitude, center.longitude]);
                    visibleCount += 1;
                }
            });

            adjustView(bounds);
            if (!markerEntries.length) return;

            const label = target ? getCategoryLabel(target) : "";
            if (!visibleCount) {
                setFilterResult(
                    target
                        ? `No hay centros para la categoría ${label || "seleccionada"}.`
                        : "No hay centros registrados todavía.",
                    true
                );
            } else {
                setFilterResult(
                    target
                        ? `Mostrando ${visibleCount} centro${visibleCount === 1 ? "" : "s"} de ${label || "la categoría seleccionada"}.`
                        : `Mostrando ${visibleCount} centro${visibleCount === 1 ? "" : "s"} activos.`
                );
            }
        }

        if (categorySelect) {
            categorySelect.addEventListener("change", () => applyFilter(categorySelect.value));
        }
        if (resetButton && categorySelect) {
            resetButton.addEventListener("click", () => {
                if (!categorySelect.value) { categorySelect.blur(); applyFilter(""); return; }
                categorySelect.value = "";
                categorySelect.dispatchEvent(new Event("change"));
                categorySelect.focus();
            });
        }

        const initialFilter = categorySelect ? (categorySelect.value || initialCategory) : initialCategory;
        if (markerEntries.length) applyFilter(initialFilter);

        // ---- Geolocation ----

        const locateControl = L.control({ position: "topleft" });
        locateControl.onAdd = function () {
            const btn = L.DomUtil.create("button", "leaflet-bar leaflet-control");
            btn.type = "button";
            btn.title = "Actualizar mi ubicación";
            btn.innerHTML = "📍";
            L.DomEvent.on(btn, "click", (e) => { L.DomEvent.stop(e); locateVisitor({ silent: false }); });
            return btn;
        };
        locateControl.addTo(map);

        function locateVisitor({ silent = false } = {}) {
            if (!silent) setStatus("Localizando tu ubicación…");
            map.locate({
                enableHighAccuracy: true,
                timeout: 10000,
                maximumAge: silent ? 60000 : 20000,
                watch: false,
                setView: false,
            });
        }

        map.on("locationfound", ({ latitude, longitude, accuracy }) => {
            userMarker.setLatLng([latitude, longitude]).addTo(map);
            userMarker.bindPopup("Estás aquí").openPopup();
            map.setView([latitude, longitude], Math.max(defaultZoom || 5, 13));
            setStatus(accuracy ? `Ubicación detectada (±${Math.round(accuracy)} m).` : "Ubicación detectada.");
        });

        map.on("locationerror", (e) => {
            setStatus(e.message || "No se pudo obtener tu ubicación.", true);
        });

        locateVisitor({ silent: false });
    }

    ready(initPublicCentersMap);
})();
