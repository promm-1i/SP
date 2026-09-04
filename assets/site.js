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
  document.querySelectorAll('.hdr nav .item > a').forEach(function (a) {
    if (a.getAttribute('href').replace('./', '') === here) a.classList.add('on');
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

  // consult: floating labels for selects
  document.querySelectorAll('.cform select').forEach(function (sel) {
    var sync = function () { sel.classList.toggle('has', !!sel.value); }; sel.addEventListener('change', sync); sync();
  });

  // product: gallery thumbs, quantity, tab scrollspy
  var gmain = document.querySelector('.gmain');
  if (gmain) {
    var slides = gmain.children, thumbs = document.querySelectorAll('.thumbs button');
    thumbs.forEach(function (t, i) { t.addEventListener('click', function () { [].forEach.call(slides, function (s, k) { s.classList.toggle('on', k === i); }); thumbs.forEach(function (x, k) { x.classList.toggle('on', k === i); }); }); });
    var qi = document.querySelector('.qty input');
    document.querySelectorAll('.qty button').forEach(function (b) { b.addEventListener('click', function () { qi.value = Math.max(1, Math.min(99, (+qi.value || 1) + (+b.dataset.d))); }); });
    var tabs = document.querySelectorAll('.ptabs a'), secs = [].map.call(tabs, function (a) { return document.querySelector(a.getAttribute('href')); });
    var spy = function () { var y = window.scrollY + 170, cur = 0; secs.forEach(function (s, i) { if (s && s.offsetTop <= y) cur = i; }); tabs.forEach(function (a, i) { a.classList.toggle('on', i === cur); }); };
    window.addEventListener('scroll', spy, { passive: true }); spy();
  }

  // home hero: subtle mouse parallax on the background photo
  var hero = document.querySelector('.hero'), hbg = document.querySelector('.hero .bg');
  if (hero && hbg && matchMedia('(pointer:fine)').matches) {
    hero.addEventListener('mousemove', function (e) {
      var r = hero.getBoundingClientRect(), x = (e.clientX - r.left) / r.width - .5, y = (e.clientY - r.top) / r.height - .5;
      hbg.style.transform = 'scale(1.02) translate(' + (-x * 14) + 'px,' + (-y * 10) + 'px)';
    });
    hero.addEventListener('mouseleave', function () { hbg.style.transform = ''; });
  }

  // product: 360° spin (drag / swipe / auto-rotate)
  var spin = document.querySelector('.spin');
  if (spin) {
    var fr = spin.querySelectorAll('img'), cur = 0, startX = 0, startIdx = 0, drag = false, idle;
    var set = function (i) { cur = ((i % fr.length) + fr.length) % fr.length; fr.forEach(function (im, k) { im.classList.toggle('on', k === cur); }); };
    var auto = setInterval(function () { if (!drag) set(cur + 1); }, 1400);
    var stopAuto = function () { clearInterval(auto); clearTimeout(idle); idle = setTimeout(function () { auto = setInterval(function () { if (!drag) set(cur + 1); }, 1400); }, 4000); };
    var down = function (x) { drag = true; startX = x; startIdx = cur; stopAuto(); };
    var move = function (x) { if (!drag) return; var d = Math.round((x - startX) / 40); set(startIdx - d); };
    spin.addEventListener('mousedown', function (e) { down(e.clientX); e.preventDefault(); });
    window.addEventListener('mousemove', function (e) { move(e.clientX); });
    window.addEventListener('mouseup', function () { drag = false; });
    spin.addEventListener('touchstart', function (e) { down(e.touches[0].clientX); }, { passive: true });
    spin.addEventListener('touchmove', function (e) { move(e.touches[0].clientX); }, { passive: true });
    spin.addEventListener('touchend', function () { drag = false; });
    spin.addEventListener('mouseenter', stopAuto);
  }

  // home: photo carousel
  var car = document.querySelector('.car');
  if (car) {
    var imgs = car.querySelectorAll('img'), cnt = car.querySelector('.cnt'), idx = 0;
    var show = function (n) { idx = (n + imgs.length) % imgs.length; imgs.forEach(function (im, i) { im.classList.toggle('on', i === idx); }); if (cnt) cnt.textContent = (idx + 1) + ' / ' + imgs.length; };
    document.querySelectorAll('[data-car]').forEach(function (b) { b.addEventListener('click', function () { show(idx + parseInt(b.dataset.car, 10)); }); });
    setInterval(function () { show(idx + 1); }, 5000);
  }

  // support page: dealer list + map (data from assets/dealers.js)
  var list = document.querySelector('#dealerList');
  if (list && window.DEALERS) {
    var chips = document.querySelectorAll('.chip[data-region]'), q = document.querySelector('#dealerq'), empty = document.querySelector('#dealerEmpty');
    var map = null, markers = [], hasL = typeof L !== 'undefined' && document.querySelector('#map');
    var pinSvg = function (hq) {
      var c = hq ? '#E5322D' : '#1470A8';
      return '<svg viewBox="0 0 34 44" xmlns="http://www.w3.org/2000/svg"><path d="M17 43C17 43 3 27.5 3 16.5A14 14 0 0 1 31 16.5C31 27.5 17 43 17 43Z" fill="' + c + '" stroke="#fff" stroke-width="2"/><path d="M19.5 8.5 12 18.5h5l-1.2 8 7.7-10.5h-5z" fill="#fff"/></svg>';
    };
    if (hasL) {
      map = L.map('map', { scrollWheelZoom: false, zoomControl: true, attributionControl: true }).setView([36.5, 127.8], 7);
      L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', { maxZoom: 19, attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors' }).addTo(map);
      window.DEALERS.forEach(function (d, i) {
        if (typeof d.lat !== 'number') return;
        var m = L.marker([d.lat, d.lng], { icon: L.divIcon({ className: 'evpin', html: pinSvg(d.type === 'hq'), iconSize: [34, 44], iconAnchor: [17, 43], popupAnchor: [0, -40] }) }).addTo(map);
        m.bindPopup('<b>' + d.name + '</b>' + d.addr + '<br><a href="tel:' + d.tel + '">' + d.tel + '</a>');
        m.on('click', function () { select(i, false); });
        m._idx = i; markers.push(m);
      });
    }
    var cards = [];
    window.DEALERS.forEach(function (d, i) {
      var el = document.createElement('button'); el.type = 'button'; el.className = 'dcard'; el.dataset.region = d.region; el.dataset.idx = i;
      el.innerHTML = '<div class="tag">#' + d.region + (d.type === 'hq' ? ' 본사' : ' 협력점') + '</div><h3>' + d.name + (d.type === 'hq' ? '<span class="hqmark">HQ</span>' : '') + '</h3><a class="tel" href="tel:' + d.tel + '">' + d.tel + '</a><p>' + d.addr + '</p>';
      el.addEventListener('click', function (e) { if (e.target.tagName !== 'A') select(i, true); });
      list.appendChild(el); cards.push(el);
    });
    function select(i, fly) {
      cards.forEach(function (c) { c.classList.toggle('on', +c.dataset.idx === i); });
      markers.forEach(function (m) { var el = m.getElement(); if (el) el.classList.toggle('on', m._idx === i); });
      if (map && markers.length) { var m = markers.filter(function (x) { return x._idx === i; })[0]; if (m) { if (fly) map.flyTo(m.getLatLng(), 13, { duration: .8 }); m.openPopup(); } }
    }
    function apply() {
      var on = document.querySelector('.chip.on'); var region = on ? on.dataset.region : '전체';
      var kw = q ? q.value.trim() : ''; var n = 0, vis = [];
      cards.forEach(function (c, i) {
        var d = window.DEALERS[i];
        var ok = (region === '전체' || d.region === region) && (!kw || (d.name + d.addr).indexOf(kw) > -1);
        c.hidden = !ok; if (ok) { n++; vis.push(i); }
      });
      if (empty) empty.hidden = n > 0;
      if (map) {
        markers.forEach(function (m) { var show = vis.indexOf(m._idx) > -1; if (show && !map.hasLayer(m)) m.addTo(map); if (!show && map.hasLayer(m)) map.removeLayer(m); });
        var shown = markers.filter(function (m) { return vis.indexOf(m._idx) > -1; });
        if (shown.length > 1) map.fitBounds(L.featureGroup(shown).getBounds().pad(.3));
        else if (shown.length === 1) map.setView(shown[0].getLatLng(), 11);
        else map.setView([36.5, 127.8], 7);
      }
    }
    chips.forEach(function (c) { c.addEventListener('click', function () { chips.forEach(function (x) { x.classList.remove('on'); }); c.classList.add('on'); apply(); }); });
    if (q) q.addEventListener('input', apply);
    apply();
  }
})();
