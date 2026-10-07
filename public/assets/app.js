/* Bestower storefront — cart, shop filters and WhatsApp-confirmed checkout. No secrets here. */
(function () {
  var CFG = window.BESTOWER_CONFIG || {};
  var ROOT = window.BESTOWER_ROOT || '';
  var PRODUCTS = window.PRODUCTS || [];
  var KEY = 'bestower-cart';
  var byId = function (id) { return PRODUCTS.filter(function (p) { return p.id === id; })[0]; };
  var inr = function (n) { return '₹' + Number(n).toLocaleString('en-IN', { minimumFractionDigits: n % 1 ? 2 : 0, maximumFractionDigits: 2 }); };
  var esc = function (s) { return String(s == null ? '' : s).replace(/[&<>"']/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]; }); };

  /* cart keys are "id" or "id|pack" for products with pack sizes */
  function parse(key) {
    var parts = key.split('|'), p = byId(parts[0]); if (!p) return null;
    var pack = parts[1] || null, price = p.price;
    if (p.variants && p.variants.length) {
      var v = p.variants.filter(function (x) { return x.pack === pack; })[0]; if (!v) return null;
      price = v.price;
    } else pack = p.pack;
    return { p: p, pack: pack, price: price, key: key };
  }
  function keyFor(p, pack) { return p.variants && p.variants.length ? p.id + '|' + (pack || p.variants[0].pack) : p.id; }

  /* ---------- cart storage (only purchasable products are kept) ---------- */
  function load() {
    var c; try { c = JSON.parse(localStorage.getItem(KEY)) || {}; } catch (e) { c = {}; }
    Object.keys(c).forEach(function (k) { var i = parse(k); if (!i || !i.p.stock || i.price == null || !(c[k] > 0)) delete c[k]; });
    return c;
  }
  function save(c) { localStorage.setItem(KEY, JSON.stringify(c)); badge(); }
  function count() { var c = load(), n = 0; for (var k in c) n += c[k]; return n; }
  function add(id, q, pack) { var p = byId(id); if (!p || !p.stock) return false; var k = keyFor(p, pack); if (!parse(k)) return false; var c = load(); c[k] = (c[k] || 0) + q; save(c); return true; }
  function badge() {
    var a = document.getElementById('bag-link'); if (!a) return;
    var s = a.querySelector('.bag-count'), n = count();
    if (!n) { if (s) s.remove(); a.setAttribute('aria-label', 'Shopping cart'); return; }
    if (!s) { s = document.createElement('span'); s.className = 'bag-count'; a.appendChild(s); }
    s.textContent = n; a.setAttribute('aria-label', 'Shopping cart, ' + n + ' items');
  }
  badge();

  /* ---------- header menu ---------- */
  var mb = document.getElementById('menu-btn'), mn = document.getElementById('mobile-nav');
  if (mb) mb.addEventListener('click', function () {
    var o = mn.classList.toggle('open'); mb.setAttribute('aria-expanded', o);
  });

  /* ---------- add to cart buttons (cards + product page) ---------- */
  function flash(btn, msg) { var t = btn.textContent; btn.textContent = msg; setTimeout(function () { btn.textContent = t; }, 1400); }
  document.querySelectorAll('.add-btn').forEach(function (b) {
    b.addEventListener('click', function () { if (add(b.dataset.id, 1)) flash(b, 'Added ✓'); });
  });
  var qty = 1, qEl = document.getElementById('qty');
  document.querySelectorAll('[data-qty]').forEach(function (b) {
    b.addEventListener('click', function () { qty = Math.max(1, Math.min(20, qty + Number(b.dataset.qty))); qEl.textContent = qty; });
  });
  var pack = null, packsEl = document.getElementById('packs');
  if (packsEl) {
    pack = packsEl.querySelector('.on').dataset.pack;
    packsEl.querySelectorAll('.pack').forEach(function (b) {
      b.addEventListener('click', function () {
        packsEl.querySelectorAll('.pack').forEach(function (o) { o.classList.remove('on'); }); b.classList.add('on');
        pack = b.dataset.pack; document.getElementById('pdp-price').textContent = inr(b.dataset.price);
      });
    });
  }
  var a2c = document.getElementById('add-to-cart');
  if (a2c) a2c.addEventListener('click', function () { if (add(a2c.dataset.id, qty, pack)) flash(a2c, 'Added ✓'); });
  var bn = document.getElementById('buy-now');
  if (bn) bn.addEventListener('click', function () { if (add(bn.dataset.id, qty, pack)) location.href = ROOT + 'cart.html'; });
  var big = document.querySelector('#pdp-photo img');
  document.querySelectorAll('.thumbs img').forEach(function (t) {
    t.addEventListener('click', function () {
      big.src = t.src; big.style.objectPosition = 'center'; big.style.objectFit = (t.naturalWidth / t.naturalHeight > 1.15) ? 'contain' : 'cover';
      document.querySelectorAll('.thumbs img').forEach(function (i) { i.classList.remove('on'); }); t.classList.add('on');
    });
  });

  /* ---------- shop filters ---------- */
  var grid = document.getElementById('product-grid');
  if (grid) {
    var tabs = document.querySelectorAll('.filters button'), empty = document.getElementById('empty');
    var cards = Array.prototype.slice.call(grid.children);
    function show(cat) {
      var n = 0;
      cards.forEach(function (c) { var ok = cat === 'all' || c.dataset.cat === cat; c.hidden = !ok; if (ok) n++; });
      empty.hidden = n > 0;
      tabs.forEach(function (t) { t.classList.toggle('on', t.dataset.cat === cat); });
    }
    tabs.forEach(function (t) { t.addEventListener('click', function () { show(t.dataset.cat); }); });
    var want = new URLSearchParams(location.search).get('category'); if (want) show(want);
  }

  /* ---------- cart + checkout ---------- */
  var root = document.getElementById('cart-root');
  if (!root) return;

  function shippingFor(sub) {
    var s = CFG.shipping || {};
    if (s.flatRate == null) return null;
    if (s.freeAbove != null && sub >= s.freeAbove) return 0;
    return s.flatRate;
  }
  function totals() {
    var c = load(), items = [], sub = 0;
    Object.keys(c).forEach(function (k) { var i = parse(k); items.push({ p: i.p, pack: i.pack, price: i.price, key: k, q: c[k] }); sub += i.price * c[k]; });
    var ship = shippingFor(sub);
    return { items: items, sub: sub, ship: ship, total: sub + (ship || 0) };
  }
  function shipLabel(t) { return t.ship == null ? 'Confirmed at dispatch' : (t.ship === 0 ? 'Free' : inr(t.ship)); }

  function render() {
    var t = totals();
    if (!t.items.length) {
      root.innerHTML = '<div class="empty" style="margin-bottom:90px"><h2>Your cart is empty</h2><p style="margin:14px 0 24px">Browse the Bestower collection and add your favourites.</p><a class="btn" href="' + ROOT + 'shop.html">Shop Bestower</a></div>';
      return;
    }
    var lines = t.items.map(function (i) {
      var img = i.p.image ? '<img src="' + ROOT + i.p.image + '" alt="' + esc(i.p.name) + '" style="object-position:' + esc(i.p.position) + ';object-fit:' + esc(i.p.fit || 'cover') + '"/>' : '<div class="ph">' + esc(i.p.name) + '</div>';
      return '<div class="line">' + img + '<div><h3>' + esc(i.p.name) + '</h3><p>' + esc(i.pack || '') + (i.pack ? ' · ' : '') + inr(i.price) + ' each</p>' +
        '<div class="qty"><button data-d="-1" data-id="' + esc(i.key) + '" aria-label="Decrease quantity of ' + esc(i.p.name) + '">−</button><span>' + i.q + '</span><button data-d="1" data-id="' + esc(i.key) + '" aria-label="Increase quantity of ' + esc(i.p.name) + '">+</button></div></div>' +
        '<div class="line-total">' + inr(i.price * i.q) + '<button data-rm="' + esc(i.key) + '">Remove</button></div></div>';
    }).join('');
    function f(name, label, type, extra) {
      return '<div class="field" data-f="' + name + '"><label for="f-' + name + '">' + label + '</label><input id="f-' + name + '" name="' + name + '" type="' + (type || 'text') + '" ' + (extra || '') + ' required/><span class="msg"></span></div>';
    }
    root.innerHTML = '<div class="checkout"><div><h2 style="margin-bottom:8px">Items</h2>' + lines + '</div>' +
      '<form class="panel" id="checkout" novalidate><h2>Checkout</h2>' +
      f('name', 'Full name', 'text', 'autocomplete="name"') +
      '<div class="two">' + f('phone', 'Mobile number', 'tel', 'autocomplete="tel" inputmode="numeric" maxlength="14"') + f('email', 'Email', 'email', 'autocomplete="email"') + '</div>' +
      '<div class="field" data-f="address"><label for="f-address">Complete shipping address</label><textarea id="f-address" name="address" rows="3" autocomplete="street-address" required></textarea><span class="msg"></span></div>' +
      '<div class="two">' + f('city', 'City', 'text', 'autocomplete="address-level2"') +
      '<div class="field" data-f="state"><label for="f-state">State</label><select id="f-state" name="state" autocomplete="address-level1" required>' + root.dataset.states + '</select><span class="msg"></span></div></div>' +
      f('pin', 'PIN code', 'text', 'autocomplete="postal-code" inputmode="numeric" maxlength="6"') +
      '<h2 style="font-size:24px;margin:26px 0 8px">Order summary</h2>' +
      '<div class="sum-row"><span>Subtotal</span><span>' + inr(t.sub) + '</span></div>' +
      '<div class="sum-row"><span>Shipping</span><span>' + shipLabel(t) + '</span></div>' +
      '<div class="sum-row total"><span>Total</span><span>' + inr(t.total) + '</span></div>' +
      '<div class="pay-box"><strong>Payment method</strong>Our team will confirm your order and share a secure payment link (UPI, cards or net banking) on WhatsApp.</div>' +
      '<p class="msg" id="form-err" role="alert" style="color:var(--maroon);font-weight:700"></p>' +
      '<button type="submit" class="btn btn-gold btn-block" id="place">Place Order</button>' +
      '<p class="secure">Your details are used only to process and deliver your order.</p></form></div>';

    root.querySelectorAll('[data-d]').forEach(function (b) { b.onclick = function () { var c = load(); c[b.dataset.id] = Math.max(1, Math.min(20, c[b.dataset.id] + Number(b.dataset.d))); save(c); render(); }; });
    root.querySelectorAll('[data-rm]').forEach(function (b) { b.onclick = function () { var c = load(); delete c[b.dataset.rm]; save(c); render(); }; });
    document.getElementById('checkout').addEventListener('submit', submit);
  }

  function validate(form) {
    var d = {}; ['name', 'phone', 'email', 'address', 'city', 'state', 'pin'].forEach(function (k) { d[k] = (form.elements[k].value || '').trim(); });
    var rules = {
      name: [d.name.length >= 2, 'Please enter your full name.'],
      phone: [/^(\+91[\s-]?)?[6-9][0-9]{9}$/.test(d.phone.replace(/\s/g, '')), 'Please enter a valid 10-digit mobile number.'],
      email: [/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(d.email), 'Please enter a valid email address.'],
      address: [d.address.length >= 8, 'Please enter your complete shipping address.'],
      city: [d.city.length >= 2, 'Please enter your city.'],
      state: [!!d.state, 'Please select your state.'],
      pin: [/^[1-9][0-9]{5}$/.test(d.pin), 'Please enter a valid 6-digit PIN code.']
    }, ok = true, first = null;
    Object.keys(rules).forEach(function (k) {
      var fld = form.querySelector('[data-f="' + k + '"]'), bad = !rules[k][0];
      fld.classList.toggle('err', bad); fld.querySelector('.msg').textContent = bad ? rules[k][1] : '';
      if (bad) { ok = false; if (!first) first = fld; }
    });
    if (first) first.querySelector('input,select,textarea').focus();
    return ok ? d : null;
  }

  function orderRef() { return 'BST' + Date.now().toString(36).toUpperCase().slice(-7); }

  function success(ref, t, customer) {
    localStorage.removeItem(KEY); badge();
    var lines = t.items.map(function (i) { return '• ' + i.p.name + (i.pack ? ' (' + i.pack + ')' : '') + ' × ' + i.q + ' = ' + inr(i.price * i.q); }).join('\n');
    var msg = 'Hello Bestower, I have placed order ' + ref + ':\n\n' + lines + '\n\nSubtotal: ' + inr(t.sub) + '\nTotal: ' + inr(t.total) +
      '\n\nName: ' + customer.name + '\nMobile: ' + customer.phone + '\nEmail: ' + customer.email + '\nAddress: ' + customer.address + ', ' + customer.city + ', ' + customer.state + ' - ' + customer.pin;
    var wa = 'https://wa.me/' + (CFG.whatsapp || '919962630550') + '?text=' + encodeURIComponent(msg);
    root.innerHTML = '<div class="success"><p class="eyebrow">Order received</p><h2>Thank you, ' + esc(customer.name.split(' ')[0]) + '.</h2>' +
      '<div class="ref">Order ' + esc(ref) + '</div>' +
      '<p>Please send your order to us on WhatsApp so our team can confirm it and share payment and delivery details.</p>' +
      '<div class="btn-row"><a class="btn btn-gold" href="' + wa + '" target="_blank" rel="noopener">Send order on WhatsApp</a><a class="btn btn-outline" href="' + ROOT + 'shop.html">Continue shopping</a></div></div>';
    window.scrollTo(0, 0);
    window.open(wa, '_blank');
  }

  function submit(e) {
    e.preventDefault();
    var form = e.target, customer = validate(form); if (!customer) return;
    success(orderRef(), totals(), customer);
  }
  render();
})();
