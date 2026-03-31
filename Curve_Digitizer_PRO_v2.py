
import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from PIL import Image

st.set_page_config(layout="wide")
st.title("🔥 Curve Digitizer PRO - Multi Curve (Head / Eff / Power)")

st.info("Upload image → define axes → click few points per curve → export all data")

uploaded_file = st.file_uploader("Upload Curve Image", type=["png","jpg","jpeg"])

def pixel_to_real(px, py, w, h, xmin, xmax, ymin, ymax):
    Q = xmin + (px / w) * (xmax - xmin)
    Y = ymax - (py / h) * (ymax - ymin)
    return Q, Y

if uploaded_file:
    img = Image.open(uploaded_file)
    width, height = img.size

    st.subheader("⚙️ Axis Calibration")

    col1, col2 = st.columns(2)

    with col1:
        x_min = st.number_input("Flow Min", value=0.0)
        x_max = st.number_input("Flow Max", value=150.0)

    with col2:
        y_min = st.number_input("Y Min", value=0.0)
        y_max = st.number_input("Y Max", value=50.0)

    st.subheader("🖱️ Click Points (Close window after each curve)")

    def get_curve_points(label):
        st.write(f"👉 Click points for: {label}")
        fig, ax = plt.subplots()
        ax.imshow(img)
        ax.set_title(label)
        st.pyplot(fig)

        pts = plt.ginput(25, timeout=0)

        if not pts:
            return None

        px = np.array([p[0] for p in pts])
        py = np.array([p[1] for p in pts])

        Q, Y = pixel_to_real(px, py, width, height, x_min, x_max, y_min, y_max)

        return pd.DataFrame({
            "Flow": np.round(Q,2),
            label: np.round(Y,2)
        })

    # ================= CURVES =================
    head_df = get_curve_points("Head")
    eff_df = get_curve_points("Efficiency")
    power_df = get_curve_points("Power")

    # ================= MERGE =================
    dfs = [df for df in [head_df, eff_df, power_df] if df is not None]

    if dfs:
        final_df = dfs[0]

        for df in dfs[1:]:
            final_df = pd.merge_asof(
                final_df.sort_values("Flow"),
                df.sort_values("Flow"),
                on="Flow",
                direction="nearest"
            )

        st.subheader("📊 Final Extracted Data")
        st.dataframe(final_df, use_container_width=True)

        # Plot all
        fig2, ax2 = plt.subplots()
        if "Head" in final_df:
            ax2.plot(final_df["Flow"], final_df["Head"], label="Head")
        if "Efficiency" in final_df:
            ax2.plot(final_df["Flow"], final_df["Efficiency"], label="Efficiency")
        if "Power" in final_df:
            ax2.plot(final_df["Flow"], final_df["Power"], label="Power")

        ax2.legend()
        ax2.grid()
        ax2.set_xlabel("Flow")
        st.pyplot(fig2)

        csv = final_df.to_csv(index=False)
        st.download_button("📥 Download CSV", csv, "full_curve_data.csv")

else:
    st.warning("Upload image to start")
