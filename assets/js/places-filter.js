// Search, category chips and a timeline view for the Places page.
// The page is server-rendered as category sections; this script reads the
// data attributes on each card's <li>, then regroups the cards for the chosen
// view and filters. Without JavaScript the server-rendered sections stay.
(function () {
  "use strict";

  var controls = document.getElementById("places-filter");
  var results = document.getElementById("places-results");
  var empty = document.getElementById("places-empty");
  if (!controls || !results || !empty) return;

  var search = document.getElementById("places-search");
  var count = controls.querySelector(".filter-count");
  var chips = [].slice.call(controls.querySelectorAll(".chip"));
  var viewButtons = [].slice.call(controls.querySelectorAll(".filter-view"));
  var clear = document.getElementById("places-clear");

  // Category names in the book's order, taken from the chips.
  var categories = chips
    .map(function (chip) { return chip.getAttribute("data-category"); })
    .filter(function (name) { return name; });

  // Every card, collected once, newest visit first.
  var items = [].slice.call(results.querySelectorAll("li[data-category]")).map(function (li, index) {
    return {
      el: li,
      index: index,
      category: li.getAttribute("data-category"),
      visited: li.getAttribute("data-visited") || "",
      text: li.getAttribute("data-search") || ""
    };
  });
  items.sort(function (a, b) {
    if (a.visited !== b.visited) return a.visited < b.visited ? 1 : -1;
    return a.index - b.index;
  });

  var state = { view: "category", category: "", q: "" };

  function readUrl() {
    var params = new URLSearchParams(window.location.search);
    state.view = params.get("view") === "timeline" ? "timeline" : "category";
    var category = params.get("category") || "";
    state.category = categories.indexOf(category) === -1 ? "" : category;
    state.q = params.get("q") || "";
  }

  function writeUrl() {
    var params = new URLSearchParams(window.location.search);
    params.delete("view");
    params.delete("category");
    params.delete("q");
    if (state.view === "timeline") params.set("view", "timeline");
    if (state.category) params.set("category", state.category);
    if (state.q.trim()) params.set("q", state.q.trim());
    var query = params.toString();
    var url = window.location.pathname + (query ? "?" + query : "") + window.location.hash;
    window.history.replaceState(null, "", url);
  }

  function matchesSearch(item, words) {
    for (var i = 0; i < words.length; i++) {
      if (item.text.indexOf(words[i]) === -1) return false;
    }
    return true;
  }

  function plural(n) {
    return n + (n === 1 ? " place" : " places");
  }

  function section(title, number, list) {
    var el = document.createElement("section");
    el.className = "category";
    var heading = document.createElement("h2");
    heading.className = "section-title";
    heading.appendChild(document.createTextNode(title + " "));
    var span = document.createElement("span");
    span.textContent = number;
    heading.appendChild(span);
    var ul = document.createElement("ul");
    ul.className = "cards";
    list.forEach(function (item) { ul.appendChild(item.el); });
    el.appendChild(heading);
    el.appendChild(ul);
    return el;
  }

  function render() {
    var words = state.q.toLowerCase().split(/\s+/).filter(function (w) { return w; });
    var searched = items.filter(function (item) { return matchesSearch(item, words); });
    var shown = searched.filter(function (item) {
      return !state.category || item.category === state.category;
    });

    // Chip counts follow the search, so each chip says what it would show.
    chips.forEach(function (chip) {
      var name = chip.getAttribute("data-category");
      var n = name ? searched.filter(function (item) { return item.category === name; }).length : searched.length;
      chip.querySelector(".chip-count").textContent = n;
      chip.classList.toggle("is-empty", n === 0);
      chip.setAttribute("aria-pressed", name === state.category ? "true" : "false");
    });
    viewButtons.forEach(function (button) {
      button.setAttribute("aria-pressed", button.getAttribute("data-view") === state.view ? "true" : "false");
    });

    var fragment = document.createDocumentFragment();
    if (state.view === "timeline") {
      var years = [];
      var byYear = {};
      shown.forEach(function (item) {
        var year = item.visited.slice(0, 4) || "Undated";
        if (!byYear[year]) { byYear[year] = []; years.push(year); }
        byYear[year].push(item);
      });
      years.forEach(function (year) {
        fragment.appendChild(section(year, byYear[year].length, byYear[year]));
      });
    } else {
      categories.forEach(function (name) {
        var list = shown.filter(function (item) { return item.category === name; });
        if (list.length) fragment.appendChild(section(name, list.length, list));
      });
    }

    results.innerHTML = "";
    results.appendChild(fragment);
    results.classList.toggle("is-timeline", state.view === "timeline");
    count.textContent = plural(shown.length);
    empty.hidden = shown.length > 0;
  }

  function update() {
    render();
    writeUrl();
  }

  chips.forEach(function (chip) {
    chip.addEventListener("click", function () {
      state.category = chip.getAttribute("data-category");
      update();
    });
  });
  viewButtons.forEach(function (button) {
    button.addEventListener("click", function () {
      state.view = button.getAttribute("data-view");
      update();
    });
  });
  search.addEventListener("input", function () {
    state.q = search.value;
    update();
  });
  clear.addEventListener("click", function () {
    state.category = "";
    state.q = "";
    search.value = "";
    update();
    search.focus();
  });

  readUrl();
  search.value = state.q;
  controls.hidden = false;
  render();
})();
