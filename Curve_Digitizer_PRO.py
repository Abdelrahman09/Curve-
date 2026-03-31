
import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from PIL import Image

st.set_page_config(layout="wide")

st.title("📊 Curve Digitizer PRO")

st.info("Upload curve image → define axes → click points → export CSV")

# Upload image
uploaded_file = st.file_uploader("Upload Curve Image", type=["png","jpg","jpeg"])

if uploaded_file:
    img = Image.open(uploaded_file)

    st.subheader("⚙️ Step 1: Define Axis Limits")

    col1, col2 = st.columns(2)

    with col1:
        x_min = st.number_input("Flow min (X min)", value=0.0)
        x_max = st.number_input("Flow max (X max)", value=150.0)

    with col2:
        y_min = st.number_input("Head min (Y min)", value=0.0)
        y_max = st.number_input("Head max (Y max)", value=50.0)

    st.subheader("🖱️ Step 2: Click on Curve Points")

    st.write("⚠️ Click multiple points on the curve, then close the plot window")

    fig, ax = plt.subplots()
    ax.imshow(img)
    ax.set_title("Click points on curve → Close window when done")

    # Show plot
    st.pyplot(fig)

    # Capture clicks
    points = plt.ginput(30, timeout=0)

    if points:
        px = np.array([p[0] for p in points])
        py = np.array([p[1] for p in points])

        width, height = img.size

        # Convert pixel → real values
        Q = x_min + (px / width) * (x_max - x_min)
        H = y_max - (py / height) * (y_max - y_min)

        df = pd.DataFrame({
            "Flow (L/s or chosen)": np.round(Q,2),
            "Head (m or chosen)": np.round(H,2)
        })

        st.subheader("📊 Extracted Data")
        st.dataframe(df, use_container_width=True)

        # Plot extracted curve
        fig2, ax2 = plt.subplots()
        ax2.scatter(Q, H)
        ax2.set_xlabel("Flow")
        ax2.set_ylabel("Head")
        ax2.set_title("Digitized Curve")
        ax2.grid()
        st.pyplot(fig2)

        # Download
        csv = df.to_csv(index=False)
        st.download_button("📥 Download CSV", csv, "curve_points.csv")

else:
    st.warning("Please upload an image to start")
