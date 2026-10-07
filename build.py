#!/usr/bin/env python3
"""Bestower static site generator.
Run:  npm run build   (or python3 build.py)  ->  writes the site into ./public
Edit products in products.json (flip "stock" to true, add "price"/"pack") and rebuild.
"""
import json
import html
import os
import shutil
import glob
from jinja2 import Environment, FileSystemLoader

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

# Setup Jinja2 Environment
env = Environment(loader=FileSystemLoader(os.path.join(ROOT, 'templates')))

def public_products():
    return [dict(id=x['id'], name=x['name'], price=x.get('price'), stock=x['stock'], pack=x.get('pack'), variants=x.get('variants') or [],
                 image=x.get('image', ''), fit=x.get('fit', 'cover'), position=x.get('position', 'center'), category=x['category']) for x in PRODUCTS]

def fmt(n):
    return '₹%s' % ('{:,.0f}'.format(n) if n == int(n) else '{:,.2f}'.format(n))

def write(path, content):
    full = os.path.join(OUT, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, 'w', encoding='utf-8') as f:
        f.write(content)

def render_page(template_name, path, title, desc, active='', depth=0, **kwargs):
    template = env.get_template(template_name)
    p = '../' * depth
    context = {
        'title': title,
        'desc': desc,
        'active': active,
        'p': p,
        'phone_tel': PHONE_TEL,
        'phone_display': PHONE_DISPLAY,
        'wa': WA,
        'email': EMAIL,
        'wa_icon': WA_ICON,
        'nav': NAV,
        'bag': BAG,
        'menu': MENU,
        'public_products': json.dumps(public_products(), ensure_ascii=False),
        'fmt': fmt
    }
    context.update(kwargs)
    content = template.render(**context)
    write(path, content)

def home():
    def ico(d):
        return f'<svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{d}</svg>'
    
    trust = [
        (ico('<path d="M12 3l2.6 5.3 5.9.9-4.3 4.1 1 5.8L12 16.300 6.800 19.100l1-5.800L3.500 9.200l5.900-.9z"/>'), 'Carefully selected', 'Products chosen for quality and origin'),
        (ico('<circle cx="12" cy="12" r="9"/><path d="M12 11v5"/><path d="M12 8h.01"/>'), 'Clear product information', 'Honest details, no exaggeration'),
        (ico('<rect x="3" y="11" width="18" height="10" rx="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/>'), 'Secure online payment', 'UPI, cards and net banking'),
        (ico('<path d="M1 6h13v10H1z"/><path d="M14 9h4l3 3v4h-7"/><circle cx="6" cy="18" r="2"/><circle cx="17" cy="18" r="2"/>'), 'India-wide delivery', 'Shipped to your doorstep'),
        (ico('<path d="M22 16.900v3a2 2 0 0 1-2.200 2 19.800 19.800 0 0 1-8.600-3.100 19.500 19.500 0 0 1-6-6A19.800 19.800 0 0 1 2.100 4.200 2 2 0 0 1 4.100 2h3a2 2 0 0 1 2 1.700c.1 1 .4 1.900.7 2.800a2 2 0 0 1-.5 2.100L8.100 9.900a16 16 0 0 0 6 6l1.300-1.300a2 2 0 0 1 2.100-.4c.9.3 1.800.6 2.800.7a2 2 0 0 1 1.700 2z"/>'), 'Direct support', 'Call, WhatsApp or email us')
    ]
    render_page('index.html', 'index.html', HOME_TITLE, HOME_DESC, active='index.html', products=PRODUCTS, trust=trust)

def shop():
    render_page('shop.html', 'shop.html', 'Shop | Bestower', 'Shop Bestower’s collection of Kashmiri saffron, walnuts, almonds and dry fruits. From the finest origin at your table.', active='shop.html', products=PRODUCTS, categories=CATEGORIES)

def product_pages():
    for x in PRODUCTS:
        rows = list(x.get('details', {}))
        if x.get('pack') and not any(k == 'Net quantity' for k, _ in rows):
            pack_val = ', '.join(v['pack'] for v in x['variants']) if x.get('variants') else x['pack']
            rows.append(['Pack size', pack_val])
        
        render_page(
            'product.html',
            f"product/{x['id']}.html",
            f"{x['name']} | Bestower",
            f"{x['short']} From Bestower, Chennai.",
            active='shop.html',
            depth=1,
            x=x,
            rows=rows
        )

def about():
    render_page('about.html', 'about.html', 'About Bestower | Premium Saffron, Dry Fruits & Natural Products', 'Bestower is a premium Indian specialty-food brand by Bestower Enterprises, based in Chennai. From the finest origin at your table.', active='about.html')

def contact():
    render_page('contact.html', 'contact.html', 'Contact | Bestower', 'Contact Bestower Enterprises in Perambur, Chennai by phone, WhatsApp or email.', active='contact.html')

def prose_page(fname, title, desc, h1, intro, sections, faq=False):
    render_page('prose.html', fname, title, desc, h1=h1, intro=intro, sections=sections, faq=faq)

