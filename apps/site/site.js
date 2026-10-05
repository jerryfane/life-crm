// Scroll-spy for the contents list. The page works without it; entries open with <details>.
(function () {
  var links = [].slice.call(document.querySelectorAll('.toc a')), ol = document.querySelector('.toc ol'),
      side = document.querySelector('.side'), root = document.documentElement;
  if (!links.length) return;
  var targets = links.map(function (a) { return document.getElementById(decodeURIComponent(a.hash.slice(1))); });

  function spy() {
    var line = (parseFloat(getComputedStyle(root).getPropertyValue('--nav')) || 0) + 48, cur = links[0];
    targets.forEach(function (s, i) { if (s && s.getBoundingClientRect().top <= line) cur = links[i]; });
    if (window.innerHeight + window.scrollY >= root.scrollHeight - 2) cur = links[links.length - 1];
    links.forEach(function (a) { if (a === cur) a.setAttribute('aria-current', 'location'); else a.removeAttribute('aria-current'); });
    // Keep the current section visible: in the phone's sideways row, or in a sidebar taller than the window.
    if (ol.scrollWidth > ol.clientWidth) {
      var l = cur.offsetLeft - ol.offsetLeft - 24;
      if (l < ol.scrollLeft || cur.offsetLeft + cur.offsetWidth - ol.offsetLeft > ol.scrollLeft + ol.clientWidth) ol.scrollTo({ left: l, behavior: 'smooth' });
    } else if (side.scrollHeight > side.clientHeight) {
      if (cur.offsetTop < side.scrollTop || cur.offsetTop + cur.offsetHeight > side.scrollTop + side.clientHeight)
        side.scrollTo({ top: cur.offsetTop - side.clientHeight / 2, behavior: 'smooth' });
    }
  }
  var t = 0;
  window.addEventListener('scroll', function () { if (!t) t = requestAnimationFrame(function () { t = 0; spy(); }); }, { passive: true });
  window.addEventListener('resize', spy);
  spy();

  // Print everything: open the closed entries for the printout, then close them again.
  var opened = [];
  window.addEventListener('beforeprint', function () {
    opened = [].filter.call(document.querySelectorAll('details:not([open])'), function (d) { d.open = true; return true; });
  });
  window.addEventListener('afterprint', function () { opened.forEach(function (d) { d.open = false; }); opened = []; });
})();
