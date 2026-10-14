// Light and dark switching for the header button (_includes/theme-toggle.html).
//
// Loaded synchronously in <head> on purpose: deferring it would let the light
// palette paint for a frame before a dark visitor's saved choice took effect.
// With no saved choice the CSS follows the system setting on its own, so all
// this file has to carry is an explicit one.
(function () {
  'use strict';

  var KEY = 'weird300-theme';
  var root = document.documentElement;

  function saved() {
    try {
      return localStorage.getItem(KEY);
    } catch (e) {
      return null; // private browsing, or storage switched off
    }
  }

  var chosen = saved();
  if (chosen === 'dark' || chosen === 'light') root.setAttribute('data-theme', chosen);

  function current() {
    return root.getAttribute('data-theme') ||
      (window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light');
  }

  document.addEventListener('DOMContentLoaded', function () {
    var button = document.getElementById('theme-toggle');
    if (!button) return;

    function label() {
      button.setAttribute('aria-label', 'Switch to ' + (current() === 'dark' ? 'light' : 'dark') + ' theme');
    }

    // Revealed only now, so a visitor with no JavaScript is never shown a
    // control that cannot work.
    button.hidden = false;
    label();

    button.addEventListener('click', function () {
      var next = current() === 'dark' ? 'light' : 'dark';
      root.setAttribute('data-theme', next);
      try {
        localStorage.setItem(KEY, next);
      } catch (e) {
        // The choice still applies to this page view.
      }
      label();
      // The map draws its pins from the tokens once, at load, so it needs
      // telling (assets/js/map.js).
      document.dispatchEvent(new CustomEvent('weird300:theme', { detail: next }));
    });
  });
})();
