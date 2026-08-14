/* Mobile navigation toggle.
 *
 * The markup ships with the panel open and aria-expanded="true" so that a phone
 * with JavaScript disabled still gets a working (if long) nav. This script
 * collapses it on load and takes over the open/close behaviour.
 *
 * Above the breakpoint the panel is always visible and the button is hidden by
 * CSS, so the collapsed state is only applied on small viewports.
 */
(function () {
  var nav = document.querySelector('[data-site-nav]');
  if (!nav) return;

  var toggle = nav.querySelector('[data-nav-toggle]');
  var panel = nav.querySelector('[data-nav-panel]');
  if (!toggle || !panel) return;

  var mq = window.matchMedia('(max-width: 900px)');

  function setOpen(open) {
    toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
    nav.classList.toggle('is-open', open);
  }

  function isOpen() {
    return toggle.getAttribute('aria-expanded') === 'true';
  }

  function sync() {
    // Above the breakpoint the panel is shown by CSS regardless; keep
    // aria-expanded truthful for assistive tech rather than leaving it stale.
    setOpen(!mq.matches);
  }

  toggle.addEventListener('click', function () {
    var next = !isOpen();
    setOpen(next);
    if (next) {
      var first = panel.querySelector('a');
      if (first) first.focus();
    }
  });

  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape' && mq.matches && isOpen()) {
      setOpen(false);
      toggle.focus();
    }
  });

  document.addEventListener('click', function (e) {
    if (!mq.matches || !isOpen()) return;
    if (!nav.contains(e.target)) setOpen(false);
  });

  // Following an in-page link (#contact) should close the panel.
  panel.addEventListener('click', function (e) {
    if (mq.matches && e.target.closest('a')) setOpen(false);
  });

  if (mq.addEventListener) {
    mq.addEventListener('change', sync);
  } else if (mq.addListener) {
    mq.addListener(sync);
  }

  sync();
})();
