import streamlit as st
import sqlite3
import smtplib
import random
import string
import hashlib
import torch
import torch.nn as nn
import torchvision.transforms as transforms
from PIL import Image
import os
import numpy as np
import cv2
from fpdf import FPDF
from datetime import datetime

# -----------------------
# Create a .streamlit theme file (if not present) to improve native Streamlit look
# -----------------------
try:
    os.makedirs(".streamlit", exist_ok=True)
    cfg_path = os.path.join(".streamlit", "config.toml")
    if not os.path.exists(cfg_path):
        with open(cfg_path, "w", encoding="utf-8") as f:
            f.write(
"""[theme]
primaryColor = "#0ea5e9"
backgroundColor = "#f8fbff"
secondaryBackgroundColor = "#ffffff"
textColor = "#0f172a"
font = "sans serif"
"""
            )
except Exception:
    pass

# ======================
# Database Setup
# ======================
conn = sqlite3.connect("users.db", check_same_thread=False)
c = conn.cursor()
c.execute("""CREATE TABLE IF NOT EXISTS users
             (username TEXT, email TEXT, password TEXT)""")
c.execute("""CREATE TABLE IF NOT EXISTS history
             (email TEXT, result TEXT, confidence REAL, stage TEXT, date TEXT)""")
conn.commit()

# ======================
# Helper Functions
# ======================
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def add_user(username, email, password):
    c.execute("INSERT INTO users (username, email, password) VALUES (?,?,?)",
              (username, email, hash_password(password)))
    conn.commit()

def login_user(email, password):
    c.execute("SELECT * FROM users WHERE email=? AND password=?",
              (email, hash_password(password)))
    return c.fetchone()

def get_user(email):
    c.execute("SELECT * FROM users WHERE email=?", (email,))
    return c.fetchone()

def send_otp(receiver_email, otp):
    sender_email = "vv690396@gmail.com"
    sender_password = ""  # Use Gmail App Password
    subject = "Password Reset OTP"
    body = f"Your OTP for password reset is: {otp}"
    message = f"Subject: {subject}\n\n{body}"
    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, receiver_email, message)
        server.quit()
        return True
    except Exception as e:
        st.error(f"Error sending email: {e}")
        return False

# ======================
# Model settings & labels
# ======================
MODEL_PATH = "model.pth"
IMG_SIZE = (224, 224)

stage_labels = [
    "Stage 0 - Healthy",
    "Stage 1 - Superficial",
    "Stage 2 - Deep",
    "Stage 3 - Infected",
    "Stage 4 - Gangrene"
]

# ======================
# Model class (matches trained model)
# - features output: 32 x 56 x 56
# - classifier expects 32*56*56 flattened
# - final linear outputs 5 classes
# ======================
# Inside app.py
class SimpleCNN(nn.Module):
    def __init__(self):
        super(SimpleCNN, self).__init__()
        self.features = nn.Sequential(
            nn.Conv2d(3, 16, 3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2),
            nn.Conv2d(16, 32, 3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2)
        )
        self.classifier = nn.Sequential(
            nn.Flatten(),
            nn.Linear(32 * 56 * 56, 128),
            nn.ReLU(),
            nn.Linear(128, 5)
        )

    def forward(self, x):
        x = self.features(x)
        x = self.classifier(x)
        return x


# ======================
# Preprocess function (must match training preprocessing)
# ======================
def preprocess_image(image: Image.Image):
    transform = transforms.Compose([
        transforms.Resize(IMG_SIZE),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406],
                             [0.229, 0.224, 0.225])  # use if training used ImageNet normalization
    ])
    return transform(image).unsqueeze(0)

# ======================
# Grad-CAM heatmap
# ======================
def generate_gradcam(model, image_tensor, target_layer):
    gradients = []
    activations = []

    def backward_hook(module, grad_input, grad_output):
        gradients.append(grad_output[0])

    def forward_hook(module, input, output):
        activations.append(output)

    hook_f = target_layer.register_forward_hook(forward_hook)
    try:
        hook_b = target_layer.register_full_backward_hook(backward_hook)
    except Exception:
        hook_b = target_layer.register_backward_hook(backward_hook)

    output = model(image_tensor)
    pred_class = output.argmax(dim=1)
    model.zero_grad()
    output[0, pred_class].backward()

    grad = gradients[0].mean(dim=[2, 3], keepdim=True)
    activation = activations[0]
    cam = (activation * grad).sum(dim=1).squeeze()
    cam = torch.relu(cam)
    if cam.max() != 0:
        cam = cam / cam.max()
    cam = cam.detach().cpu().numpy()
    cam = cv2.resize(cam, (IMG_SIZE[0], IMG_SIZE[1]))

    hook_f.remove()
    try:
        hook_b.remove()
    except Exception:
        pass

    return cam

