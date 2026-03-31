
import streamlit as st
from streamlit_drawable_canvas import st_canvas
from PIL import Image
import numpy as np
import pandas as pd

st.set_page_config(layout="wide")
st.title("🔥 Curve Digitizer PRO (Interactive)")

st.info("Upload image → calibrate axes → click curve points → export real data")

uploaded_file = st.file_uploader("Upload Curve Image", type=["png","jpg","jpeg"])

def pixel_to_real(points, w, h, xmin, xmax, ymin, ymax):
    px = np.array([p[0] for p in points])
    py = np.array([p[1] for p in points])

    Q = xmin + (px / w) * (xmax - xmin)
    Y = ymax - (py / h) * (ymax - ymin)

    return Q, Y

if uploaded_file:
    img = Image.open(uploaded_file)
    width, height = img.size

    st.subheader("⚙️ Axis Calibration")

    col1, col2 = st.columns(2)

    with col1:
        x_min = st.number_input("Flow Min (X min)", value=0.0)
        x_max = st.number_input("Flow Max (X max)", value=150.0)

    with col2:
        y_min = st.number_input("Y Min", value=0.0)
        y_max = st.number_input("Y Max", value=50.0)

    st.subheader("🖱️ Click Points on Curve")

    canvas_result = st_canvas(
        fill_color="red",
        stroke_width=3,
        background_image=img,
        update_streamlit=True,
        height=600,
        width=900,
        drawing_mode="point",
        key="canvas",
    )

    if canvas_result.json_data is not None:
        objects = canvas_result.json_data["objects"]

        if objects:
            points = []
            for obj in objects:
                x = obj["left"]
                y = obj["top"]
                points.append((x, y))

            st.subheader("📍 Pixel Points")
            df_pixels = pd.DataFrame(points, columns=["Pixel_X", "Pixel_Y"])
            st.dataframe(df_pixels, use_container_width=True)

            # Convert to real values
            Q, H = pixel_to_real(points, width, height, x_min, x_max, y_min, y_max)

            df_real = pd.DataFrame({
                "Flow": np.round(Q, 2),
                "Head/Eff/Power": np.round(H, 2)
            })

            st.subheader("📊 Converted Data")
            st.dataframe(df_real, use_container_width=True)

            # Plot
            st.subheader("📈 Curve")
            st.line_chart(df_real.set_index("Flow"))

            # Download CSV
            csv = df_real.to_csv(index=False)
            st.download_button("📥 Download CSV", csv, "curve_data.csv")

else:
    st.warning("Upload an image to start")
