window.CenterIcons = (function () {
    // Normal clinic marker — primary blue circle
    const center = L.divIcon({
        className: "",
        html: '<div class="map-pin"></div>',
        iconSize: [20, 20],
        iconAnchor: [10, 10],
        popupAnchor: [0, -14],
        tooltipAnchor: [0, -14],
    });

    // Active/selected clinic marker — accent colour, slightly larger
    const centerActive = L.divIcon({
        className: "",
        html: '<div class="map-pin map-pin--active"></div>',
        iconSize: [24, 24],
        iconAnchor: [12, 12],
        popupAnchor: [0, -16],
        tooltipAnchor: [0, -16],
    });

    // User location marker — red dot
    const user = L.divIcon({
        className: "",
        html: '<div class="map-pin map-pin--user"></div>',
        iconSize: [14, 14],
        iconAnchor: [7, 7],
        popupAnchor: [0, -10],
    });

    return { center, centerActive, user };
})();