# ======================
# PDF Report
# ======================
def generate_report(user, result, confidence, stage, timestamp, image_bytes=None):
    pdf = FPDF()
    pdf.add_page()

    # IMPORTANT: Set font FIRST
    pdf.set_font("Arial", size=12)

    # Safe margins
    pdf.set_left_margin(15)
    pdf.set_right_margin(15)
    pdf.set_auto_page_break(auto=True, margin=15)

    # Title
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "DFU Detection Report", ln=True, align="C")
    pdf.ln(8)

    # Body text
    pdf.set_font("Arial", size=12)
    pdf.cell(0, 8, f"User: {user}", ln=True)
    pdf.cell(0, 8, f"Result: {result}", ln=True)
    pdf.cell(0, 8, f"Confidence: {confidence*100:.2f}%", ln=True)
    pdf.cell(0, 8, f"Predicted Stage: {stage}", ln=True)
    pdf.cell(0, 8, f"Date: {timestamp}", ln=True)

    # Image page
    if image_bytes:
        tmp_img_path = "temp_report_image.png"
        with open(tmp_img_path, "wb") as f:
            f.write(image_bytes)

        pdf.add_page()
        pdf.image(tmp_img_path, x=15, y=20, w=180)
        os.remove(tmp_img_path)

    pdf.output("dfu_report.pdf")



# DFU stage descriptions (unchanged)
stage_descriptions = {
    "Stage 0 - Healthy Foot": "No ulcer detected, preventive care recommended. Keep feet clean and moisturized.",
    "Stage 1 - Superficial Ulcer": "Surface-level skin damage. Monitor closely; clean wound and consult a clinician if it persists.",
    "Stage 2 - Deep Ulcer": "Tissue involvement detected. Requires medical attention; consider wound dressing and evaluation.",
    "Stage 3 - Ulcer with Infection/Osteomyelitis": "Signs of infection — seek immediate medical care; antibiotics and imaging may be required.",
    "Stage 4 - Partial Gangrene": "Serious tissue damage detected; urgent specialist assessment needed."
}

