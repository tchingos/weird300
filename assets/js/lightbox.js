// Opens any link marked data-lightbox (rendered by _includes/photo.html) in a
// full-screen viewer. All such links on the page form one set, in page order.
(function () {
  var links = Array.prototype.slice.call(document.querySelectorAll('a[data-lightbox]'));
  if (!links.length || !window.HTMLDialogElement) return;

  var dialog = document.createElement('dialog');
  dialog.className = 'lightbox';
  dialog.setAttribute('aria-label', 'Photo viewer');
  var icon = function (path) {
    return '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" ' +
      'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="' + path + '"/></svg>';
  };
  dialog.innerHTML =
    '<figure><img alt=""><figcaption></figcaption></figure>' +
    '<p class="lightbox-count" aria-live="polite"></p>' +
    '<button class="lightbox-close" type="button" aria-label="Close">' + icon('M6 6l12 12M18 6L6 18') + '</button>' +
    '<button class="lightbox-prev" type="button" aria-label="Previous photo">' + icon('M15 5l-7 7 7 7') + '</button>' +
    '<button class="lightbox-next" type="button" aria-label="Next photo">' + icon('M9 5l7 7-7 7') + '</button>';
  document.body.appendChild(dialog);

  var img = dialog.querySelector('img');
  var caption = dialog.querySelector('figcaption');
  var count = dialog.querySelector('.lightbox-count');
  var current = 0;

  function show(i) {
    current = (i + links.length) % links.length;
    var link = links[current];
    img.src = link.href;
    img.alt = link.dataset.caption || '';
    caption.textContent = link.dataset.caption || '';
    count.textContent = links.length > 1 ? (current + 1) + ' / ' + links.length : '';
  }

  function open(i) {
    show(i);
    dialog.showModal();
    document.documentElement.classList.add('lightbox-open');
  }

  dialog.addEventListener('close', function () {
    document.documentElement.classList.remove('lightbox-open');
    links[current].focus();
  });

  links.forEach(function (link, i) {
    link.addEventListener('click', function (e) {
      e.preventDefault();
      open(i);
    });
  });

  dialog.classList.toggle('lightbox-single', links.length === 1);
  dialog.querySelector('.lightbox-close').addEventListener('click', function () { dialog.close(); });
  dialog.querySelector('.lightbox-prev').addEventListener('click', function () { show(current - 1); });
  dialog.querySelector('.lightbox-next').addEventListener('click', function () { show(current + 1); });

  // A click on the dark backdrop (not the photo or a button) closes it.
  dialog.addEventListener('click', function (e) {
    if (e.target === dialog || e.target.tagName === 'FIGURE') dialog.close();
  });

  dialog.addEventListener('keydown', function (e) {
    if (e.key === 'ArrowLeft') show(current - 1);
    if (e.key === 'ArrowRight') show(current + 1);
  });

  var touchX = null;
  dialog.addEventListener('touchstart', function (e) { touchX = e.touches[0].clientX; }, { passive: true });
  dialog.addEventListener('touchend', function (e) {
    if (touchX === null) return;
    var dx = e.changedTouches[0].clientX - touchX;
    if (Math.abs(dx) > 50) show(current + (dx < 0 ? 1 : -1));
    touchX = null;
  });
})();
