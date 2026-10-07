#!/usr/bin/env python3
"""Bestower static site generator.
Run:  npm run build   (or python3 build.py)  ->  writes the site into ./public
Edit products in products.json (flip "stock" to true, add "price"/"pack") and rebuild.
"""
import json, html, os, shutil, glob

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, 'public')
PRODUCTS = json.load(open(os.path.join(ROOT, 'products.json'), encoding='utf-8'))
CATEGORIES = ['Saffron', 'Nuts & Seeds', 'Fruits & Dry Fruits', 'Natural Products']
PHONE_DISPLAY, PHONE_TEL, WA = '+91 9962630550', '+919962630550', '919962630550'
EMAIL = 'business@bestower.co.in'
E = html.escape

HOME_TITLE = 'Bestower | Premium Saffron, Dry Fruits & Natural Products'
HOME_DESC = 'Discover carefully selected saffron, dry fruits and natural products from remarkable origins. Bestower — from the finest origin at your table.'

NAV = [('index.html', 'Home'), ('shop.html', 'Shop'), ('about.html', 'About'), ('contact.html', 'Contact')]

BAG = '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M6 2 3 6v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2V6l-3-4Z"/><path d="M3 6h18"/><path d="M16 10a4 4 0 0 1-8 0"/></svg>'
MENU = '<svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" aria-hidden="true"><path d="M4 7h16M4 12h16M4 17h16"/></svg>'
WA_ICON = '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M21 11.5a8.4 8.4 0 0 1-12.5 7.3L3 20.500l1.500-5.200A8.500 8.500 0 1 1 21 11.500Z"/></svg>'


def prefix(depth):
    return '../' * depth


def layout(title, desc, main, depth=0, active='', extra_head=''):
    p = prefix(depth)
    nav = ''.join('<a href="%s%s"%s>%s</a>' % (p, h, ' class="active"' if h == active else '', l) for h, l in NAV)
    mnav = ''.join('<a href="%s%s">%s</a>' % (p, h, l) for h, l in NAV)
    footer = f'''<footer class="site-footer"><div class="wrap"><div class="foot-grid">
<div><img src="{p}assets/img/logo.png" alt="Bestower" width="86" height="86"/><p class="foot-tag">from the finest origin at your table</p></div>
<div><h4>Explore</h4><a href="{p}shop.html">Shop</a><a href="{p}about.html">About</a><a href="{p}contact.html">Contact</a><a href="{p}faq.html">FAQs</a></div>
<div><h4>Policies</h4><a href="{p}shipping-delivery.html">Shipping &amp; Delivery</a><a href="{p}returns-refunds.html">Returns &amp; Refunds</a><a href="{p}privacy.html">Privacy Policy</a><a href="{p}terms.html">Terms &amp; Conditions</a></div>
<div><h4>Contact</h4><p><a href="tel:{PHONE_TEL}">{PHONE_DISPLAY}</a></p><p><a href="mailto:{EMAIL}">{EMAIL}</a></p><p>Perambur, Chennai, Tamil Nadu</p><a class="text-link" href="https://wa.me/{WA}" target="_blank" rel="noopener">Chat with us on WhatsApp</a></div>
</div><div class="foot-bottom"><span>© 2026 Bestower Enterprises. All rights reserved.</span><span>Chennai, India</span></div></div></footer>
<a class="wa-float" href="https://wa.me/{WA}" target="_blank" rel="noopener" aria-label="Chat with Bestower on WhatsApp">{WA_ICON}<span>WhatsApp</span></a>'''
    return f'''<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"/><meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>{E(title)}</title><meta name="description" content="{E(desc)}"/>
<meta property="og:title" content="{E(title)}"/><meta property="og:description" content="{E(desc)}"/><meta property="og:type" content="website"/>
<link rel="icon" href="{p}assets/img/logo.png" type="image/png"/>
<link rel="preconnect" href="https://fonts.googleapis.com"/><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin/>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,600;0,700;1,600&amp;family=Manrope:wght@400;500;600;700;800&amp;display=swap"/>
<link rel="stylesheet" href="{p}assets/styles.css"/>{extra_head}</head><body>
<a class="skip" href="#main">Skip to content</a>
<div class="announce">India-wide delivery · Questions? <a href="https://wa.me/{WA}" target="_blank" rel="noopener">Chat with us on WhatsApp</a></div>
<header class="site-header"><div class="wrap header-in">
<a class="brand" href="{p}index.html" aria-label="Bestower home"><img src="{p}assets/img/logo.png" alt="Bestower" width="76" height="76"/></a>
<nav class="nav" aria-label="Main navigation">{nav}</nav>
<div class="header-actions"><a class="icon-btn" id="bag-link" href="{p}cart.html" aria-label="Shopping cart">{BAG}</a>
<button class="icon-btn menu-btn" id="menu-btn" aria-label="Open menu" aria-expanded="false">{MENU}</button></div></div>
<nav class="mobile-nav" id="mobile-nav" aria-label="Mobile navigation">{mnav}</nav></header>
<main id="main">{main}</main>{footer}
<script>window.BESTOWER_ROOT="{p}";window.PRODUCTS={json.dumps(public_products(), ensure_ascii=False)};</script>
<script src="{p}assets/config.js"></script><script src="{p}assets/app.js"></script></body></html>'''


