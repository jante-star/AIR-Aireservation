/* search_overlay.js — Spot search overlay + Google Maps integration */
(function () {
    'use strict';

    var overlay = document.getElementById('search-overlay');
    var backdrop = document.getElementById('overlay-backdrop');
    var categoryTabs = document.getElementById('category-tabs');
    var mapEl = document.getElementById('spot-map');
    var mapPlaceholder = document.getElementById('map-placeholder');
    var flightSvg = document.getElementById('flight-svg');
    var flightPlane = document.getElementById('flight-plane');

    var map = null;
    var markers = [];
    var mapInitialized = false;
    var flightAnimId = null;
    var currentCat = 'homes';

    // ── Public API ────────────────────────────────────────────────────────────
    window.SpotOverlay = {
        currentCat: currentCat,
        open: open,
        close: close,
        switchCat: switchCat,
        search: doSearch,
        searchFlights: searchFlights,
        previewFlight: previewFlight,
    };

    // ── Open / close ──────────────────────────────────────────────────────────
    function open(cat) {
        currentCat = cat || 'homes';
        window.SpotOverlay.currentCat = currentCat;
        overlay.style.display = 'flex';
        // Allow display to apply before adding transition class
        requestAnimationFrame(function () {
            overlay.classList.add('is-open');
        });
        backdrop.style.display = 'block';
        if (categoryTabs) categoryTabs.classList.add('overlay-active');
        document.body.style.overflow = 'hidden';
        updateOverlayCat(currentCat);
        initMapLazy();
    }

    function close() {
        overlay.classList.remove('is-open');
        backdrop.style.display = 'none';
        if (categoryTabs) categoryTabs.classList.remove('overlay-active');
        document.body.style.overflow = '';
        cancelFlightAnim();
        // Hide after transition completes
        setTimeout(function () {
            if (!overlay.classList.contains('is-open')) {
                overlay.style.display = 'none';
            }
        }, 460);
    }

    // ESC key closes
    document.addEventListener('keydown', function (e) {
        if (e.key === 'Escape') close();
    });

    // ── Category switching ────────────────────────────────────────────────────
    function switchCat(cat) {
        currentCat = cat;
        window.SpotOverlay.currentCat = cat;
        updateOverlayCat(cat);
        if (cat === 'flights') {
            if (flightSvg) flightSvg.style.display = 'none';
            if (flightPlane) flightPlane.style.display = 'none';
        } else {
            loadCategoryPins(cat);
        }
    }

    function updateOverlayCat(cat) {
        // Update pill active states
        document.querySelectorAll('.overlay-cat-pill').forEach(function (p) {
            p.classList.toggle('active', p.dataset.ocat === cat);
        });
        // Show correct fields
        var fieldSets = {
            homes: 'overlay-fields-homes',
            experiences: 'overlay-fields-homes',
            services: 'overlay-fields-homes',
            flights: 'overlay-fields-flights',
            cars: 'overlay-fields-cars',
        };
        ['overlay-fields-homes', 'overlay-fields-flights', 'overlay-fields-cars', 'overlay-fields-generic'].forEach(function (id) {
            var el = document.getElementById(id);
            if (el) el.classList.add('hidden');
        });
        var target = fieldSets[cat] || 'overlay-fields-homes';
        var targetEl = document.getElementById(target);
        if (targetEl) targetEl.classList.remove('hidden');
    }

    // ── Map initialization ────────────────────────────────────────────────────
    function initMapLazy() {
        if (mapInitialized) return;
        var key = window._mapsApiKey;
        if (!key) {
            showMapPlaceholder('Add GOOGLE_MAPS_API_KEY to your .env to enable the interactive map.');
            return;
        }
        if (window.google && window.google.maps) {
            initMap();
            return;
        }
        // Load Maps JS API dynamically
        window._gmapReady = function () {
            initMap();
        };
        var script = document.createElement('script');
        script.src = 'https://maps.googleapis.com/maps/api/js?key=' + key + '&callback=_gmapReady&libraries=places';
        script.async = true;
        script.defer = true;
        script.onerror = function () {
            showMapPlaceholder('Could not load Google Maps. Check your API key and ensure Maps JavaScript API is enabled.');
        };
        document.head.appendChild(script);
    }

    function initMap() {
        if (mapInitialized) return;
        mapInitialized = true;
        if (mapPlaceholder) mapPlaceholder.style.display = 'none';
        map = new google.maps.Map(mapEl, {
            center: { lat: 18.1096, lng: -77.2975 },
            zoom: 9,
            mapTypeControl: false,
            streetViewControl: false,
            fullscreenControl: false,
            styles: getMapStyles(),
        });
        // Try geolocation
        if (navigator.geolocation) {
            navigator.geolocation.getCurrentPosition(function (pos) {
                map.setCenter({ lat: pos.coords.latitude, lng: pos.coords.longitude });
                map.setZoom(10);
            }, null, { timeout: 5000 });
        }
        loadCategoryPins(currentCat);
    }

    function showMapPlaceholder(msg) {
        if (mapPlaceholder) {
            mapPlaceholder.style.display = 'flex';
            var span = mapPlaceholder.querySelector('span');
            if (span && msg) span.textContent = msg;
        }
    }

    // ── Price markers ─────────────────────────────────────────────────────────
    function clearMarkers() {
        markers.forEach(function (m) { m.setMap(null); });
        markers = [];
    }

    function addPriceMarker(lat, lng, price, title, url) {
        var label = price >= 1000 ? '$' + Math.round(price / 1000) + 'k' : '$' + Math.round(price);
        var charW = label.length * 9 + 20;
        var svg = '<svg xmlns="http://www.w3.org/2000/svg" width="' + charW + '" height="32">' +
            '<rect x="0" y="0" width="' + charW + '" height="32" rx="16" fill="#0A0A0A"/>' +
            '<text x="' + (charW / 2) + '" y="20" text-anchor="middle" fill="white" ' +
            'font-family="-apple-system,BlinkMacSystemFont,sans-serif" font-size="13" font-weight="700">' +
            label + '</text></svg>';
        var icon = {
            url: 'data:image/svg+xml;charset=UTF-8,' + encodeURIComponent(svg),
            scaledSize: new google.maps.Size(charW, 32),
            anchor: new google.maps.Point(charW / 2, 32),
        };
        var marker = new google.maps.Marker({
            position: { lat: lat, lng: lng },
            map: map,
            icon: icon,
            title: title,
        });
        var infoWindow = new google.maps.InfoWindow({
            content: '<div style="font-family:system-ui;padding:4px 8px;min-width:160px;">' +
                '<strong style="font-size:14px;">' + title + '</strong><br>' +
                '<span style="color:#666;font-size:13px;">From $' + Math.round(price) + '</span><br>' +
                (url ? '<a href="' + url + '" style="color:#F59E0B;font-size:13px;font-weight:600;">View →</a>' : '') +
                '</div>',
        });
        marker.addListener('click', function () {
            infoWindow.open(map, marker);
        });
        markers.push(marker);
    }

    function loadCategoryPins(cat) {
        if (!map) return;
        clearMarkers();
        // Fetch pins from API
        fetch('/api/search?category=' + cat + '&fmt=json')
            .then(function (r) { return r.json(); })
            .then(function (data) {
                if (!data.pins || !data.pins.length) return;
                data.pins.forEach(function (pin) {
                    addPriceMarker(pin.lat, pin.lng, pin.price, pin.title, pin.url);
                });
                if (data.pins.length > 0) {
                    var bounds = new google.maps.LatLngBounds();
                    data.pins.forEach(function (p) { bounds.extend({ lat: p.lat, lng: p.lng }); });
                    map.fitBounds(bounds, 60);
                }
            })
            .catch(function () { /* no pins available */ });
    }

    // ── Search ────────────────────────────────────────────────────────────────
    function doSearch(cat) {
        var whereEl = document.getElementById('where-' + cat) || document.getElementById('where-homes') || document.getElementById('where-generic');
        var city = whereEl ? whereEl.value.trim() : '';
        if (cat === 'cars') {
            var whereC = document.getElementById('where-cars');
            city = whereC ? whereC.value.trim() : '';
        }
        var url = '/' + cat + '/';
        if (city) url += '?city=' + encodeURIComponent(city);
        // Pan map first if we have Google Maps
        if (map && city) {
            var geocoder = new google.maps.Geocoder();
            geocoder.geocode({ address: city }, function (results, status) {
                if (status === 'OK' && results[0]) {
                    map.panTo(results[0].geometry.location);
                    map.setZoom(11);
                }
            });
            setTimeout(function () { window.location.href = url; }, 800);
        } else {
            window.location.href = url;
        }
    }

    function searchFlights() {
        var from = document.getElementById('from-flights');
        var to = document.getElementById('to-flights');
        var fromVal = from ? from.value.trim() : '';
        var toVal = to ? to.value.trim() : '';
        if (fromVal && toVal && map) {
            geocodeAndDrawArc(fromVal, toVal);
        }
        var url = '/flights/?from=' + encodeURIComponent(fromVal) + '&to=' + encodeURIComponent(toVal);
        setTimeout(function () { window.location.href = url; }, toVal ? 1500 : 0);
    }

    // ── Flight arc ────────────────────────────────────────────────────────────
    function previewFlight(originLat, originLng, destLat, destLng) {
        open('flights');
        setTimeout(function () {
            if (map) {
                drawFlightArc(originLat, originLng, destLat, destLng);
            } else {
                // Wait for map init
                var check = setInterval(function () {
                    if (map) {
                        clearInterval(check);
                        drawFlightArc(originLat, originLng, destLat, destLng);
                    }
                }, 200);
            }
        }, 500);
    }

    function geocodeAndDrawArc(fromCity, toCity) {
        if (!map || !window.google) return;
        var geocoder = new google.maps.Geocoder();
        geocoder.geocode({ address: fromCity }, function (r1, s1) {
            if (s1 !== 'OK') return;
            geocoder.geocode({ address: toCity }, function (r2, s2) {
                if (s2 !== 'OK') return;
                var loc1 = r1[0].geometry.location;
                var loc2 = r2[0].geometry.location;
                drawFlightArc(loc1.lat(), loc1.lng(), loc2.lat(), loc2.lng());
            });
        });
    }

    function drawFlightArc(oLat, oLng, dLat, dLng) {
        if (!map) return;
        cancelFlightAnim();
        clearMarkers();

        var origin = { lat: oLat, lng: oLng };
        var dest = { lat: dLat, lng: dLng };

        // Fit map to show both points
        var bounds = new google.maps.LatLngBounds();
        bounds.extend(origin);
        bounds.extend(dest);
        map.fitBounds(bounds, 80);

        // Origin marker (yellow)
        var oSvg = '<svg xmlns="http://www.w3.org/2000/svg" width="40" height="40"><circle cx="20" cy="20" r="14" fill="#F59E0B"/><text x="20" y="26" text-anchor="middle" font-size="16">🛫</text></svg>';
        var dSvg = '<svg xmlns="http://www.w3.org/2000/svg" width="40" height="40"><circle cx="20" cy="20" r="14" fill="#EF4444"/><text x="20" y="26" text-anchor="middle" font-size="16">🛬</text></svg>';
        var oMarker = new google.maps.Marker({ position: origin, map: map, icon: { url: 'data:image/svg+xml;charset=UTF-8,' + encodeURIComponent(oSvg), scaledSize: new google.maps.Size(40, 40), anchor: new google.maps.Point(20, 20) } });
        var dMarker = new google.maps.Marker({ position: dest, map: map, icon: { url: 'data:image/svg+xml;charset=UTF-8,' + encodeURIComponent(dSvg), scaledSize: new google.maps.Size(40, 40), anchor: new google.maps.Point(20, 20) } });
        markers.push(oMarker, dMarker);

        // Draw geodesic arc polyline
        var arcPoints = computeArc(oLat, oLng, dLat, dLng, 50);
        var polyline = new google.maps.Polyline({
            path: arcPoints,
            geodesic: false,
            strokeColor: '#F59E0B',
            strokeOpacity: 0,
            strokeWeight: 3,
            icons: [{ icon: { path: 'M 0,-1 0,1', strokeOpacity: 1, scale: 3 }, offset: '0', repeat: '12px' }],
            map: map,
        });
        markers.push(polyline);

        // Animate plane along arc
        animatePlane(arcPoints);
    }

    function computeArc(oLat, oLng, dLat, dLng, steps) {
        var pts = [];
        for (var i = 0; i <= steps; i++) {
            var t = i / steps;
            var lat = oLat + (dLat - oLat) * t;
            var lng = oLng + (dLng - oLng) * t;
            // Add curve: midpoint offset
            var curve = Math.sin(Math.PI * t) * 5;
            var midLat = (oLat + dLat) / 2;
            var midLng = (oLng + dLng) / 2;
            var perpLat = -(dLng - oLng) / Math.sqrt(Math.pow(dLat - oLat, 2) + Math.pow(dLng - oLng, 2));
            var perpLng = (dLat - oLat) / Math.sqrt(Math.pow(dLat - oLat, 2) + Math.pow(dLng - oLng, 2));
            lat += perpLat * curve;
            lng += perpLng * curve;
            pts.push({ lat: lat, lng: lng });
        }
        return pts;
    }

    function animatePlane(arcPoints) {
        if (!flightPlane) return;
        flightPlane.style.display = 'block';
        var step = 0;
        var total = arcPoints.length;

        function tick() {
            if (step >= total - 1) {
                step = 0;
            }
            var pt = arcPoints[step];
            var nextPt = arcPoints[Math.min(step + 1, total - 1)];
            var px = latLngToPixel(pt.lat, pt.lng);
            if (px) {
                flightPlane.style.left = (px.x - 12) + 'px';
                flightPlane.style.top = (px.y - 12) + 'px';
                // Rotate plane toward next point
                var nextPx = latLngToPixel(nextPt.lat, nextPt.lng);
                if (nextPx) {
                    var angle = Math.atan2(nextPx.y - px.y, nextPx.x - px.x) * 180 / Math.PI;
                    flightPlane.style.transform = 'rotate(' + angle + 'deg)';
                }
                flightPlane.style.display = 'block';
            }
            step++;
            flightAnimId = requestAnimationFrame(function () {
                setTimeout(tick, 30);
            });
        }
        tick();
    }

    function latLngToPixel(lat, lng) {
        if (!map) return null;
        var proj = map.getProjection();
        if (!proj) return null;
        var bounds = map.getBounds();
        if (!bounds) return null;
        var topRight = proj.fromLatLngToPoint(bounds.getNorthEast());
        var bottomLeft = proj.fromLatLngToPoint(bounds.getSouthWest());
        var scale = Math.pow(2, map.getZoom());
        var worldPoint = proj.fromLatLngToPoint(new google.maps.LatLng(lat, lng));
        var mapDiv = mapEl;
        return {
            x: (worldPoint.x - bottomLeft.x) * scale,
            y: (worldPoint.y - topRight.y) * scale,
        };
    }

    function cancelFlightAnim() {
        if (flightAnimId) {
            cancelAnimationFrame(flightAnimId);
            flightAnimId = null;
        }
        if (flightPlane) flightPlane.style.display = 'none';
    }

    // ── Map styles (clean minimal) ────────────────────────────────────────────
    function getMapStyles() {
        var isDark = document.documentElement.getAttribute('data-theme') === 'dark';
        if (!isDark) return [];
        return [
            { elementType: 'geometry', stylers: [{ color: '#1a1a1a' }] },
            { elementType: 'labels.text.stroke', stylers: [{ color: '#1a1a1a' }] },
            { elementType: 'labels.text.fill', stylers: [{ color: '#9ca3af' }] },
            { featureType: 'road', elementType: 'geometry', stylers: [{ color: '#2a2a2a' }] },
            { featureType: 'road', elementType: 'geometry.stroke', stylers: [{ color: '#111' }] },
            { featureType: 'water', elementType: 'geometry', stylers: [{ color: '#0f172a' }] },
            { featureType: 'poi', stylers: [{ visibility: 'off' }] },
        ];
    }

    // ── Scroll row drag-to-scroll ─────────────────────────────────────────────
    document.querySelectorAll('.scroll-row').forEach(function (row) {
        var isDown = false;
        var startX, scrollLeft;
        row.addEventListener('mousedown', function (e) {
            isDown = true;
            row.classList.add('dragging');
            startX = e.pageX - row.offsetLeft;
            scrollLeft = row.scrollLeft;
        });
        row.addEventListener('mouseleave', function () { isDown = false; row.classList.remove('dragging'); });
        row.addEventListener('mouseup', function () { isDown = false; row.classList.remove('dragging'); });
        row.addEventListener('mousemove', function (e) {
            if (!isDown) return;
            e.preventDefault();
            var x = e.pageX - row.offsetLeft;
            var walk = (x - startX) * 1.5;
            row.scrollLeft = scrollLeft - walk;
        });
    });

    // ── Recently viewed ───────────────────────────────────────────────────────
    window.SpotRecent = {
        save: function (listing, ltype) {
            try {
                var key = 'spot_recent';
                var list = JSON.parse(localStorage.getItem(key) || '[]');
                list = list.filter(function (r) { return r.id !== listing.id; });
                list.unshift({ id: listing.id, title: listing.title, price: listing.price || listing.ticketPrice || 0, ltype: ltype, location: listing.location || {} });
                localStorage.setItem(key, JSON.stringify(list.slice(0, 10)));
            } catch (e) {}
        },
        render: function () {
            try {
                var list = JSON.parse(localStorage.getItem('spot_recent') || '[]');
                var section = document.getElementById('recently-viewed-section');
                var row = document.getElementById('recently-viewed-row');
                if (!list.length || !section || !row) return;
                row.innerHTML = list.map(function (r) {
                    return '<a href="/' + r.ltype + 's/' + r.id + '" class="spot-card" style="width:220px;">' +
                        '<div class="spot-card-img-placeholder" style="height:140px;font-size:40px;">🏠</div>' +
                        '<div class="spot-card-body"><div class="spot-card-title">' + r.title + '</div>' +
                        '<div class="spot-card-location">' + (r.location.city || '') + '</div>' +
                        '<div class="spot-card-price">$' + Math.round(r.price) + '</div></div></a>';
                }).join('');
                section.style.display = 'block';
            } catch (e) {}
        },
    };

    // Render recently viewed on page load
    document.addEventListener('DOMContentLoaded', function () {
        if (window.SpotRecent) window.SpotRecent.render();
    });

})();
