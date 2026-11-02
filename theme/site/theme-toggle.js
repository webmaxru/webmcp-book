/* Light/dark theme toggle (contract kept from the APM book's theme-toggle.js).
 * - The choice is stored in localStorage under "tnc-theme" as "light" | "dark".
 * - An explicit choice is set as data-theme on <html>; without one the attribute is
 *   absent and CSS follows the OS via @media (prefers-color-scheme: dark).
 * - Any <button data-theme-toggle> flips and persists the choice.
 * The anti-flash snippet in each page's <head> applies a stored choice before paint. */
(function () {
  var KEY = 'tnc-theme';
  var COLORS = { light: '#F6F7FB', dark: '#10141F' };
  var root = document.documentElement;
  var mql = window.matchMedia ? window.matchMedia('(prefers-color-scheme: dark)') : null;
  function stored() { try { var v = localStorage.getItem(KEY); return v === 'light' || v === 'dark' ? v : null; } catch (e) { return null; } }
  function effective() { return stored() || (mql && mql.matches ? 'dark' : 'light'); }
  function apply(c) { if (c === 'light' || c === 'dark') root.setAttribute('data-theme', c); else root.removeAttribute('data-theme'); }
  function sync() {
    var active = effective(), next = active === 'dark' ? 'light' : 'dark', label = 'Switch to ' + next + ' theme';
    document.querySelectorAll('[data-theme-toggle]').forEach(function (b) {
      b.dataset.active = active; b.setAttribute('aria-pressed', String(active === 'dark'));
      b.setAttribute('aria-label', label); b.setAttribute('title', label);
    });
    var meta = document.querySelector('meta[name="theme-color"]:not([media])');
    if (!meta) { meta = document.createElement('meta'); meta.setAttribute('name', 'theme-color'); document.head.appendChild(meta); }
    meta.setAttribute('content', COLORS[active]);
  }
  apply(stored()); sync();
  document.querySelectorAll('[data-theme-toggle]').forEach(function (b) {
    b.addEventListener('click', function () {
      var next = effective() === 'dark' ? 'light' : 'dark';
      try { localStorage.setItem(KEY, next); } catch (e) {}
      apply(next); sync();
    });
  });
  if (mql) { var on = function () { if (!stored()) sync(); }; mql.addEventListener ? mql.addEventListener('change', on) : mql.addListener(on); }
})();
