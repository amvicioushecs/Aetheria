/**
 * Contact-page map of all Aetheria Funeral Homes locations.
 *
 * Uses Leaflet with OpenStreetMap tiles (no API key). Coordinates were
 * looked up once from Nominatim and are hardcoded below. Name, address,
 * and phone are read from the location cards on this page.
 */
(function () {
  "use strict";

  // Nominatim / OpenStreetMap results, retrieved 2026-11-16.
  // East Los Angeles addressdetails listed "Compton" as city, but the
  // display name, ZIP 90022, and coordinates match Eastmont / East LA.
  const LOCATION_COORDINATES = {
    "east-los-angeles": { lat: 34.0300304, lng: -118.15037 },
    "santa-ana": { lat: 33.7682437, lng: -117.8515091 },
    "ontario": { lat: 34.0317022, lng: -117.6506114 },
    "hawthorne": { lat: 33.9061721, lng: -118.3522848 },
    "oakland": { lat: 37.772698, lng: -122.195748 }
  };

  const OSM_ATTRIBUTION =
    '&copy; <a href="https://www.openstreetmap.org/copyright" target="_blank" rel="noopener noreferrer">OpenStreetMap</a> contributors';
  const OSM_TILE_URL = "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png";

  const mapEl = document.getElementById("locations-map");
  const fallbackEl = document.getElementById("locations-map-fallback");
  const statusEl = document.getElementById("locations-map-status");
  const layoutEl = document.querySelector(".locations-map-layout");

  if (!mapEl) return;

  function setStatus(message) {
    if (statusEl) statusEl.textContent = message || "";
  }

  function showFallback(message) {
    if (fallbackEl) {
      if (message) {
        const body = fallbackEl.querySelector("[data-fallback-body]");
        if (body) body.textContent = message;
      }
      fallbackEl.hidden = false;
    }
    mapEl.setAttribute("aria-hidden", "true");
    if (layoutEl) layoutEl.classList.remove("is-interactive");
  }

  function hideFallback() {
    if (fallbackEl) fallbackEl.hidden = true;
    mapEl.removeAttribute("aria-hidden");
  }

  function directionsUrl(address) {
    return "https://www.google.com/maps/dir/?api=1&destination=" + encodeURIComponent(address);
  }

  function readLocations() {
    const cards = document.querySelectorAll(".loc-list .loc-card[data-location-id]");
    return Array.from(cards).map(function (card) {
      const address =
        card.getAttribute("data-address") ||
        (card.querySelector("address")
          ? card.querySelector("address").innerText.replace(/\s+/g, " ").trim()
          : "");
      const tel = card.querySelector("a.tel");
      const coords = LOCATION_COORDINATES[card.getAttribute("data-location-id")];
      return {
        id: card.getAttribute("data-location-id"),
        name: card.getAttribute("data-name") || (card.querySelector("h3") && card.querySelector("h3").textContent.trim()) || "",
        address: address,
        phone: card.getAttribute("data-phone") || (tel && tel.textContent.trim()) || "",
        phoneHref: card.getAttribute("data-phone-href") || (tel && tel.getAttribute("href")) || "",
        directions: (address ? directionsUrl(address) : "") || card.getAttribute("data-directions") || "",
        lat: coords && coords.lat,
        lng: coords && coords.lng,
        card: card
      };
    }).filter(function (loc) {
      return loc.id && loc.name && loc.address && typeof loc.lat === "number" && typeof loc.lng === "number";
    });
  }

  function buildPopup(loc) {
    var wrap = document.createElement("div");
    wrap.className = "loc-info";

    var header = document.createElement("strong");
    header.className = "loc-info-header";
    header.textContent = loc.name;
    wrap.appendChild(header);

    var address = document.createElement("address");
    address.textContent = loc.address;
    wrap.appendChild(address);

    if (loc.phone) {
      var phone = document.createElement("a");
      phone.className = "tel";
      phone.href = loc.phoneHref || ("tel:" + loc.phone.replace(/[^\d+]/g, ""));
      phone.textContent = loc.phone;
      wrap.appendChild(phone);
    }

    if (loc.directions) {
      var directions = document.createElement("a");
      directions.className = "btn btn--secondary btn--sm";
      directions.href = loc.directions;
      directions.target = "_blank";
      directions.rel = "noopener noreferrer";
      directions.appendChild(document.createTextNode("Get directions"));
      var sr = document.createElement("span");
      sr.className = "sr-only";
      sr.textContent = " (opens in a new tab)";
      directions.appendChild(sr);
      wrap.appendChild(directions);
    }

    return wrap;
  }

  function highlightCard(locations, activeId) {
    locations.forEach(function (loc) {
      if (!loc.card) return;
      loc.card.classList.toggle("is-active", loc.id === activeId);
    });
  }

  function pinIcon(name) {
    return L.divIcon({
      className: "loc-marker",
      iconSize: [28, 36],
      iconAnchor: [14, 34],
      popupAnchor: [0, -28],
      html:
        '<span class="loc-marker__pin" aria-hidden="true">' +
        '<svg viewBox="0 0 28 36" width="28" height="36" focusable="false">' +
        '<path fill="#4a2c59" stroke="#9b7ebd" stroke-width="1.5" d="M14 1.5c-6.35 0-11.5 5.05-11.5 11.28 0 8.2 10.2 21.02 10.64 21.56a1.1 1.1 0 0 0 1.72 0C15.3 23.8 25.5 17.48 25.5 12.78 25.5 6.55 20.35 1.5 14 1.5z"/>' +
        '<circle cx="14" cy="12.5" r="4.2" fill="#eadcf8"/>' +
        "</svg></span>"
    });
  }

  function initMap(locations) {
    if (typeof L === "undefined" || !L.map) {
      throw new Error("Leaflet failed to load.");
    }

    const map = L.map(mapEl, {
      scrollWheelZoom: false,
      keyboard: true,
      zoomControl: true,
      attributionControl: true
    });

    L.tileLayer(OSM_TILE_URL, {
      attribution: OSM_ATTRIBUTION,
      maxZoom: 19,
      crossOrigin: true
    }).addTo(map);

    // Enable wheel zoom only while the map is focused, so page scrolling is not hijacked.
    map.once("focus", function () {
      map.scrollWheelZoom.enable();
    });
    map.on("click", function () {
      map.scrollWheelZoom.enable();
    });
    map.on("blur", function () {
      map.scrollWheelZoom.disable();
    });

    const markersById = {};
    const bounds = L.latLngBounds([]);

    locations.forEach(function (loc) {
      const marker = L.marker([loc.lat, loc.lng], {
        icon: pinIcon(loc.name),
        title: "Aetheria Funeral Homes — " + loc.name,
        alt: "Aetheria Funeral Homes — " + loc.name,
        keyboard: true,
        riseOnHover: true
      });

      marker.bindPopup(buildPopup(loc), {
        maxWidth: 280,
        autoPan: true,
        className: "loc-popup"
      });

      marker.on("popupopen", function () {
        highlightCard(locations, loc.id);
        setStatus(loc.name + " selected on the map.");
      });
      marker.on("popupclose", function () {
        if (loc.card && loc.card.classList.contains("is-active")) {
          loc.card.classList.remove("is-active");
        }
      });

      marker.addTo(map);
      markersById[loc.id] = marker;
      bounds.extend([loc.lat, loc.lng]);

      // Make the custom pin keyboard-focusable.
      const iconEl = marker.getElement();
      if (iconEl) {
        iconEl.setAttribute("tabindex", "0");
        iconEl.setAttribute("role", "button");
        iconEl.setAttribute("aria-label", "Aetheria Funeral Homes — " + loc.name);
      }
    });

    if (bounds.isValid()) {
      map.fitBounds(bounds, { padding: [48, 48], maxZoom: 11 });
    }

    function selectFromList(id) {
      const marker = markersById[id];
      if (!marker) return;
      map.panTo(marker.getLatLng());
      if (map.getZoom() < 11) map.setZoom(11);
      marker.openPopup();
    }

    locations.forEach(function (loc) {
      if (!loc.card) return;
      loc.card.addEventListener("click", function (event) {
        if (event.target.closest("a, button")) return;
        selectFromList(loc.id);
      });
      const showBtn = loc.card.querySelector("[data-show-location]");
      if (showBtn) {
        showBtn.addEventListener("click", function (event) {
          event.preventDefault();
          event.stopPropagation();
          selectFromList(loc.id);
          mapEl.scrollIntoView({ behavior: "smooth", block: "nearest" });
        });
      }
    });

    hideFallback();
    if (layoutEl) layoutEl.classList.add("is-interactive");
    setStatus("Map showing all " + locations.length + " Aetheria Funeral Homes locations.");

    // Leaflet needs a size recalc if the container was hidden or fonts shifted.
    requestAnimationFrame(function () {
      map.invalidateSize();
      if (bounds.isValid()) map.fitBounds(bounds, { padding: [48, 48], maxZoom: 11 });
    });
  }

  const locations = readLocations();
  if (!locations.length) {
    showFallback("Location details could not be read from this page. Please use the list below and the Get directions links.");
    return;
  }

  try {
    initMap(locations);
  } catch (err) {
    console.warn("Locations map could not load:", err);
    showFallback("The interactive map could not be loaded. Use the location list below and the Get directions links — they open Google Maps in a new tab.");
    setStatus("The interactive map could not be loaded.");
  }
})();
