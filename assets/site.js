/* SP Mobility — small progressive enhancements. No frameworks. */
(function () {
  // scroll reveal
  var els = document.querySelectorAll('.rv');
  if ('IntersectionObserver' in window) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) { if (e.isIntersecting) { e.target.classList.add('is-in'); io.unobserve(e.target); } });
    }, { rootMargin: '0px 0px -12% 0px' });
    els.forEach(function (el) { io.observe(el); });
  } else { els.forEach(function (el) { el.classList.add('is-in'); }); }

  // mobile nav
  var btn = document.querySelector('.hdr .menu');
  if (btn) btn.addEventListener('click', function () { document.body.classList.toggle('nav-open'); });

  // current nav highlight
  var here = location.pathname.split('/').pop() || 'index.html';
  document.querySelectorAll('.hdr nav a').forEach(function (a) {
    if (a.getAttribute('href') === here) a.classList.add('on');
  });

  // consult page: preselect type from ?type=rent
  var t = new URLSearchParams(location.search).get('type');
  if (t) { var r = document.querySelector('input[name="상담유형"][value="' + (t === 'rent' ? '렌트/리스' : '신차 구매') + '"]'); if (r) r.checked = true; }

  // forms: netlify handles POST in production; on file:// preview just show the done state
  document.querySelectorAll('form[data-netlify]').forEach(function (f) {
    f.addEventListener('submit', function (ev) {
      if (location.protocol === 'file:') { ev.preventDefault(); f.closest('.form').classList.add('sent'); window.scrollTo({ top: f.closest('.form').offsetTop - 120, behavior: 'smooth' }); }
    });
  });

  // home: photo carousel
  var car = document.querySelector('.car');
  if (car) {
    var imgs = car.querySelectorAll('img'), cnt = car.querySelector('.cnt'), idx = 0;
    var show = function (n) { idx = (n + imgs.length) % imgs.length; imgs.forEach(function (im, i) { im.classList.toggle('on', i === idx); }); if (cnt) cnt.textContent = (idx + 1) + ' / ' + imgs.length; };
    document.querySelectorAll('[data-car]').forEach(function (b) { b.addEventListener('click', function () { show(idx + parseInt(b.dataset.car, 10)); }); });
    setInterval(function () { show(idx + 1); }, 5000);
  }

  // support page: region filter + search
  var chips = document.querySelectorAll('.chip[data-region]');
  var cards = document.querySelectorAll('.dcard[data-region]');
  var q = document.querySelector('#dealerq');
  var empty = document.querySelector('.dealers .empty');
  function apply() {
    var on = document.querySelector('.chip.on'); var region = on ? on.dataset.region : '전체';
    var kw = q ? q.value.trim() : ''; var n = 0;
    cards.forEach(function (c) {
      var ok = (region === '전체' || c.dataset.region === region) && (!kw || c.textContent.indexOf(kw) > -1);
      c.style.display = ok ? '' : 'none'; if (ok) n++;
    });
    if (empty) empty.style.display = n ? 'none' : '';
  }
  chips.forEach(function (c) { c.addEventListener('click', function () { chips.forEach(function (x) { x.classList.remove('on'); }); c.classList.add('on'); apply(); }); });
  if (q) q.addEventListener('input', apply);
  if (chips.length) apply();
})();
