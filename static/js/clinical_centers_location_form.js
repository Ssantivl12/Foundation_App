(function () {
    function ready(callback) {
        if (document.readyState === "loading") {
            document.addEventListener("DOMContentLoaded", callback, { once: true });
        } else {
            callback();
        }
    }

    function initLocationMap() {
        const mapElement = document.getElementById("location-map");
        if (!mapElement) {
            return;
        }
        if (typeof L === "undefined") {
            console.warn("Leaflet no está cargado. Revisa que el script del CDN esté disponible.");
            return;
        }

        const dataset = mapElement.dataset;
        const defaultLat = Number.parseFloat(dataset.defaultLat);
        const defaultLon = Number.parseFloat(dataset.defaultLon);
        const defaultZoom = Number.parseInt(dataset.defaultZoom, 10);
        const hasInitial = dataset.hasInitial === "1";
        const initialLat = Number.parseFloat(dataset.initialLat);
        const initialLon = Number.parseFloat(dataset.initialLon);
        const nominatimEmail = dataset.nominatimEmail || "";

        const latInput = document.getElementById("id_latitude");
        const lonInput = document.getElementById("id_longitude");
        const addressInput = document.getElementById("id_address_text");
        const districtInput = document.getElementById("id_district");
        const statusElement = document.getElementById("location-map-status");

        function setStatus(message, isError = false) {
            if (!statusElement) {
                return;
            }
            statusElement.textContent = message || "";
            statusElement.classList.toggle("is-error", Boolean(isError && message));
        }

        const map = L.map(mapElement, { scrollWheelZoom: true }).setView(
            Number.isFinite(defaultLat) && Number.isFinite(defaultLon) ? [defaultLat, defaultLon] : [0, 0],
            Number.isFinite(defaultZoom) ? defaultZoom : 5,
        );
        L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
            attribution: '&copy; <a href="https://www.openstreetmap.org/">OpenStreetMap</a> contributors',
        }).addTo(map);
        map.whenReady(() => map.invalidateSize());

        let marker = null;
        let addressDirty = false;
        let districtDirty = false;
        let reverseTimeout = null;
        let locateSilent = true;
        let locateShouldCenter = true;

        if (addressInput) {
            addressInput.addEventListener("input", () => {
                addressDirty = true;
            });
        }
        if (districtInput) {
            districtInput.addEventListener("input", () => {
                districtDirty = true;
            });
        }

        function placeMarker(lat, lon) {
            if (!marker) {
                marker = L.marker([lat, lon], { draggable: true }).addTo(map);
                marker.on("dragend", (event) => {
                    const { lat: dragLat, lng: dragLon } = event.target.getLatLng();
                    updateLocationInputs(dragLat, dragLon, true);
                });
            } else {
                marker.setLatLng([lat, lon]);
            }
        }

        function scheduleReverse(lat, lon) {
            if (!nominatimEmail) {
                return;
            }
            window.clearTimeout(reverseTimeout);
            reverseTimeout = window.setTimeout(() => reverseGeocode(lat, lon), 400);
        }

        function updateLocationInputs(lat, lon, shouldReverse) {
            if (latInput) {
                latInput.value = Number(lat).toFixed(6);
            }
            if (lonInput) {
                lonInput.value = Number(lon).toFixed(6);
            }
            placeMarker(lat, lon);
            if (shouldReverse) {
                scheduleReverse(lat, lon);
            }
        }

        function reverseGeocode(lat, lon) {
            const url = new URL("https://nominatim.openstreetmap.org/reverse");
            url.searchParams.set("format", "jsonv2");
            url.searchParams.set("lat", lat);
            url.searchParams.set("lon", lon);
            url.searchParams.set("addressdetails", "1");
            url.searchParams.set("accept-language", "es");
            url.searchParams.set("email", nominatimEmail);

            fetch(url.toString(), { headers: { Accept: "application/json" } })
                .then((response) => (response.ok ? response.json() : null))
                .then((data) => {
                    if (!data) {
                        return;
                    }
                    if (addressInput && !addressDirty && data.display_name) {
                        addressInput.value = data.display_name;
                    }
                    if (districtInput && !districtDirty && data.address) {
                        const address = data.address;
                        const district =
                            address.neighbourhood ||
                            address.suburb ||
                            address.city_district ||
                            address.town ||
                            address.city ||
                            address.village ||
                            "";
                        if (district) {
                            districtInput.value = district;
                        }
                    }
                })
                .catch(() => {});
        }

        function locateUser(options = {}) {
            locateSilent = Boolean(options.silent);
            locateShouldCenter = options.recenter !== false;
            if (!locateSilent) {
                setStatus("Solicitando tu ubicación…");
            }
            map.locate({
                enableHighAccuracy: true,
                timeout: 10000,
                maximumAge: 20000,
                watch: false,
                setView: false,
            });
        }

        const locateControl = L.control({ position: "topleft" });
        locateControl.onAdd = function onAdd() {
            const button = L.DomUtil.create("button", "leaflet-bar leaflet-control");
            button.type = "button";
            button.title = "Usar mi ubicación";
            button.innerHTML = "📍";
            L.DomEvent.on(button, "click", (event) => {
                L.DomEvent.stop(event);
                locateUser({ silent: false, recenter: true });
            });
            return button;
        };
        locateControl.addTo(map);

        map.on("locationfound", (event) => {
            const { latitude, longitude, accuracy } = event;
            if (!locateSilent) {
                if (accuracy) {
                    setStatus(`Ubicación detectada (±${Math.round(accuracy)} m).`);
                } else {
                    setStatus("Ubicación detectada.");
                }
            } else {
                setStatus("");
            }

            if (locateShouldCenter) {
                map.setView([latitude, longitude], Math.max(defaultZoom || 13, 15));
            }
            updateLocationInputs(latitude, longitude, true);
            map.stopLocate();
        });

        map.on("locationerror", (event) => {
            map.stopLocate();
            if (!locateSilent) {
                setStatus(event.message || "No se pudo obtener la ubicación.", true);
            } else {
                setStatus("");
            }
            console.warn("Error de geolocalización:", event.message);
        });

        map.on("click", (event) => {
            updateLocationInputs(event.latlng.lat, event.latlng.lng, true);
        });

        if (latInput) {
            latInput.addEventListener("change", () => {
                const newLat = Number.parseFloat(latInput.value);
                const currentLon = Number.parseFloat(lonInput ? lonInput.value : NaN);
                if (Number.isFinite(newLat) && Number.isFinite(currentLon)) {
                    map.setView([newLat, currentLon], map.getZoom());
                    placeMarker(newLat, currentLon);
                }
            });
        }

        if (lonInput) {
            lonInput.addEventListener("change", () => {
                const newLon = Number.parseFloat(lonInput.value);
                const currentLat = Number.parseFloat(latInput ? latInput.value : NaN);
                if (Number.isFinite(newLon) && Number.isFinite(currentLat)) {
                    map.setView([currentLat, newLon], map.getZoom());
                    placeMarker(currentLat, newLon);
                }
            });
        }

        if (addressInput) {
            let searchTimeout = null;
            addressInput.addEventListener("blur", () => {
                const query = addressInput.value.trim();
                if (!query || !nominatimEmail) {
                    return;
                }
                window.clearTimeout(searchTimeout);
                searchTimeout = window.setTimeout(() => {
                    const url = new URL("https://nominatim.openstreetmap.org/search");
                    url.searchParams.set("format", "jsonv2");
                    url.searchParams.set("limit", "1");
                    url.searchParams.set("accept-language", "es");
                    url.searchParams.set("email", nominatimEmail);
                    url.searchParams.set("q", query);

                    fetch(url.toString(), { headers: { Accept: "application/json" } })
                        .then((response) => (response.ok ? response.json() : null))
                        .then((results) => {
                            if (!results || !results.length) {
                                return;
                            }
                            const result = results[0];
                            const lat = Number.parseFloat(result.lat);
                            const lon = Number.parseFloat(result.lon);
                            if (Number.isFinite(lat) && Number.isFinite(lon)) {
                                map.setView([lat, lon], Math.max(defaultZoom || 13, 15));
                                updateLocationInputs(lat, lon, false);
                                if (districtInput && !districtDirty && result.address) {
                                    const address = result.address;
                                    const district =
                                        address.neighbourhood ||
                                        address.suburb ||
                                        address.city_district ||
                                        address.town ||
                                        address.city ||
                                        address.village ||
                                        "";
                                    if (district) {
                                        districtInput.value = district;
                                    }
                                }
                            }
                        })
                        .catch(() => {});
                }, 400);
            });
        }

        if (hasInitial && Number.isFinite(initialLat) && Number.isFinite(initialLon)) {
            map.setView([initialLat, initialLon], Math.max(defaultZoom || 13, 15));
            updateLocationInputs(initialLat, initialLon, false);
        } else {
            // intentar geolocalizar siempre al cargar
            window.setTimeout(() => locateUser({ silent: false, recenter: true }), 250);
        }

        window.setTimeout(() => map.invalidateSize(), 250);
    }

    ready(initLocationMap);
})();
