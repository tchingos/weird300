// Draws a Leaflet map into #map from the JSON array in its data-places
// attribute (rendered by _includes/places-map.html).
(function () {
  var el = document.getElementById('map');
  if (!el || !window.L) return;

  var places = JSON.parse(el.dataset.places || '[]');
  var map = L.map(el, { scrollWheelZoom: false });
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 18,
    attribution: '&copy; OpenStreetMap contributors'
  }).addTo(map);

  function fills() {
    var style = getComputedStyle(document.documentElement);
    return {
      place: style.getPropertyValue('--accent').trim(),
      post: style.getPropertyValue('--journal').trim()
    };
  }

  var fill = fills();
  var pins = [];
  var points = places.map(function (p) {
    var marker = L.circleMarker([p.lat, p.lng], {
      radius: 8, color: '#fff', weight: 2, fillColor: fill[p.kind], fillOpacity: 1
    }).addTo(map);
    pins.push({ marker: marker, kind: p.kind });
    var link = document.createElement('a');
    link.href = p.url;
    link.textContent = p.title;
    marker.bindPopup(link);
    return [p.lat, p.lng];
  });

  // The light/dark switch fires this (assets/js/theme.js).
  document.addEventListener('weird300:theme', function () {
    var fresh = fills();
    pins.forEach(function (pin) { pin.marker.setStyle({ fillColor: fresh[pin.kind] }); });
  });

  if (points.length === 1) map.setView(points[0], 11);
  else if (points.length) map.fitBounds(points, { padding: [40, 40], maxZoom: 10 });
  else map.setView([54.8, -3.5], 5); // the whole of Britain
})();
