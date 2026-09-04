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
      if (location.protocol === 'file:') { ev.preventDefault(); var box = f.closest('.cform') || f.closest('.form'); box.classList.add('sent'); window.scrollTo({ top: box.getBoundingClientRect().top + window.scrollY - 120, behavior: 'smooth' }); }
    });
  });

  // consult: floating labels for selects
  document.querySelectorAll('.cform select').forEach(function (sel) {
    var sync = function () { sel.classList.toggle('has', !!sel.value); }; sel.addEventListener('change', sync); sync();
  });

  // product: gallery thumbs, quantity, tab scrollspy
  var gmain = document.querySelector('.gmain');
  if (gmain) {
    var slides = [].filter.call(gmain.children, function (c) { return c.matches('.spin, img'); }), thumbs = document.querySelectorAll('.thumbs button'), gi = 0;
    var gnum = gmain.querySelector('.gnum'), gcap = gmain.querySelector('.gcap');
    var go = function (i) {
      gi = (i + slides.length) % slides.length;
      slides.forEach(function (s, k) { s.classList.toggle('on', k === gi); }); thumbs.forEach(function (x, k) { x.classList.toggle('on', k === gi); });
      if (gnum) gnum.textContent = (gi + 1) + ' / ' + slides.length; if (gcap) gcap.textContent = slides[gi].dataset.cap || '360° 회전';
      if (thumbs[gi]) thumbs[gi].scrollIntoView({ block: 'nearest', inline: 'center', behavior: 'smooth' });
    };
    thumbs.forEach(function (t, i) { t.addEventListener('click', function () { go(i); }); });
    gmain.querySelectorAll('[data-g]').forEach(function (b) { b.addEventListener('click', function () { go(gi + +b.dataset.g); }); });
    document.addEventListener('keydown', function (e) { if (e.key === 'ArrowRight') go(gi + 1); if (e.key === 'ArrowLeft') go(gi - 1); });
    var tx = 0; gmain.addEventListener('touchstart', function (e) { tx = e.touches[0].clientX; }, { passive: true });
    gmain.addEventListener('touchend', function (e) { if (gi === 0) return; var dx = e.changedTouches[0].clientX - tx; if (Math.abs(dx) > 40) go(gi + (dx < 0 ? 1 : -1)); }, { passive: true });
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

  // home: horizontal scroller (arrows / wheel / drag)
  var scr = document.querySelector('.scroller');
  if (scr) {
    var stepW = function () { var c = scr.firstElementChild; return c ? c.getBoundingClientRect().width + 24 : 400; };
    document.querySelectorAll('[data-scr]').forEach(function (b) { b.addEventListener('click', function () { scr.scrollBy({ left: stepW() * +b.dataset.scr, behavior: 'smooth' }); }); });
    scr.addEventListener('wheel', function (e) {
      var canL = scr.scrollLeft > 0, canR = scr.scrollLeft < scr.scrollWidth - scr.clientWidth - 1;
      if ((e.deltaY > 0 && canR) || (e.deltaY < 0 && canL)) { e.preventDefault(); scr.scrollLeft += e.deltaY; }
    }, { passive: false });
    var sx = 0, sl = 0, sd = false;
    scr.addEventListener('mousedown', function (e) { sd = true; sx = e.clientX; sl = scr.scrollLeft; scr.classList.add('drag'); e.preventDefault(); });
    window.addEventListener('mousemove', function (e) { if (sd) scr.scrollLeft = sl - (e.clientX - sx); });
    window.addEventListener('mouseup', function () { if (sd) { sd = false; scr.classList.remove('drag'); } });
  }

  // home: photo carousel
  var car = document.querySelector('.car');
  if (car) {
    var imgs = car.querySelectorAll('img'), cnt = car.querySelector('.cnt'), idx = 0;
    var show = function (n) { idx = (n + imgs.length) % imgs.length; imgs.forEach(function (im, i) { im.classList.toggle('on', i === idx); }); if (cnt) cnt.textContent = (idx + 1) + ' / ' + imgs.length; };
    document.querySelectorAll('[data-car]').forEach(function (b) { b.addEventListener('click', function () { show(idx + parseInt(b.dataset.car, 10)); }); });
    setInterval(function () { show(idx + 1); }, 5000);
  }

  // support page: dealer list + map (data from assets/dealers.js). Kakao map when KAKAO_APP_KEY is set, else OpenStreetMap.
  var list = document.querySelector('#dealerList');
  if (list && window.DEALERS) {
    var chips = document.querySelectorAll('.chip[data-region]'), q = document.querySelector('#dealerq'), empty = document.querySelector('#dealerEmpty');
    var mapEl = document.querySelector('#map'), D = window.DEALERS, api = null;
    var pinSvg = function (hq) {
      var c = hq ? '#E5322D' : '#1470A8';
      return '<svg viewBox="0 0 34 44" width="34" height="44" xmlns="http://www.w3.org/2000/svg"><path d="M17 43C17 43 3 27.5 3 16.5A14 14 0 0 1 31 16.5C31 27.5 17 43 17 43Z" fill="' + c + '" stroke="#fff" stroke-width="2"/><path d="M19.5 8.5 12 18.5h5l-1.2 8 7.7-10.5h-5z" fill="#fff"/></svg>';
    };
    var popupHtml = function (d) { return '<b>' + d.name + '</b>' + d.addr + '<br><a href="tel:' + d.tel + '">' + d.tel + '</a>'; };
    // --- Leaflet backend
    var leaflet = function () {
      if (typeof L === 'undefined' || !mapEl) return null;
      var map = L.map('map', { scrollWheelZoom: false }).setView([36.5, 127.8], 7), ms = {};
      L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', { maxZoom: 19, attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors' }).addTo(map);
      D.forEach(function (d, i) {
        if (typeof d.lat !== 'number') return;
        var m = L.marker([d.lat, d.lng], { icon: L.divIcon({ className: 'evpin', html: pinSvg(d.type === 'hq'), iconSize: [34, 44], iconAnchor: [17, 43], popupAnchor: [0, -40] }) }).addTo(map);
        m.bindPopup(popupHtml(d)); m.on('click', function () { select(i, false); }); ms[i] = m;
      });
      return {
        show: function (vis) {
          Object.keys(ms).forEach(function (k) { var on = vis.indexOf(+k) > -1; if (on && !map.hasLayer(ms[k])) ms[k].addTo(map); if (!on && map.hasLayer(ms[k])) map.removeLayer(ms[k]); });
          var shown = vis.map(function (i) { return ms[i]; }).filter(Boolean);
          if (shown.length > 1) map.fitBounds(L.featureGroup(shown).getBounds().pad(.3)); else if (shown.length === 1) map.setView(shown[0].getLatLng(), 11); else map.setView([36.5, 127.8], 7);
        },
        focus: function (i, fly) { var m = ms[i]; if (!m) return; if (fly) map.flyTo(m.getLatLng(), 13, { duration: .8 }); m.openPopup(); Object.keys(ms).forEach(function (k) { var el = ms[k].getElement(); if (el) el.classList.toggle('on', +k === i); }); }
      };
    };
    // --- Kakao backend
    var kakaoMap = function (done) {
      var sc = document.createElement('script');
      sc.src = 'https://dapi.kakao.com/v2/maps/sdk.js?appkey=' + window.KAKAO_APP_KEY + '&autoload=false';
      sc.onerror = function () { done(leaflet()); };
      sc.onload = function () {
        kakao.maps.load(function () {
          var map = new kakao.maps.Map(mapEl, { center: new kakao.maps.LatLng(36.5, 127.8), level: 12 }), ov = {}, info = null;
          map.addControl(new kakao.maps.ZoomControl(), kakao.maps.ControlPosition.TOPLEFT);
          D.forEach(function (d, i) {
            if (typeof d.lat !== 'number') return;
            var el = document.createElement('div'); el.className = 'evpin kpin'; el.innerHTML = pinSvg(d.type === 'hq');
            el.addEventListener('click', function () { select(i, false); });
            ov[i] = { o: new kakao.maps.CustomOverlay({ position: new kakao.maps.LatLng(d.lat, d.lng), content: el, yAnchor: 1 }), el: el, pos: new kakao.maps.LatLng(d.lat, d.lng) };
            ov[i].o.setMap(map);
          });
          done({
            show: function (vis) {
              Object.keys(ov).forEach(function (k) { ov[k].o.setMap(vis.indexOf(+k) > -1 ? map : null); });
              var pts = vis.map(function (i) { return ov[i] && ov[i].pos; }).filter(Boolean);
              if (pts.length > 1) { var b = new kakao.maps.LatLngBounds(); pts.forEach(function (p) { b.extend(p); }); map.setBounds(b, 60); }
              else if (pts.length === 1) { map.setCenter(pts[0]); map.setLevel(6); } else { map.setCenter(new kakao.maps.LatLng(36.5, 127.8)); map.setLevel(12); }
            },
            focus: function (i, fly) {
              var o = ov[i]; if (!o) return;
              if (fly) { map.setLevel(4); map.panTo(o.pos); }
              if (info) info.setMap(null);
              var box = document.createElement('div'); box.className = 'kinfo'; box.innerHTML = popupHtml(D[i]);
              info = new kakao.maps.CustomOverlay({ position: o.pos, content: box, yAnchor: 1.55 }); info.setMap(map);
              Object.keys(ov).forEach(function (k) { ov[k].el.classList.toggle('on', +k === i); });
            }
          });
        });
      };
      document.head.appendChild(sc);
    };
    var cards = [];
    D.forEach(function (d, i) {
      var el = document.createElement('button'); el.type = 'button'; el.className = 'dcard'; el.dataset.region = d.region; el.dataset.idx = i;
      el.innerHTML = '<div class="tag">#' + d.region + (d.type === 'hq' ? ' 본사' : ' 협력점') + '</div><h3>' + d.name + (d.type === 'hq' ? '<span class="hqmark">HQ</span>' : '') + '</h3><a class="tel" href="tel:' + d.tel + '">' + d.tel + '</a><p>' + d.addr + '</p>';
      el.addEventListener('click', function (e) { if (e.target.tagName !== 'A') select(i, true); });
      list.appendChild(el); cards.push(el);
    });
    function select(i, fly) { cards.forEach(function (c) { c.classList.toggle('on', +c.dataset.idx === i); }); if (api) api.focus(i, fly); }
    function apply() {
      var on = document.querySelector('.chip.on'); var region = on ? on.dataset.region : '전체';
      var kw = q ? q.value.trim() : ''; var vis = [];
      cards.forEach(function (c, i) { var d = D[i]; var ok = (region === '전체' || d.region === region) && (!kw || (d.name + d.addr).indexOf(kw) > -1); c.hidden = !ok; if (ok) vis.push(i); });
      if (empty) empty.hidden = vis.length > 0;
      if (api) api.show(vis);
    }
    chips.forEach(function (c) { c.addEventListener('click', function () { chips.forEach(function (x) { x.classList.remove('on'); }); c.classList.add('on'); apply(); }); });
    if (q) q.addEventListener('input', apply);
    if (window.KAKAO_APP_KEY && mapEl) kakaoMap(function (a) { api = a; apply(); }); else { api = leaflet(); apply(); }
  }
})();
