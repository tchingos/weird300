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

  var accent = getComputedStyle(document.documentElement).getPropertyValue('--accent').trim();
  var points = places.map(function (p) {
    var marker = L.circleMarker([p.lat, p.lng], {
      radius: 8, color: '#fff', weight: 2, fillColor: accent, fillOpacity: 1
    }).addTo(map);
    var link = document.createElement('a');
    link.href = p.url;
    link.textContent = p.title;
    marker.bindPopup(link);
    return [p.lat, p.lng];
  });

  if (points.length === 1) map.setView(points[0], 11);
  else if (points.length) map.fitBounds(points, { padding: [40, 40], maxZoom: 10 });
  else map.setView([54.8, -3.5], 5); // the whole of Britain
})();