# ======================
# UI Styling (unchanged)
# ======================
st.set_page_config(page_title="DFU Detection", page_icon="🦶", layout="wide")
st.markdown(
    """
    <style>
    .stApp { background: linear-gradient(180deg, #f7fbff 0%, #f0f9ff 100%); color: #0f172a; }
    .card { border-radius: 12px; padding: 18px; background: #ffffff; box-shadow: 0 6px 20px rgba(16,24,40,0.08); margin-bottom: 16px; }
    .header { background: linear-gradient(90deg, rgba(14,165,233,0.12), rgba(96,165,250,0.08)); padding: 18px; border-radius: 12px; margin-bottom: 16px; }
    .small { font-size: 14px; color: #475569; }
    footer { visibility: hidden; }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="header">
        <h1 style="margin:0;">🦶 DFU Detection — AI Dashboard</h1>
        <p class="small" style="margin:0;">Upload thermal foot images → get detection, stage simulation, Grad-CAM explanation, pdf report & history.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ---------------------
# Session init
# ---------------------
if "user" not in st.session_state:
    st.session_state["user"] = None
if "otp" not in st.session_state:
    st.session_state["otp"] = None
if "reset_email" not in st.session_state:
    st.session_state["reset_email"] = None

menu = ["Login", "Sign Up", "Forgot Password"]
choice = st.sidebar.selectbox("Menu", menu)

with st.sidebar:
    st.markdown("## ⚙️ Model Settings")
    threshold = st.slider("Confidence Threshold", 0.0, 1.0, 0.5)
    visualize_heatmap = st.checkbox("Show Heatmap", value=True)
    show_chart = st.checkbox("Show Confidence Chart", value=True)
    st.markdown("---")
    st.markdown("### 📣 Quick Actions")
    st.write("Use the sidebar to switch between Login/Sign Up/Forgot Password.")
    st.markdown("---")
    feedback_side = st.text_area("Share quick feedback (optional)", height=80)
    if st.button("Send Feedback"):
        st.success("Thanks for the feedback! (Not persisted)")
if choice == "Sign Up":
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("Create New Account")
    username = st.text_input("Username")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    if st.button("Sign Up"):
        if get_user(email):
            st.warning("Email already registered!")
        else:
            add_user(username, email, password)
            st.success("Account created! Please login.")
    st.markdown('</div>', unsafe_allow_html=True)

elif choice == "Login":
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("Login to Your Account")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        result = login_user(email, password)
        if result:
            st.success(f"Welcome {result[0]}!")
            st.session_state["user"] = result
        else:
            st.error("Invalid credentials!")
    st.markdown('</div>', unsafe_allow_html=True)

elif choice == "Forgot Password":
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("Reset Password via OTP")
    email = st.text_input("Enter your registered Email")
    if st.button("Send OTP"):
        user = get_user(email)
        if user:
            otp = "".join(random.choices(string.digits, k=6))
            st.session_state["reset_email"] = email
            st.session_state["otp"] = otp
            if send_otp(email, otp):
                st.success("OTP sent! Please check your email.")
        else:
            st.error("Email not found!")
    if st.session_state["otp"]:
        entered_otp = st.text_input("Enter OTP")
        new_password = st.text_input("New Password", type="password")
        if st.button("Reset Password"):
            if entered_otp == st.session_state["otp"]:
                c.execute("UPDATE users SET password=? WHERE email=?",
                          (hash_password(new_password), st.session_state["reset_email"]))
                conn.commit()
                st.success("Password reset successfully! Please login.")
                st.session_state["otp"] = None
            else:
                st.error("Invalid OTP!")
    st.markdown('</div>', unsafe_allow_html=True)

# ----------------------
# Main DFU Detection Dashboard
# ----------------------
if st.session_state["user"]:
    user_obj = st.session_state["user"]
    username_display = user_obj[0]
    email_display = user_obj[1]

    # Welcome & Stats
    with st.container():
        st.markdown('<div class="card">', unsafe_allow_html=True)
        col1, col2, col3 = st.columns([2,1,1])
        with col1:
            st.markdown(f"**👋 Welcome back, {username_display}**")
            st.markdown("Upload a thermal foot image (jpg/png) and get an explainable detection result.")
        rows_all = c.execute("SELECT email, result, confidence, stage, date FROM history WHERE email=?", (email_display,)).fetchall()
        total_preds = len(rows_all)
        last_pred = rows_all[-1][1] if rows_all else "—"
        last_date = rows_all[-1][4] if rows_all else "—"
        with col2:
            st.metric("Total Predictions", total_preds)
        with col3:
            st.metric("Last Result", last_pred, delta=last_date)
        st.markdown('</div>', unsafe_allow_html=True)

    left_col, right_col = st.columns([1.2, 1])

    # Left: upload & preview
    with left_col:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("Upload Image")
        uploaded_file = st.file_uploader("Upload a foot image (jpg, jpeg, png)", type=["jpg", "jpeg", "png"])
        feedback = st.text_input("Add notes for this image (optional)")
        st.markdown('</div>', unsafe_allow_html=True)

        if uploaded_file:
            image = Image.open(uploaded_file).convert("RGB")
            try:
                uploaded_file.seek(0)
                image_bytes = uploaded_file.read()
            except Exception:
                image_bytes = None
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.subheader("Preview")
            st.image(image, caption="Uploaded Image", use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

    # Right: prediction & explanation
    with right_col:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("Prediction & Explanation")

        if not os.path.exists(MODEL_PATH):
            st.error("⚠ Model file not found! Please place 'model.pth' in the app folder.")
        else:
            # load model and handle possible load errors
            model = SimpleCNN()
            try:
                model.load_state_dict(torch.load(MODEL_PATH, map_location="cpu"))
                model.eval()
            except Exception as e:
                st.error(f"Model load error: {e}")
                st.markdown('</div>', unsafe_allow_html=True)
                st.stop()

            if uploaded_file:
                input_tensor = preprocess_image(image)

                with torch.no_grad():
                    output = model(input_tensor)
                    probabilities = torch.softmax(output, dim=1)
                    predicted_class = torch.argmax(probabilities).item()
                    confidence = probabilities[0][predicted_class].item()

                # Map predicted class index to stage label
                predicted_stage = stage_labels[predicted_class]

                # Display results
                st.metric(label="Predicted Stage", value=predicted_stage)
                st.metric(label="Confidence", value=f"{confidence*100:.2f}%")

                # Color-coded stage pill
                stage_color = "✅" if "Healthy" in predicted_stage else "⚠️"
                st.markdown(f"**Detected Stage:** {stage_color} **{predicted_stage}**")

                st.progress(int(min(max(confidence, 0.0), 1.0) * 100))

                if show_chart:
                    st.write("### Confidence Scores")
                    # build chart dict dynamically (safe indexing)
                    chart_dict = {}
                    for i, label in enumerate(stage_labels):
                        chart_dict[label] = float(probabilities[0][i].item())
                    st.bar_chart(chart_dict)

                with st.expander("🩺 Stage Description & Care Tips", expanded=True):
                    desc = stage_descriptions.get(predicted_stage, "No description available.")
                    st.write(f"**{predicted_stage}**")
                    st.write(desc)
                    st.write("---")
                    st.write("**Care tips (general):**")
                    st.write("""
                    - Keep the wound clean and dry.  
                    - Inspect feet daily for cuts, blisters, or redness.  
                    - Offload pressure from affected area (use protective footwear).  
                    - Consult a healthcare professional for wounds that don't improve.
                    """)

                # Grad-CAM (use the second conv layer as target)
                if visualize_heatmap:
                    try:
                        cam = generate_gradcam(model, input_tensor, model.features[3])  # features[3] is second conv in this structure
                        heatmap = cv2.applyColorMap(np.uint8(255 * cam), cv2.COLORMAP_JET)
                        overlay = cv2.addWeighted(np.array(image.resize((IMG_SIZE[0], IMG_SIZE[1]))), 0.6, heatmap, 0.4, 0)
                        st.image(overlay, caption="Grad-CAM Heatmap Overlay", use_container_width=True)
                    except Exception as e:
                        st.error(f"Heatmap generation error: {e}")

                # Save to history (store stage label)
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                try:
                    c.execute("INSERT INTO history VALUES (?,?,?,?,?)",
                              (email_display,
                               predicted_stage,
                               float(confidence),
                               predicted_stage,
                               timestamp))
                    conn.commit()
                except Exception as e:
                    st.error(f"Error saving history: {e}")

                # Download report & export history
                col_dl, col_export = st.columns([1,1])
                with col_dl:
                    if st.button("📄 Generate & Download Report"):
                        try:
                            generate_report(username_display,
                                            predicted_stage,
                                            confidence,
                                            predicted_stage,
                                            timestamp,
                                            image_bytes=image_bytes)
                            with open("dfu_report.pdf", "rb") as f:
                                pdf_bytes = f.read()
                            st.download_button(label="⬇️ Download Report (PDF)",
                                               data=pdf_bytes,
                                               file_name="dfu_report.pdf",
                                               mime="application/pdf")
                        except Exception as e:
                            st.error(f"Report generation failed: {e}")

                with col_export:
                    if st.button("📁 Export History (CSV)"):
                        try:
                            rows = c.execute("SELECT email, result, confidence, stage, date FROM history WHERE email=?", (email_display,)).fetchall()
                            if rows:
                                import io, csv
                                csv_buffer = io.StringIO()
                                writer = csv.writer(csv_buffer)
                                writer.writerow(["email", "result", "confidence", "stage", "date"])
                                writer.writerows(rows)
                                st.download_button("⬇️ Download CSV", csv_buffer.getvalue(), "history.csv", "text/csv")
                            else:
                                st.info("No history to export.")
                        except Exception as e:
                            st.error(f"Export error: {e}")
            else:
                st.info("Upload an image to run detection.")
        st.markdown('</div>', unsafe_allow_html=True)

    # History table
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("📜 Your Past Predictions")
    rows = c.execute("SELECT email, result, confidence, stage, date FROM history WHERE email=?", (email_display,)).fetchall()
    if rows:
        rows_sorted = sorted(rows, key=lambda x: x[4], reverse=True)
        st.table(rows_sorted)
    else:
        st.info("No previous predictions found.")
    st.markdown("---")

    # Notes & logout
    st.subheader("💬 Feedback & Notes")
    note = st.text_area("Personal notes about your findings (not saved to DB):", height=120)
    if st.button("Save Note (Session Only)"):
        st.session_state["last_note"] = note
        st.success("Note saved to session (not persisted).")

    if st.button("Logout"):
        st.session_state["user"] = None
        st.success("Logged out successfully.")

else:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("How to use this app")
    st.write("""
    1. Create an account via *Sign Up*.  
    2. Login and upload a thermal foot image.  
    3. View prediction, confidence, and the Grad-CAM heatmap.  
    4. Generate a PDF report and download it.  
    5. Track your prediction history from the dashboard.
    """)
    st.markdown("</div>", unsafe_allow_html=True)
