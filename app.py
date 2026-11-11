import streamlit as st
import qrcode
from io import BytesIO
from datetime import datetime

st.set_page_config(
    page_title="Vyapar QR | POS Billing & Dynamic UPI",
    page_icon="⚡",
    layout="wide"
)

# Custom High-Trust POS Styling
st.markdown("""
<style>
    .pos-card {
        background-color: #ffffff;
        border: 2px dashed #0f172a;
        border-radius: 12px;
        padding: 20px;
        text-align: center;
    }
    .amount-badge {
        font-size: 36px;
        font-weight: 800;
        color: #16a34a;
        margin: 8px 0;
    }
    .meta-text {
        font-size: 13px;
        color: #64748b;
    }
    .cart-box {
        background-color: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        padding: 12px;
        margin-top: 10px;
    }
</style>
""", unsafe_allow_html=True)

# Session State for Running Cart
if "cart" not in st.session_state:
    st.session_state.cart = {}

def add_to_cart(item_name, price):
    if item_name in st.session_state.cart:
        st.session_state.cart[item_name]["qty"] += 1
    else:
        st.session_state.cart[item_name] = {"price": price, "qty": 1}

def clear_cart():
    st.session_state.cart = {}

# Sidebar: Merchant Config
with st.sidebar:
    st.header("⚙️ Merchant Setup")
    vpa = st.text_input("UPI ID (VPA):", value="7007060617@kotak", help="Customer will pay directly to this UPI address")
    merchant_name = st.text_input("Business / Store Name:", value="My Store")
    currency = "INR"
    st.write("---")
    if st.button("🗑️ Clear Entire Bill / Cart", use_container_width=True, type="secondary"):
        clear_cart()
        st.rerun()

# Layout: Left side POS Item Tapper, Right side Live Dynamic QR & Bill
col_pos, col_qr = st.columns([1.1, 1], gap="large")

# Common Indian daily retail presets
PRESET_ITEMS = [
    {"name": "Chai ☕", "price": 10.0},
    {"name": "Special Tea ☕", "price": 15.0},
    {"name": "Samosa 🥟", "price": 15.0},
    {"name": "Bread Pakora 🥪", "price": 20.0},
    {"name": "Water Bottle 💧", "price": 20.0},
    {"name": "Cold Drink (Can) 🥤", "price": 40.0},
    {"name": "Chips / Namkeen 🥨", "price": 20.0},
    {"name": "Sweet / Mithai 🍬", "price": 30.0},
    {"name": "Coffee 🍵", "price": 25.0},
]

with col_pos:
    st.subheader("🛍️ 1. Quick Item Tap (POS)")
    st.caption("Tap items to instantly add them to customer bill")

    # Display items in a responsive grid
    for i in range(0, len(PRESET_ITEMS), 3):
        cols = st.columns(3)
        for j in range(3):
            if i + j < len(PRESET_ITEMS):
                item = PRESET_ITEMS[i + j]
                with cols[j]:
                    if st.button(f"{item['name']}\n₹{int(item['price'])}", key=f"btn_{item['name']}", use_container_width=True):
                        add_to_cart(item['name'], item['price'])
                        st.rerun()

    st.write("---")
    st.subheader("➕ Custom Extra Amount")
    c_custom1, c_custom2 = st.columns([2, 1])
    with c_custom1:
        custom_amt = st.number_input("Add manual amount (₹):", min_value=1.0, value=50.0, step=10.0)
    with c_custom2:
        st.write("")
        st.write("")
        if st.button("Add to Bill", use_container_width=True):
            add_to_cart(f"Custom Item (₹{int(custom_amt)})", custom_amt)
            st.rerun()

# Calculate Total
total_bill = sum(data["price"] * data["qty"] for data in st.session_state.cart.values())
if total_bill == 0.0:
    total_bill = 10.0 # Default starting fallback if cart empty

with col_qr:
    st.subheader("⚡ 2. Instant Locked QR")
    
    formatted_amount = f"{total_bill:.2f}"
    encoded_name = merchant_name.replace(" ", "%20")
    encoded_note = f"Bill_{datetime.now().strftime('%H%M%S')}"
    upi_url = f"upi://pay?pa={vpa}&pn={encoded_name}&am={formatted_amount}&cu={currency}&tn={encoded_note}"

    # Generate QR Code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=10,
        border=2,
    )
    qr.add_data(upi_url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="#0f172a", back_color="#ffffff")

    buf = BytesIO()
    img.save(buf, format="PNG")
    byte_im = buf.getvalue()

    # POS Screen Display
    st.markdown(f"""
    <div class="pos-card">
        <div class="meta-text">PAY TO: <b>{merchant_name.upper()}</b> ({vpa})</div>
        <div class="amount-badge">₹{formatted_amount}</div>
        <div class="meta-text">Scan with any UPI App. Exact amount is locked.</div>
    </div>
    """, unsafe_allow_html=True)

    st.write("")
    col_img1, col_img2, col_img3 = st.columns([1, 2, 1])
    with col_img2:
        st.image(byte_im, caption=f"Locked Scan for ₹{formatted_amount}", use_container_width=True)

    # Itemized Breakdown
    with st.expander("🧾 Active Cart & Bill Breakdown", expanded=True):
        if st.session_state.cart:
            for item, details in st.session_state.cart.items():
                st.write(f"• **{item}** × {details['qty']} = ₹{details['price'] * details['qty']:.2f}")
            st.write(f"**Total Payable:** ₹{formatted_amount}")
        else:
            st.info("No items tapped yet. Default ₹10.00 fallback active.")
        
        st.download_button(
            label="📥 Download QR (PNG)",
            data=byte_im,
            file_name=f"upi_qr_{formatted_amount}.png",
            mime="image/png",
            use_container_width=True
        )
