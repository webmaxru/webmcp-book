/* Web edition behaviour: mobile menu, copy buttons, current-section highlight, search.
   Search reads search-index.json (written by tools/build_site.py) on first use. */
(function () {
  var menu = document.querySelector('.menu');
  if (menu) menu.addEventListener('click', function () {
    var open = document.body.classList.toggle('nav-open');
    menu.setAttribute('aria-expanded', String(open));
  });
  document.addEventListener('keydown', function (e) { if (e.key === 'Escape') document.body.classList.remove('nav-open'); });
  document.addEventListener('click', function (e) {
    if (document.body.classList.contains('nav-open') && !e.target.closest('.sidebar') && !e.target.closest('.menu')) document.body.classList.remove('nav-open');
  });
  document.querySelectorAll('.sidebar a').forEach(function (a) { a.addEventListener('click', function () { document.body.classList.remove('nav-open'); }); });

  // copy buttons
  document.querySelectorAll('pre.code').forEach(function (pre) {
    var b = document.createElement('button');
    b.className = 'copy'; b.type = 'button'; b.textContent = 'Copy'; b.setAttribute('aria-label', 'Copy code');
    b.addEventListener('click', function () {
      var lines = Array.prototype.map.call(pre.querySelectorAll('.ln'), function (l) { return l.textContent; });
      var text = lines.length ? lines.join('\n') : pre.innerText;
      var done = function (t) { b.textContent = t; setTimeout(function () { b.textContent = 'Copy'; }, 1500); };
      if (navigator.clipboard) navigator.clipboard.writeText(text).then(function () { done('Copied'); }, function () { done('Press Ctrl+C'); });
      else done('Press Ctrl+C');
    });
    pre.appendChild(b);
  });

  // highlight the current section in the sidebar
  var links = Array.prototype.slice.call(document.querySelectorAll('.chapter-nav ol.sections a'));
  if (links.length && 'IntersectionObserver' in window) {
    var map = {}; links.forEach(function (a) { map[decodeURIComponent(a.hash.slice(1))] = a; });
    var io = new IntersectionObserver(function (es) {
      es.forEach(function (e) {
        if (e.isIntersecting && map[e.target.id]) { links.forEach(function (l) { l.classList.remove('active'); }); map[e.target.id].classList.add('active'); }
      });
    }, { rootMargin: '-10% 0px -80% 0px' });
    document.querySelectorAll('.prose h2[id]').forEach(function (h) { io.observe(h); });
  }

  // search
  var q = document.getElementById('q'), box = document.getElementById('results');
  if (!q || !box) return;
  var base = q.getAttribute('data-base') || '';
  var index = null, sel = -1;
  function load() {
    return index ? Promise.resolve(index) : fetch(base + 'search-index.json').then(function (r) { return r.json(); }).then(function (j) {
      index = j.map(function (e) { e.lx = e.x.toLowerCase(); e.lt = e.t.toLowerCase(); return e; }); return index;
    });
  }
  function escH(s) { return s.replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); }
  function mark(s, terms) { var h = escH(s); terms.forEach(function (t) { h = h.replace(new RegExp('(' + t.replace(/[.*+?^${}()|[\]\\]/g, '\\$&') + ')', 'ig'), '<mark>$1</mark>'); }); return h; }
  function run() {
    var v = q.value.trim().toLowerCase();
    if (v.length < 2) { box.classList.remove('open'); box.innerHTML = ''; return; }
    load().then(function (ix) {
      var terms = v.split(/\s+/).filter(Boolean), hits = [];
      ix.forEach(function (e) {
        var score = 0, ok = true;
        for (var i = 0; i < terms.length; i++) { var t = terms[i], inT = e.lt.indexOf(t) >= 0, inX = e.lx.indexOf(t) >= 0; if (!inT && !inX) { ok = false; break; } score += (inT ? 10 : 0) + (inX ? 1 : 0); }
        if (ok) hits.push([score, e]);
      });
      hits.sort(function (a, b) { return b[0] - a[0]; }); sel = -1;
      box.innerHTML = hits.slice(0, 12).map(function (h) {
        var e = h[1], i = e.lx.indexOf(terms[0]);
        var snip = i < 0 ? e.x.slice(0, 140) : (i > 60 ? '…' : '') + e.x.slice(Math.max(0, i - 60), i + 100) + '…';
        return '<a href="' + base + e.u + '"><div class="r-c">' + escH(e.c) + '</div><div class="r-t">' + mark(e.t, terms) + '</div><div class="r-x">' + mark(snip, terms) + '</div></a>';
      }).join('') || '<div class="none">No matches</div>';
      box.classList.add('open');
    });
  }
  q.addEventListener('input', run);
  q.addEventListener('focus', function () { load(); if (q.value.trim().length > 1) run(); });
  q.addEventListener('keydown', function (e) {
    var items = Array.prototype.slice.call(box.querySelectorAll('a'));
    if ((e.key === 'ArrowDown' || e.key === 'ArrowUp') && items.length) {
      e.preventDefault(); sel = (sel + (e.key === 'ArrowDown' ? 1 : -1) + items.length) % items.length;
      items.forEach(function (a, i) { a.classList.toggle('sel', i === sel); });
    } else if (e.key === 'Enter' && items.length) { location.href = items[Math.max(sel, 0)].href; }
    else if (e.key === 'Escape') { box.classList.remove('open'); q.blur(); }
  });
  document.addEventListener('click', function (e) { if (!e.target.closest('.search')) box.classList.remove('open'); });
  document.addEventListener('keydown', function (e) { if (e.key === '/' && document.activeElement !== q && !/input|textarea/i.test(document.activeElement.tagName)) { e.preventDefault(); q.focus(); } });
})();