def public_products():
    return [dict(id=x['id'], name=x['name'], price=x.get('price'), stock=x['stock'], pack=x.get('pack'), variants=x.get('variants') or [],
                 image=x.get('image', ''), fit=x.get('fit', 'cover'), position=x.get('position', 'center'), category=x['category']) for x in PRODUCTS]


def write(path, content):
    full = os.path.join(OUT, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    open(full, 'w', encoding='utf-8').write(content)


def fmt(n):
    return '₹%s' % ('{:,.0f}'.format(n) if n == int(n) else '{:,.2f}'.format(n))


def price_html(x):
    if x.get('price') is None:
        return ''
    if x.get('variants'):
        return '<div class="price">From %s</div>' % fmt(min(v['price'] for v in x['variants']))
    return '<div class="price">%s</div>' % fmt(x['price'])


def photo(x, p, lazy=True):
    if x.get('image'):
        return '<img src="%s%s" alt="%s" %swidth="800" height="800" style="object-position:%s;object-fit:%s"/>' % (
            p, x['image'], E(x['name']), 'loading="lazy" ' if lazy else '', x.get('position', 'center'), x.get('fit', 'cover'))
    return '<div class="ph" role="img" aria-label="%s">%s</div>' % (E(x['name']), E(x['name']))


def card(x, p='', shop_now=False):
    inn = x['stock']
    badge = '<span class="badge in">Available</span>' if inn else '<span class="badge out">Out of stock</span>'
    status = '<div class="stock-line in">Available</div>' if inn else '<div class="stock-line out">Out of stock</div>'
    cta = ('<button class="btn btn-gold add-btn" data-id="%s">Add to Cart</button>' % x['id']) if inn else '<button class="btn" disabled>Out of Stock</button>'
    if shop_now:
        cta = '<a class="btn btn-gold" href="%sproduct/%s.html">Shop Now</a>' % (p, x['id'])
    link = '' if shop_now else '<a class="text-link" href="%sproduct/%s.html">View details</a>' % (p, x['id'])
    return f'''<article class="card{'' if inn else ' oos'}" data-cat="{E(x['category'])}" data-name="{E(x['name'].lower())}">
<a class="card-photo" href="{p}product/{x['id']}.html" aria-label="{E(x['name'])}">{photo(x, p)}{badge}</a>
<div class="card-body"><span class="card-cat">{E(x['category'])}</span><h3><a href="{p}product/{x['id']}.html">{E(x['name'])}</a></h3>
<p class="card-desc">{E(x['short'])}</p>{price_html(x)}{status}
<div class="card-foot">{cta}{link}</div></div></article>'''


ORIGIN_SLOT = '<div class="slot" id="origin-image"><img class="slot-logo" src="%sassets/img/logo.png" alt="" aria-hidden="true"/><img class="fill" src="%sassets/img/origin.png" alt="Where a product comes from matters" onerror="this.remove()"/></div>'


def home():
    feat = ''.join(card(x, shop_now=True) for x in PRODUCTS)
    def ico(d):
        return '<svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">%s</svg>' % d
    trust = [
        (ico('<path d="M12 3l2.6 5.3 5.9.9-4.3 4.1 1 5.8L12 16.300 6.800 19.100l1-5.800L3.500 9.200l5.900-.9z"/>'), 'Carefully selected', 'Products chosen for quality and origin'),
        (ico('<circle cx="12" cy="12" r="9"/><path d="M12 11v5"/><path d="M12 8h.01"/>'), 'Clear product information', 'Honest details, no exaggeration'),
        (ico('<rect x="3" y="11" width="18" height="10" rx="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/>'), 'Secure online payment', 'UPI, cards and net banking'),
        (ico('<path d="M1 6h13v10H1z"/><path d="M14 9h4l3 3v4h-7"/><circle cx="6" cy="18" r="2"/><circle cx="17" cy="18" r="2"/>'), 'India-wide delivery', 'Shipped to your doorstep'),
        (ico('<path d="M22 16.900v3a2 2 0 0 1-2.200 2 19.800 19.800 0 0 1-8.600-3.100 19.500 19.500 0 0 1-6-6A19.800 19.800 0 0 1 2.100 4.200 2 2 0 0 1 4.100 2h3a2 2 0 0 1 2 1.700c.1 1 .4 1.900.7 2.800a2 2 0 0 1-.5 2.100L8.100 9.900a16 16 0 0 0 6 6l1.300-1.300a2 2 0 0 1 2.100-.4c.9.3 1.800.6 2.800.7a2 2 0 0 1 1.700 2z"/>'), 'Direct support', 'Call, WhatsApp or email us')]
    t = ''.join('<div class="trust-item"><span class="trust-ico">%s</span><strong>%s</strong><span class="trust-txt">%s</span></div>' % i for i in trust)
    main = f'''<section aria-label="Welcome">
<div class="hero-media" id="hero-image"><img class="slot-logo" src="assets/img/logo.png" alt="" aria-hidden="true"/><img class="fill" src="assets/img/origin.png" alt="Bestower saffron, dry fruits and natural products" fetchpriority="high" onerror="this.remove()"/></div>
<div class="wrap"><div class="hero-copy"><p class="eyebrow">From the finest origin at your table</p>
<h1>Authentic products. Remarkable origins.</h1>
<p class="lead">Discover carefully selected saffron, dry fruits and natural products sourced with a focus on quality, authenticity and origin.</p>
<div class="btn-row"><a class="btn" href="shop.html">Shop Bestower</a><a class="btn btn-outline" href="shop.html#collection">Explore Our Collection</a></div></div></div></section>
<section class="trust" aria-label="Why Bestower"><div class="wrap trust-in">{t}</div></section>
<section class="section"><div class="wrap"><div class="section-head"><div><p class="eyebrow">Featured products</p><h2>The Bestower collection</h2></div><a class="text-link" href="shop.html">View all products</a></div>
<div class="grid">{feat}</div></div></section>
<section class="section origin" id="origin"><div class="wrap origin-in">{ORIGIN_SLOT % ('', '')}
<div class="origin-copy"><p class="eyebrow">Good things begin at the origin</p><h2>Where a product comes from matters.</h2>
<p style="margin-top:18px">From Kashmir’s saffron and walnuts to carefully selected products from other remarkable regions, Bestower focuses on products where origin, quality and careful selection come together.</p>
<p class="signature">From the finest origin at your table.</p><p style="margin-top:22px"><a class="btn" href="about.html">About</a></p></div></div></section>
<section class="cta-band"><div class="wrap"><h2>Questions about a product?</h2><p>We are happy to help with product information, availability and orders.</p>
<div class="btn-row"><a class="btn" href="https://wa.me/{WA}" target="_blank" rel="noopener">Chat on WhatsApp</a><a class="btn btn-outline" href="contact.html">Contact Bestower</a></div></div></section>'''
    write('index.html', layout(HOME_TITLE, HOME_DESC, main, 0, 'index.html'))


def shop():
    tabs = '<button class="on" data-cat="all">All</button>' + ''.join('<button data-cat="%s">%s</button>' % (E(c), E(c)) for c in CATEGORIES)
    main = f'''<div class="wrap"><div class="page-head"><p class="eyebrow">Shop</p><h1>The Bestower collection</h1>
<p>Saffron, nuts, dry fruits and natural products, chosen with care. Out-of-stock items stay listed so you know what we offer.</p></div>
<div id="collection" class="filters" role="group" aria-label="Filter by category">{tabs}</div>
<div class="grid" id="product-grid">{''.join(card(x) for x in PRODUCTS)}</div>
<div class="empty" id="empty" hidden>New products in this category will be added soon.</div><div style="height:90px"></div></div>'''
    write('shop.html', layout('Shop | Bestower', 'Shop Bestower’s collection of Kashmiri saffron, walnuts, almonds and dry fruits. From the finest origin at your table.', main, 0, 'shop.html'))


def product_pages():
    for x in PRODUCTS:
        p = '../'
        inn = x['stock']
        rows = list(x['details'])
        if x.get('pack') and not any(k == 'Net quantity' for k, _ in rows):
            rows.append(['Pack size', ', '.join(v['pack'] for v in x['variants']) if x.get('variants') else x['pack']])
        rows.append(['Availability', 'Available' if inn else 'Out of stock'])
        facts = ''.join('<tr><th scope="row">%s</th><td>%s</td></tr>' % (E(k), E(v)) for k, v in rows)
        g = x.get('gallery') or []
        thumbs = ''
        if len(g) > 1:
            thumbs = '<div class="thumbs">' + ''.join('<img src="%s%s" alt="%s view %d" class="%s" loading="lazy"/>' % (p, im, E(x['name']), i + 1, 'on' if i == 0 else '') for i, im in enumerate(g)) + '</div>'
        badge = '<span class="badge in">Available</span>' if inn else '<span class="badge out">Out of stock</span>'
        photo_html = '<div class="pdp-photo" id="pdp-photo">%s%s</div>%s' % (photo(x, p, lazy=False), badge, thumbs)
        if inn:
            buy = f'''<div class="buy"><div class="qty"><button type="button" data-qty="-1" aria-label="Decrease quantity">−</button><span id="qty">1</span><button type="button" data-qty="1" aria-label="Increase quantity">+</button></div>
<button class="btn btn-gold" id="add-to-cart" data-id="{x['id']}">Add to Cart</button><button class="btn" id="buy-now" data-id="{x['id']}">Buy Now</button></div>'''
            stock = '<div class="stock-line in">Available</div>'
            oos = ''
        else:
            buy = '<div class="buy"><button class="btn btn-block" disabled>Out of Stock</button></div>'
            stock = '<div class="stock-line out">Out of stock</div>'
            oos = '<div class="oos-note">This product is currently out of stock. Message us on WhatsApp to ask about availability.</div>'
        if x.get('variants'):
            pdp_price = '<div class="pdp-price" id="pdp-price">%s</div>' % fmt(x['variants'][0]['price'])
            packs = '<div class="packs" id="packs" role="group" aria-label="Pack size">' + ''.join(
                '<button type="button" class="pack%s" data-pack="%s" data-price="%s">%s<small>%s</small></button>' % (
                    ' on' if i == 0 else '', E(v['pack']), v['price'], E(v['pack']), fmt(v['price'])) for i, v in enumerate(x['variants'])) + '</div>'
        else:
            pdp_price = price_html(x).replace('class="price"', 'class="pdp-price"')
            packs = ''
        main = f'''<div class="wrap"><nav class="crumbs" aria-label="Breadcrumb"><a href="{p}index.html">Home</a> / <a href="{p}shop.html">Shop</a> / {E(x['name'])}</nav>
<div class="pdp"><div>{photo_html}</div><div class="pdp-info"><p class="eyebrow">{E(x['category'])} · {E(x['origin'])}</p><h1>{E(x['name'])}</h1>
<p class="lead">{E(x['description'])}</p>{pdp_price}{packs}{stock}
<table class="facts"><tbody>{facts}</tbody></table>{buy}{oos}
<div class="note-box"><p><strong>Shipping:</strong> We deliver across India. Delivery charges and timing are shown at checkout. <a class="text-link" href="{p}shipping-delivery.html">Shipping &amp; Delivery</a></p>
<p><strong>Need help?</strong> <a class="text-link" href="https://wa.me/{WA}" target="_blank" rel="noopener">Chat on WhatsApp</a> or call <a class="text-link" href="tel:{PHONE_TEL}">{PHONE_DISPLAY}</a>.</p></div></div></div></div>'''
        write('product/%s.html' % x['id'], layout('%s | Bestower' % x['name'], x['short'] + ' From Bestower, Chennai.', main, 1, 'shop.html'))


def about():
    main = f'''<div class="wrap"><div class="page-head"><p class="eyebrow">About</p><h1>From the finest origin at your table.</h1></div>
<div class="prose" style="padding-bottom:80px"><p class="about-lead">Bestower is a premium Indian specialty-food brand by Bestower Enterprises, based in Chennai.</p>
<p>We bring together carefully selected saffron, dry fruits and natural products from remarkable origins, with a focus on quality, authenticity and honest product information.</p>
<p>Our collection begins with exceptional produce associated with Kashmir and will grow thoughtfully as we discover products worth bringing to your table.</p>
<p class="signature">Origin matters. Quality matters. So does trust.</p>
<p style="margin-top:34px"><a class="btn" href="shop.html">Shop Bestower</a></p></div></div>'''
    write('about.html', layout('About Bestower | Premium Saffron, Dry Fruits & Natural Products', 'Bestower is a premium Indian specialty-food brand by Bestower Enterprises, based in Chennai. From the finest origin at your table.', main, 0, 'about.html'))


def contact():
    main = f'''<div class="wrap"><div class="page-head"><p class="eyebrow">Contact</p><h1>We are here to help.</h1>
<p>Questions about a product, an order or availability? Reach Bestower Enterprises directly. For delivery questions, please include your PIN code; for an existing order, include your order number.</p></div>
<div class="contact-grid"><div class="contact-card"><h3>Call or WhatsApp</h3><p><a href="tel:{PHONE_TEL}">{PHONE_DISPLAY}</a></p></div>
<div class="contact-card"><h3>Email</h3><p><a href="mailto:{EMAIL}">{EMAIL}</a></p></div>
<div class="contact-card"><h3>Based in</h3><p>Perambur, Chennai,<br/>Tamil Nadu, India</p></div></div>
<div class="btn-row" style="justify-content:flex-start;padding-bottom:30px"><a class="btn btn-gold" href="https://wa.me/{WA}" target="_blank" rel="noopener">Chat on WhatsApp</a><a class="btn btn-outline" href="mailto:{EMAIL}">Send an email</a></div>
<p style="padding-bottom:80px;color:var(--muted)">Please do not share card, UPI PIN or other payment details over chat or email.</p></div>'''
    write('contact.html', layout('Contact | Bestower', 'Contact Bestower Enterprises in Perambur, Chennai by phone, WhatsApp or email.', main, 0, 'contact.html'))


def prose_page(fname, title, desc, h1, intro, sections, faq=False):
    body = ''
    for q, a in sections:
        body += ('<details><summary>%s</summary><p>%s</p></details>' % (q, a)) if faq else '<h2>%s</h2><p>%s</p>' % (q, a)
    main = f'''<div class="wrap"><div class="page-head"><p class="eyebrow">{E(title.split(' | ')[0])}</p><h1>{h1}</h1><p>{intro}</p></div>
<div class="prose{' faq' if faq else ''}" style="padding-bottom:80px">{body}
<p style="margin-top:40px"><a class="btn" href="contact.html">Contact Bestower</a></p></div></div>'''
    write(fname, layout(title, desc, main, 0))


def legal():
    prose_page('faq.html', 'FAQs | Bestower', 'Answers to common questions about Bestower products, orders, payment and delivery.', 'Frequently asked questions',
               'Straightforward answers about our products, ordering and delivery.', [
        ('Where is Bestower based?', 'Bestower Enterprises is based in Perambur, Chennai, Tamil Nadu, and delivers across India.'),
        ('Where does your saffron come from?', 'Our Kashmiri Mongra Saffron has Pampore, Kashmir as its origin reference. It is sold in a 1 g glass jar.'),
        ('What if a product is out of stock?', 'Out-of-stock products stay on the website so you can see the full Bestower collection. They cannot be ordered until they are back in stock. Message us on WhatsApp to ask about availability.'),
        ('How can I pay?', 'You can pay online at checkout using UPI, debit or credit cards, net banking and other methods available at checkout.'),
        ('Do you deliver across India?', 'Yes. We ship across India through courier partners. Delivery charges and estimated timing are shown at checkout.'),
        ('How will I track my order?', 'Once your order is dispatched, we share the courier and tracking details with you.'),
        ('Can I ask about a product before ordering?', f'Of course. Call or WhatsApp {PHONE_DISPLAY}, or email {EMAIL}.'),
        ('Where can I find ingredient and allergen information?', 'Please check the product label. Nuts are allergens. Contact us if you need product information before you order.'),
    ], faq=True)
    prose_page('shipping-delivery.html', 'Shipping & Delivery | Bestower', 'Shipping and delivery information for Bestower orders across India.', 'Shipping &amp; delivery',
               'How we get your order from Chennai to your table.', [
        ('Delivery across India', 'Bestower delivers across India. Availability depends on your delivery PIN code.'),
        ('Delivery charges', 'Delivery charges, where applicable, are shown at checkout before you pay.'),
        ('Dispatch and tracking', 'Orders are dispatched through our courier partners after payment is confirmed. We share your courier and tracking details once your order ships.'),
        ('Delivery timing', 'Delivery time varies by location and courier. Please contact us if you need delivery by a specific date.'),
        ('Need help?', f'Call or WhatsApp {PHONE_DISPLAY}, or email {EMAIL}, with your order number.')])
    prose_page('returns-refunds.html', 'Returns & Refunds | Bestower', 'Returns and refunds information for Bestower orders.', 'Returns &amp; refunds',
               'If something is not right with your order, we will help.', [
        ('Damaged, incorrect or missing items', f'Please contact us as soon as possible after delivery at {EMAIL} or {PHONE_DISPLAY}. Include your order number and clear photographs of the item and its packaging, and keep the packaging until we have reviewed the issue.'),
        ('Cancellations and returns', 'Because Bestower sells food products, return eligibility depends on the product and its condition. Please contact us before sending anything back.'),
        ('Refunds', 'Where a refund is due, it is returned to your original payment method. If an item you ordered turns out to be unavailable, we will contact you and refund the amount paid.'),
        ('Your rights', 'Nothing in this policy limits your rights under applicable Indian consumer law.')])
    prose_page('privacy.html', 'Privacy Policy | Bestower', 'How Bestower Enterprises handles your personal information.', 'Privacy policy',
               'Your privacy matters to us.', [
        ('Who we are', f'This website is operated by Bestower Enterprises, Perambur, Chennai, Tamil Nadu. Privacy questions can be sent to {EMAIL}.'),
        ('Information we collect', 'When you place an order we collect your name, mobile number, email address and delivery address so that we can process and deliver it. Your shopping cart is stored in your browser.'),
        ('Payments', 'Payments are processed by our payment partner. Bestower does not see or store your card, UPI or net banking details.'),
        ('How we use your information', 'We use your information to process orders, arrange delivery, provide support and meet legal and accounting requirements. We share it only with service providers needed to do this, such as payment and courier partners.'),
        ('Your choices', f'You can ask us to access, correct or delete your personal information by writing to {EMAIL}, subject to applicable law.')])
    prose_page('terms.html', 'Terms & Conditions | Bestower', 'Terms and conditions for shopping with Bestower.', 'Terms &amp; conditions',
               'Please read these terms before placing an order.', [
        ('About Bestower', 'Bestower is the brand of Bestower Enterprises, based in Perambur, Chennai, Tamil Nadu, India.'),
        ('Products and prices', 'All prices are in Indian rupees (INR). Product availability is shown on each product page; out-of-stock products cannot be ordered.'),
        ('Orders and payment', 'An order is accepted once payment is confirmed and we have confirmed it with you. We may cancel and refund an order if a product is unavailable.'),
        ('Product information', 'Please read the product label for ingredients, allergens, storage and usage information. Nuts are allergens.'),
        ('Contact', f'For any question, contact {EMAIL} or {PHONE_DISPLAY}. These terms do not exclude your rights under applicable Indian consumer law.')])


def cart():
    states = ['Andhra Pradesh', 'Arunachal Pradesh', 'Assam', 'Bihar', 'Chhattisgarh', 'Goa', 'Gujarat', 'Haryana', 'Himachal Pradesh', 'Jharkhand', 'Karnataka', 'Kerala', 'Madhya Pradesh', 'Maharashtra', 'Manipur', 'Meghalaya', 'Mizoram', 'Nagaland', 'Odisha', 'Punjab', 'Rajasthan', 'Sikkim', 'Tamil Nadu', 'Telangana', 'Tripura', 'Uttar Pradesh', 'Uttarakhand', 'West Bengal', 'Andaman and Nicobar Islands', 'Chandigarh', 'Dadra and Nagar Haveli and Daman and Diu', 'Delhi', 'Jammu and Kashmir', 'Ladakh', 'Lakshadweep', 'Puducherry']
    opts = '<option value="">Select state</option>' + ''.join('<option>%s</option>' % s for s in states)
    main = f'''<div class="wrap"><div class="page-head"><p class="eyebrow">Cart</p><h1>Your cart</h1></div><div id="cart-root" data-states="{E(opts)}"><p>Loading your cart…</p></div></div>'''
    write('cart.html', layout('Cart & Checkout | Bestower', 'Review your Bestower cart and check out securely.', main, 0))


def clean():
    for pat in ['*.html', 'product/*.html']:
        for f in glob.glob(os.path.join(OUT, pat)):
            os.remove(f)
    for f in ['assets/site-orig.css', 'assets/extra.css']:
        fp = os.path.join(OUT, f)
        if os.path.exists(fp):
            os.remove(fp)


if __name__ == '__main__':
    clean()
    home(); shop(); product_pages(); about(); contact(); legal(); cart()
    print('Built', len(PRODUCTS), 'products ->', OUT)
