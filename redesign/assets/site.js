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

// Services page: sticky jump nav highlights the section in view and shows
// scroll progress; option cards and steps reveal in a gentle stagger.
(function () {
  var flow = document.querySelector('.svc-flow');
  var nav = document.querySelector('.svc-nav');
  if (!flow || !nav) return;
  var chips = nav.querySelector('.svc-nav__chips');
  var links = Array.prototype.slice.call(nav.querySelectorAll('a.chip'));
  var sections = links.map(function (a) { return document.querySelector(a.getAttribute('href')); }).filter(Boolean);

  function setActive(id) {
    links.forEach(function (a) {
      var on = a.getAttribute('href') === '#' + id;
      if (on) {
        a.setAttribute('aria-current', 'true');
        var left = a.offsetLeft - (chips.clientWidth - a.offsetWidth) / 2;
        chips.scrollTo({ left: Math.max(0, left), behavior: 'smooth' });
      } else {
        a.removeAttribute('aria-current');
      }
    });
  }

  var ticking = false;
  function update() {
    ticking = false;
    var r = flow.getBoundingClientRect();
    var span = r.height - window.innerHeight * 0.5;
    var p = Math.min(1, Math.max(0, (window.innerHeight * 0.5 - r.top) / span));
    nav.style.setProperty('--p', p.toFixed(4));
    var mark = window.innerHeight * 0.35;
    var current = null;
    sections.forEach(function (s) { if (s.getBoundingClientRect().top <= mark) current = s; });
    var id = current ? current.id : '';
    if (id !== nav.dataset.active) { nav.dataset.active = id; setActive(id); }
  }
  window.addEventListener('scroll', function () { if (!ticking) { ticking = true; requestAnimationFrame(update); } }, { passive: true });
  window.addEventListener('resize', update);
  update();

  if (!('IntersectionObserver' in window)) return;
  if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;
  var targets = flow.querySelectorAll('.svc-section__intro, .opt, .step');
  var io = new IntersectionObserver(function (entries) {
    entries.forEach(function (entry) {
      if (!entry.isIntersecting) return;
      var el = entry.target;
      el.classList.add('is-visible');
      io.unobserve(el);
      setTimeout(function () { el.style.transitionDelay = ''; }, 1200);
    });
  }, { threshold: 0.12, rootMargin: '0px 0px -40px 0px' });
  targets.forEach(function (el) {
    var i = Array.prototype.indexOf.call(el.parentNode.children, el);
    if (el.classList.contains('opt') || el.classList.contains('step')) el.style.transitionDelay = Math.min(i, 5) * 80 + 'ms';
    el.classList.add('reveal');
    io.observe(el);
  });
})();
