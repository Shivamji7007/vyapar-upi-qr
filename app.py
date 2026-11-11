import streamlit as st
import qrcode
from io import BytesIO
from datetime import datetime

st.set_page_config(
    page_title="Vyapar QR | Instant Dynamic UPI Generator",
    page_icon="⚡",
    layout="centered"
)

# Custom Styling for POS Receipt Look
st.markdown("""
<style>
    .qr-container {
        background-color: #ffffff;
        border: 2px dashed #0f172a;
        border-radius: 12px;
        padding: 24px;
        text-align: center;
        margin-top: 20px;
    }
    .amount-badge {
        font-size: 32px;
        font-weight: 800;
        color: #16a34a;
        margin: 10px 0;
    }
    .meta-text {
        font-size: 13px;
        color: #64748b;
    }
</style>
""", unsafe_allow_html=True)

st.title("⚡ Vyapar Instant UPI QR")
st.caption("Generate zero-fee, amount-locked payment QR codes with digital bill slips")

# Merchant Configuration (Sidebar)
with st.sidebar:
    st.header("⚙️ Merchant Setup")
    vpa = st.text_input("UPI ID (VPA):", value="example@upi", help="Enter your valid UPI ID (e.g. 9876543210@paytm, name@okhdfcbank)")
    merchant_name = st.text_input("Business / Payee Name:", value="My Store")
    currency = "INR"

# Billing Input Form
c1, c2 = st.columns([1, 1])
with c1:
    amount = st.number_input("Bill Amount (₹):", min_value=1.0, max_value=100000.0, value=150.0, step=10.0)
with c2:
    note = st.text_input("Bill Note / Item Ref:", value="Counter Bill #101")

col_quick1, col_quick2, col_quick3, col_quick4 = st.columns(4)
# Quick add buttons
quick_add = None
if col_quick1.button("+ ₹50"): amount += 50
if col_quick2.button("+ ₹100"): amount += 100
if col_quick3.button("+ ₹200"): amount += 200
if col_quick4.button("+ ₹500"): amount += 500

# Generate Valid NPCI UPI String
# Format: upi://pay?pa={vpa}&pn={name}&am={amount}&cu=INR&tn={note}
formatted_amount = f"{amount:.2f}"
encoded_name = merchant_name.replace(" ", "%20")
encoded_note = note.replace(" ", "%20")
upi_url = f"upi://pay?pa={vpa}&pn={encoded_name}&am={formatted_amount}&cu={currency}&tn={encoded_note}"

# Render QR Code
qr = qrcode.QRCode(
    version=1,
    error_correction=qrcode.constants.ERROR_CORRECT_M,
    box_size=10,
    border=2,
)
qr.add_data(upi_url)
qr.make(fit=True)
img = qr.make_image(fill_color="#0f172a", back_color="#ffffff")

# Convert to in-memory bytes for display and download
buf = BytesIO()
img.save(buf, format="PNG")
byte_im = buf.getvalue()

# Display Customer Facing Screen
st.markdown(f"""
<div class="qr-container">
    <div class="meta-text">PAY TO: <b>{merchant_name.upper()}</b> ({vpa})</div>
    <div class="amount-badge">₹{formatted_amount}</div>
    <div class="meta-text">Scan with GPay, PhonePe, Paytm, or BHIM. Amount is pre-locked.</div>
</div>
""", unsafe_allow_html=True)

st.write("")
col_left, col_center, col_right = st.columns([1, 2, 1])
with col_center:
    st.image(byte_im, caption=f"Direct Scan for ₹{formatted_amount}", use_container_width=True)

# Actions Row
st.write("---")
btn_col1, btn_col2 = st.columns(2)

with btn_col1:
    st.download_button(
        label="📥 Download QR Image (PNG)",
        data=byte_im,
        file_name=f"upi_qr_{formatted_amount}.png",
        mime="image/png",
        use_container_width=True
    )

with btn_col2:
    # Direct UPI Intent for mobile web visitors
    st.link_button(
        "📱 Open in Installed UPI App",
        upi_url,
        use_container_width=True
    )

# Printable Text Receipt
with st.expander("🧾 View / Print Text Receipt"):
    st.code(f"""
=======================================
           {merchant_name.upper()}
=======================================
Date: {datetime.now().strftime('%d-%b-%Y %I:%M %p')}
Note: {note}
---------------------------------------
TOTAL PAYABLE:           Rs. {formatted_amount}
Payment Mode:            UPI
VPA:                     {vpa}
Status:                  QR Generated
=======================================
    Scan QR to complete instant settlement
""", language="text")