def legal():
    prose_page('faq.html', 'FAQs | Bestower', 'Answers to common questions about Bestower products, orders, payment and delivery.', 'Frequently asked questions', 'Straightforward answers about our products, ordering and delivery.', [
        ('Where is Bestower based?', 'Bestower Enterprises is based in Perambur, Chennai, Tamil Nadu, and delivers across India.'),
        ('Where does your saffron come from?', 'Our Kashmiri Mongra Saffron has Pampore, Kashmir as its origin reference. It is sold in a 1 g glass jar.'),
        ('What if a product is out of stock?', 'Out-of-stock products stay on the website so you can see the full Bestower collection. They cannot be ordered until they are back in stock. Message us on WhatsApp to ask about availability.'),
        ('How can I pay?', 'You can pay online at checkout using UPI, debit or credit cards, net banking and other methods available at checkout.'),
        ('Do you deliver across India?', 'Yes. We ship across India through courier partners. Delivery charges and estimated timing are shown at checkout.'),
        ('How will I track my order?', 'Once your order is dispatched, we share the courier and tracking details with you.'),
        ('Can I ask about a product before ordering?', f'Of course. Call or WhatsApp {PHONE_DISPLAY}, or email {EMAIL}.'),
        ('Where can I find ingredient and allergen information?', 'Please check the product label. Nuts are allergens. Contact us if you need product information before you order.'),
    ], faq=True)
    
    prose_page('shipping-delivery.html', 'Shipping & Delivery | Bestower', 'Shipping and delivery information for Bestower orders across India.', 'Shipping &amp; delivery', 'How we get your order from Chennai to your table.', [
        ('Delivery across India', 'Bestower delivers across India. Availability depends on your delivery PIN code.'),
        ('Delivery charges', 'Delivery charges, where applicable, are shown at checkout before you pay.'),
        ('Dispatch and tracking', 'Orders are dispatched through our courier partners after payment is confirmed. We share your courier and tracking details once your order ships.'),
        ('Delivery timing', 'Delivery time varies by location and courier. Please contact us if you need delivery by a specific date.'),
        ('Need help?', f'Call or WhatsApp {PHONE_DISPLAY}, or email {EMAIL}, with your order number.')
    ])
    
    prose_page('returns-refunds.html', 'Returns & Refunds | Bestower', 'Returns and refunds information for Bestower orders.', 'Returns &amp; refunds', 'If something is not right with your order, we will help.', [
        ('Damaged, incorrect or missing items', f'Please contact us as soon as possible after delivery at {EMAIL} or {PHONE_DISPLAY}. Include your order number and clear photographs of the item and its packaging, and keep the packaging until we have reviewed the issue.'),
        ('Cancellations and returns', 'Because Bestower sells food products, return eligibility depends on the product and its condition. Please contact us before sending anything back.'),
        ('Refunds', 'Where a refund is due, it is returned to your original payment method. If an item you ordered turns out to be unavailable, we will contact you and refund the amount paid.'),
        ('Your rights', 'Nothing in this policy limits your rights under applicable Indian consumer law.')
    ])
    
    prose_page('privacy.html', 'Privacy Policy | Bestower', 'How Bestower Enterprises handles your personal information.', 'Privacy policy', 'Your privacy matters to us.', [
        ('Who we are', f'This website is operated by Bestower Enterprises, Perambur, Chennai, Tamil Nadu. Privacy questions can be sent to {EMAIL}.'),
        ('Information we collect', 'When you place an order we collect your name, mobile number, email address and delivery address so that we can process and deliver it. Your shopping cart is stored in your browser.'),
        ('Payments', 'Payments are processed by our payment partner. Bestower does not see or store your card, UPI or net banking details.'),
        ('How we use your information', 'We use your information to process orders, arrange delivery, provide support and meet legal and accounting requirements. We share it only with service providers needed to do this, such as payment and courier partners.'),
        ('Your choices', f'You can ask us to access, correct or delete your personal information by writing to {EMAIL}, subject to applicable law.')
    ])
    
    prose_page('terms.html', 'Terms & Conditions | Bestower', 'Terms and conditions for shopping with Bestower.', 'Terms &amp; conditions', 'Please read these terms before placing an order.', [
        ('About Bestower', 'Bestower is the brand of Bestower Enterprises, based in Perambur, Chennai, Tamil Nadu, India.'),
        ('Products and prices', 'All prices are in Indian rupees (INR). Product availability is shown on each product page; out-of-stock products cannot be ordered.'),
        ('Orders and payment', 'An order is accepted once payment is confirmed and we have confirmed it with you. We may cancel and refund an order if a product is unavailable.'),
        ('Product information', 'Please read the product label for ingredients, allergens, storage and usage information. Nuts are allergens.'),
        ('Contact', f'For any question, contact {EMAIL} or {PHONE_DISPLAY}. These terms do not exclude your rights under applicable Indian consumer law.')
    ])

def cart():
    states = ['Andhra Pradesh', 'Arunachal Pradesh', 'Assam', 'Bihar', 'Chhattisgarh', 'Goa', 'Gujarat', 'Haryana', 'Himachal Pradesh', 'Jharkhand', 'Karnataka', 'Kerala', 'Madhya Pradesh', 'Maharashtra', 'Manipur', 'Meghalaya', 'Mizoram', 'Nagaland', 'Odisha', 'Punjab', 'Rajasthan', 'Sikkim', 'Tamil Nadu', 'Telangana', 'Tripura', 'Uttar Pradesh', 'Uttarakhand', 'West Bengal', 'Andaman and Nicobar Islands', 'Chandigarh', 'Dadra and Nagar Haveli and Daman and Diu', 'Delhi', 'Jammu and Kashmir', 'Ladakh', 'Lakshadweep', 'Puducherry']
    opts = '<option value="">Select state</option>' + ''.join('<option>%s</option>' % s for s in states)
    render_page('cart.html', 'cart.html', 'Cart & Checkout | Bestower', 'Review your Bestower cart and check out securely.', opts=opts)

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
    home()
    shop()
    product_pages()
    about()
    contact()
    legal()
    cart()
    print('Built', len(PRODUCTS), 'products ->', OUT)
