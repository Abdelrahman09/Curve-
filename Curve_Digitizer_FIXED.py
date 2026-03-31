import streamlit as st
from streamlit_drawable_canvas import st_canvas
from PIL import Image
import numpy as np
import pandas as pd
from io import BytesIO

st.set_page_config(layout="wide")
st.title("🔥 Curve Digitizer PRO (Cloud Fixed)")

st.info("Upload image → set axis → click points → get real data")

uploaded_file = st.file_uploader("Upload Curve Image", type=["png","jpg","jpeg"])

# ================= FUNCTION =================
def pixel_to_real(points, w, h, xmin, xmax, ymin, ymax):
    px = np.array([p[0] for p in points])
    py = np.array([p[1] for p in points])

    Q = xmin + (px / w) * (xmax - xmin)
    Y = ymax - (py / h) * (ymax - ymin)

    return Q, Y

# ================= MAIN =================
if uploaded_file:

    # 🔥 FIX: convert image to BytesIO
    img = Image.open(uploaded_file).convert("RGB")

    buf = BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)

    width, height = img.size

    # ===== Axis =====
    st.subheader("⚙️ Axis Calibration")

    col1, col2 = st.columns(2)

    with col1:
        x_min = st.number_input("Flow Min", value=0.0)
        x_max = st.number_input("Flow Max", value=150.0)

    with col2:
        y_min = st.number_input("Y Min", value=0.0)
        y_max = st.number_input("Y Max", value=50.0)

    # ===== Canvas =====
    st.subheader("🖱️ Click on Curve Points")

    canvas_result = st_canvas(
        fill_color="red",
        stroke_width=3,
        background_image=buf,   # ✅ الحل النهائي
        update_streamlit=True,
        height=600,
        width=900,
        drawing_mode="point",
        key="canvas",
    )

    # ===== Data Extraction =====
    if canvas_result.json_data is not None:

        objects = canvas_result.json_data["objects"]

        if objects:
            points = []
            for obj in objects:
                x = obj["left"]
                y = obj["top"]
                points.append((x, y))

            # Convert to real values
            Q, H = pixel_to_real(points, width, height, x_min, x_max, y_min, y_max)

            df = pd.DataFrame({
                "Flow": np.round(Q, 2),
                "Value": np.round(H, 2)
            })

            st.subheader("📊 Extracted Data")
            st.dataframe(df, use_container_width=True)

            # Plot
            st.subheader("📈 Curve")
            st.line_chart(df.set_index("Flow"))

            # Download
            csv = df.to_csv(index=False)
            st.download_button("📥 Download CSV", csv, "curve_data.csv")

else:
    st.warning("Upload an image to start")
