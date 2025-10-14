# utils/visual_components.py
from __future__ import annotations
import streamlit as st
from typing import Optional
from utils.image_export import altair_to_png

def export_controls_altair_png(chart, *, key_suffix: str, default_scale: float = 2.0):
    c1, c2 = st.columns([1, 1])
    with c1:
        scale = st.number_input("Scale", 0.5, 5.0, default_scale, 0.5, key=f"scale_{key_suffix}")
    with c2:
        bg = st.selectbox("Background", ["white", "transparent"], key=f"bg_{key_suffix}")

    w = st.number_input("Width (px)", 0, 4000, 0, 50, key=f"w_{key_suffix}", help="0 = auto")
    h = st.number_input("Height (px)", 0, 4000, 0, 50, key=f"h_{key_suffix}", help="0 = auto")

    if chart is None:
        st.info("No chart to export.")
        return

    try:
        data = altair_to_png(
            chart,
            scale=float(scale),
            width=int(w) if w > 0 else None,
            height=int(h) if h > 0 else None,
            background=None if bg == "transparent" else bg,
        )
        st.download_button(
            "⬇️ Download PNG",
            data=data,
            file_name=f"visual_{key_suffix}.png",
            mime="image/png",
            key=f"dl_png_{key_suffix}",
        )
    except Exception as e:
        st.exception(e)
