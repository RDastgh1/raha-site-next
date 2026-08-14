/* Client-side filter for the publications index.
 *
 * Progressive enhancement: the form ships with `hidden` set, so if this script
 * never runs the page is exactly the full, unfiltered list it was before.
 * Matching is done against a pre-rendered data-search attribute (title,
 * authors, venue, year) so there is no per-keystroke DOM text extraction.
 */
(function () {
  var form = document.querySelector('[data-pub-filter]');
  if (!form) return;

  var input = form.querySelector('[data-pub-search]');
  var count = form.querySelector('[data-pub-count]');
  var items = Array.prototype.slice.call(document.querySelectorAll('[data-pub-item]'));
  var sections = Array.prototype.slice.call(document.querySelectorAll('[data-pub-section]'));
  if (!input || !items.length) return;

  form.hidden = false;
  form.addEventListener('submit', function (e) { e.preventDefault(); });

  var total = items.length;

  function apply() {
    var q = input.value.trim().toLowerCase();
    var terms = q ? q.split(/\s+/) : [];
    var shown = 0;

    items.forEach(function (el) {
      var hay = el.getAttribute('data-search') || '';
      var hit = terms.every(function (t) { return hay.indexOf(t) !== -1; });
      el.hidden = !hit;
      if (hit) shown++;
    });

    // Hide a tier heading entirely when nothing in it survived the filter.
    sections.forEach(function (sec) {
      var any = sec.querySelector('[data-pub-item]:not([hidden])');
      sec.hidden = !any;
    });

    if (!terms.length) {
      count.textContent = total + ' publications';
    } else if (shown === 0) {
      count.textContent = 'No publications match “' + input.value.trim() + '”';
    } else {
      count.textContent = shown + ' of ' + total + ' publications';
    }
  }

  var pending;
  input.addEventListener('input', function () {
    window.clearTimeout(pending);
    pending = window.setTimeout(apply, 80);
  });
  input.addEventListener('search', apply);

  apply();
})();
