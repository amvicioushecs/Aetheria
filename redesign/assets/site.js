// Mobile navigation toggle
(function () {
  var btn = document.querySelector('.nav-toggle');
  var nav = document.querySelector('.nav');
  if (!btn || !nav) return;
  btn.addEventListener('click', function () {
    var open = nav.classList.toggle('is-open');
    btn.setAttribute('aria-expanded', open ? 'true' : 'false');
  });
})();

// Home page scroll reveal: only on index.html, only with IntersectionObserver,
// and never for reduced-motion users. .reveal is added by JS, so without JS
// (or without observer support) the content simply stays visible.
(function () {
  var path = window.location.pathname;
  var isHome = /(^|\/)index\.html$/.test(path) || path === '/' || path === '';
  if (!isHome) return;
  if (!('IntersectionObserver' in window)) return;
  if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;
  var targets = document.querySelectorAll('main .section, .svc-card, .obit-card, .loc-card');
  if (!targets.length) return;
  var io = new IntersectionObserver(function (entries) {
    entries.forEach(function (entry) {
      if (entry.isIntersecting) { entry.target.classList.add('is-visible'); io.unobserve(entry.target); }
    });
  }, { threshold: 0.12, rootMargin: '0px 0px -40px 0px' });
  targets.forEach(function (el) { el.classList.add('reveal'); io.observe(el); });
})();

// Home service cards: gentle 3D tilt following the mouse, capped at about
// 3.5 degrees so it stays calm and warm, not gimmicky. Mouse/trackpad only,
// never for reduced-motion users, and the card returns to its CSS hover lift
// on mouseleave (inline transform is cleared).
(function () {
  var path = window.location.pathname;
  var isHome = /(^|\/)index\.html$/.test(path) || path === '/' || path === '';
  if (!isHome) return;
  if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;
  if (!window.matchMedia('(pointer: fine)').matches) return;
  var cards = document.querySelectorAll('.svc-card');
  cards.forEach(function (card) {
    card.addEventListener('mousemove', function (e) {
      var r = card.getBoundingClientRect();
      var x = (e.clientX - r.left) / r.width - 0.5;
      var y = (e.clientY - r.top) / r.height - 0.5;
      var ry = (x * 7).toFixed(2);
      var rx = (-y * 7).toFixed(2);
      card.style.transform = 'rotateX(' + rx + 'deg) rotateY(' + ry + 'deg) translateY(-6px)'; // perspective comes from .svc-card in site.css
    });
    card.addEventListener('mouseleave', function () { card.style.transform = ''; });
  });
})();
