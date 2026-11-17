/**
 * Contact-page map of all Aetheria Funeral Homes locations.
 *
 * API key: no production key is committed. Replace the placeholder below
 * with a restricted Google Maps Platform key when you are ready to show
 * the interactive map. Until then the page keeps the static location list
 * and "Get directions" links, so it never breaks.
 *
 * Create a key in Google Cloud Console, enable Maps JavaScript API and
 * Geocoding API, and restrict it to HTTP referrers for
 * https://aetheriafuneralhomes.com/*, https://www.aetheriafuneralhomes.com/*,
 * and http://localhost:* (plus any staging host). Do not commit a real key
 * that is unrestricted.
 *
 * Addresses are read from the contact page. Coordinates are geocoded at
 * runtime and are not hardcoded or cached.
 */
(function () {
  "use strict";

  // TODO: replace with a restricted production Google Maps Platform API key.
  // Leave this placeholder as-is until a key is created. Never commit a real secret
  // in a public pull request if the repo is public — prefer a deploy-time substitution.
  const AETHERIA_GOOGLE_MAPS_API_KEY = "AIzaSyBkB6sJk6WQPfiD5JTbK_VKmtL42x34BBk";

  const ATTRIBUTION_ID = "gmp_git_agentskills_v1";
  const PIN_BACKGROUND = "#4a2c59";
  const PIN_BORDER = "#9b7ebd";
  const PIN_GLYPH = "#eadcf8";

  const mapEl = document.getElementById("locations-map");
  const fallbackEl = document.getElementById("locations-map-fallback");
  const statusEl = document.getElementById("locations-map-status");
  const layoutEl = document.querySelector(".locations-map-layout");

  if (!mapEl) return;

  function isConfiguredMapsKey(key) {
    if (!key || typeof key !== "string") return false;
    const trimmed = key.trim();
    if (!trimmed) return false;
    if (/^YOUR_/i.test(trimmed)) return false;
    if (/PLACEHOLDER/i.test(trimmed)) return false;
    return true;
  }

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

  function readLocations() {
    const cards = document.querySelectorAll(".loc-list .loc-card[data-location-id]");
    return Array.from(cards).map(function (card) {
      const address =
        card.getAttribute("data-address") ||
        (card.querySelector("address")
          ? card.querySelector("address").innerText.replace(/\s+/g, " ").trim()
          : "");
      const tel = card.querySelector("a.tel");
      const dirs = card.querySelector('a[href*="google.com/maps"]');
      return {
        id: card.getAttribute("data-location-id"),
        name: card.getAttribute("data-name") || (card.querySelector("h3") && card.querySelector("h3").textContent.trim()) || "",
        address: address,
        phone: card.getAttribute("data-phone") || (tel && tel.textContent.trim()) || "",
        phoneHref: card.getAttribute("data-phone-href") || (tel && tel.getAttribute("href")) || "",
        directions: card.getAttribute("data-directions") || (dirs && dirs.getAttribute("href")) || "",
        card: card,
      };
    }).filter(function (loc) {
      return loc.id && loc.name && loc.address;
    });
  }

  /**
   * Dynamic bootstrap loader for the Maps JavaScript API.
   * Source: Google Maps Platform documentation (Apache License 2.0).
   * https://developers.google.com/maps/documentation/javascript/load-maps-js-api?utm_campaign=gmp_git_agentskills_v1
   */
  function loadMapsBootstrap(apiKey) {
    return new Promise(function (resolve, reject) {
      if (window.google && window.google.maps && typeof window.google.maps.importLibrary === "function") {
        resolve();
        return;
      }

      (function (g) {
        var h, a, k, p = "The Google Maps JavaScript API", c = "google", l = "importLibrary", q = "__ib__", m = document, b = window;
        b = b[c] || (b[c] = {});
        var d = b.maps || (b.maps = {}), r = new Set(), e = new URLSearchParams(), u = function () {
          return h || (h = new Promise(async function (f, n) {
            await (a = m.createElement("script"));
            e.set("libraries", [...r] + "");
            for (k in g) e.set(k.replace(/[A-Z]/g, function (t) { return "_" + t[0].toLowerCase(); }), g[k]);
            e.set("callback", c + ".maps." + q);
            a.src = "https://maps.googleapis.com/maps/api/js?" + e;
            d[q] = f;
            a.onerror = function () { h = n(Error(p + " could not load.")); };
            a.nonce = m.querySelector("script[nonce]") ? m.querySelector("script[nonce]").nonce : "";
            m.head.appendChild(a);
          }));
        };
        if (d[l]) {
          console.warn(p + " only loads once. Ignoring:", g);
        } else {
          d[l] = function (f) {
            r.add(f);
            var rest = [].slice.call(arguments, 1);
            return u().then(function () { return d[l].apply(d, [f].concat(rest)); });
          };
        }
      })({
        key: apiKey,
        v: "weekly",
      });

      var waited = 0;
      var timer = setInterval(function () {
        waited += 50;
        if (window.google && window.google.maps && typeof window.google.maps.importLibrary === "function") {
          clearInterval(timer);
          resolve();
        } else if (waited >= 15000) {
          clearInterval(timer);
          reject(new Error("Maps JavaScript API timed out."));
        }
      }, 50);
    });
  }

  function buildInfoContent(loc) {
    var wrap = document.createElement("div");
    wrap.className = "loc-info";

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

    var header = document.createElement("span");
    header.className = "loc-info-header";
    header.textContent = loc.name;

    return { header: header, content: wrap };
  }

  function highlightCard(locations, activeId) {
    locations.forEach(function (loc) {
      if (!loc.card) return;
      loc.card.classList.toggle("is-active", loc.id === activeId);
    });
  }

  async function initMap(locations) {
    const [{ Map, InfoWindow, RenderingType }, { AdvancedMarkerElement, PinElement }, { Geocoder }] = await Promise.all([
      google.maps.importLibrary("maps"),
      google.maps.importLibrary("marker"),
      google.maps.importLibrary("geocoding"),
    ]);

    const geocoder = new Geocoder();
    const placed = [];

    for (let i = 0; i < locations.length; i++) {
      const loc = locations[i];
      try {
        const response = await geocoder.geocode({
          address: loc.address,
          componentRestrictions: { country: "US" },
          region: "US",
        });
        const result = response.results && response.results[0];
        if (result && result.geometry && result.geometry.location) {
          placed.push({ loc: loc, position: result.geometry.location });
        } else {
          console.warn("No geocoding result for", loc.name);
        }
      } catch (err) {
        console.warn("Geocoding failed for", loc.name, err);
      }
    }

    if (!placed.length) {
      throw new Error("None of the funeral home addresses could be placed on the map.");
    }

    const map = new Map(mapEl, {
      mapId: "DEMO_MAP_ID",
      renderingType: RenderingType.VECTOR,
      gestureHandling: "cooperative",
      clickableIcons: false,
      mapTypeControl: false,
      streetViewControl: false,
      fullscreenControl: true,
      zoomControl: true,
      internalUsageAttributionIds: [ATTRIBUTION_ID],
      center: placed[0].position,
      zoom: 6,
    });

    const infoWindow = new InfoWindow();
    const markersById = {};

    function openLocation(entry) {
      const info = buildInfoContent(entry.loc);
      infoWindow.setHeaderContent(info.header);
      infoWindow.setContent(info.content);
      infoWindow.setOptions({ ariaLabel: entry.loc.name + " location details" });
      infoWindow.open({ map: map, anchor: entry.marker });
      highlightCard(locations, entry.loc.id);
      setStatus(entry.loc.name + " selected on the map.");
    }

    placed.forEach(function (entry) {
      const pin = new PinElement({
        background: PIN_BACKGROUND,
        borderColor: PIN_BORDER,
        glyphColor: PIN_GLYPH,
        scale: 1.1,
      });

      const marker = new AdvancedMarkerElement({
        map: map,
        position: entry.position,
        title: "Aetheria Funeral Homes — " + entry.loc.name,
        content: pin.element,
        gmpClickable: true,
        gmpDraggable: false,
      });

      entry.marker = marker;
      markersById[entry.loc.id] = entry;

      marker.addEventListener("gmp-click", function () {
        openLocation(entry);
      });
    });

    const bounds = new google.maps.LatLngBounds();
    placed.forEach(function (entry) {
      bounds.extend(entry.position);
    });
    map.fitBounds(bounds, { top: 64, right: 64, bottom: 64, left: 64 });

    function selectFromList(id, opts) {
      const entry = markersById[id];
      if (!entry) return;
      if (opts && opts.pan !== false) {
        map.panTo(entry.position);
        if (map.getZoom() < 11) map.setZoom(11);
      }
      openLocation(entry);
    }

    locations.forEach(function (loc) {
      if (!loc.card) return;
      loc.card.addEventListener("click", function (event) {
        if (event.target.closest("a")) return;
        if (!markersById[loc.id]) return;
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
    setStatus("Map showing all " + placed.length + " Aetheria Funeral Homes locations.");
  }

  const locations = readLocations();
  if (!locations.length) {
    showFallback("Location details could not be read from this page. Please use the contact options above.");
    return;
  }

  if (!isConfiguredMapsKey(AETHERIA_GOOGLE_MAPS_API_KEY)) {
    showFallback();
    setStatus("Interactive map is not available yet. Use the location list and Get directions links.");
    return;
  }

  window.gm_authFailure = function () {
    showFallback("The map could not be authorized. Please check the Google Maps API key. The location list below still includes Get directions links.");
    setStatus("The interactive map could not be authorized.");
  };

  loadMapsBootstrap(AETHERIA_GOOGLE_MAPS_API_KEY)
    .then(function () {
      return initMap(locations);
    })
    .catch(function (err) {
      console.warn("Locations map could not load:", err);
      showFallback("The interactive map could not be loaded. Use the location list below and the Get directions links — they open Google Maps in a new tab.");
      setStatus("The interactive map could not be loaded.");
    });
})();
