// Obituaries index: client-side search, location filter, sort, progressive "show more".
(function () {
  var grid = document.getElementById('obit-grid');
  if (!grid) return;
  var cards = Array.prototype.slice.call(grid.querySelectorAll('.obit-card'));
  var input = document.getElementById('obit-search');
  var sortSel = document.getElementById('obit-sort');
  var chips = Array.prototype.slice.call(document.querySelectorAll('.chip[data-loc]'));
  var meta = document.getElementById('obit-count');
  var more = document.getElementById('obit-more');
  var empty = document.getElementById('obit-empty');
  var PAGE = 24, limit = PAGE, loc = 'all';

  function norm(s) { return (s || '').normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLowerCase().trim(); }
  cards.forEach(function (c) { c._name = norm(c.getAttribute('data-name')); });

  function sortCards() {
    var mode = sortSel.value;
    cards.sort(function (a, b) {
      if (mode === 'name') return a._name.localeCompare(b._name);
      var da = +a.getAttribute('data-death'), db = +b.getAttribute('data-death');
      if (da === db) return (+b.getAttribute('data-pub')) - (+a.getAttribute('data-pub'));
      return mode === 'oldest' ? da - db : db - da;
    });
    cards.forEach(function (c) { grid.appendChild(c); });
  }

  function apply() {
    var q = norm(input.value);
    var terms = q ? q.split(/\s+/) : [];
    var matched = 0;
    cards.forEach(function (c) {
      var ok = (loc === 'all' || c.getAttribute('data-loc') === loc) &&
        terms.every(function (t) { return c._name.indexOf(t) !== -1; });
      if (ok) { matched++; c.hidden = matched > limit; } else { c.hidden = true; }
    });
    var shown = Math.min(matched, limit);
    meta.textContent = matched === cards.length && !q && loc === 'all'
      ? 'Showing ' + shown + ' of ' + cards.length + ' obituaries, newest first'
      : 'Showing ' + shown + ' of ' + matched + ' matching obituaries';
    more.hidden = matched <= limit;
    empty.hidden = matched !== 0;
  }

  input.addEventListener('input', function () { limit = PAGE; apply(); });
  sortSel.addEventListener('change', function () { sortCards(); apply(); });
  chips.forEach(function (ch) {
    ch.addEventListener('click', function () {
      chips.forEach(function (o) { o.setAttribute('aria-pressed', 'false'); });
      ch.setAttribute('aria-pressed', 'true');
      loc = ch.getAttribute('data-loc'); limit = PAGE; apply();
    });
  });
  more.addEventListener('click', function () { limit += PAGE * 2; apply(); });
  var params = new URLSearchParams(location.search);
  if (params.get('q')) input.value = params.get('q');
  sortCards(); apply();
})();
