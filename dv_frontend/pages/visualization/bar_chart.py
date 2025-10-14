# pages/visualization/bar_chart.py
import streamlit as st
import pandas as pd
import numpy as np

# Reusable PNG export UI (PNG-only)
from utils.visual_components import export_controls_altair_png

try:
    import altair as alt
except Exception:
    alt = None

st.set_page_config(page_title="Visualization · Bar Chart", page_icon="📊", layout="wide")
st.title("📊 Visualization → Bar Chart")

# -------------------- Data --------------------
df: pd.DataFrame | None = st.session_state.get("uploaded_df")
if df is None:
    st.warning("⚠️ No dataset found. Please upload one first from the **Upload Dataset** page.")
    st.stop()

# -------------------- Helpers --------------------
def selectable_categorical_columns(data: pd.DataFrame, max_unique_numeric_as_cat: int = 30) -> list[str]:
    cat_cols = data.select_dtypes(include=["object", "category", "bool"]).columns.tolist()
    low_card_numeric = [c for c in data.select_dtypes(include=[np.number]).columns
                        if data[c].nunique(dropna=True) <= max_unique_numeric_as_cat]
    dt_cols = data.select_dtypes(include=["datetime64[ns]", "datetime64[ns, UTC]"]).columns.tolist()
    low_card_dt = [c for c in dt_cols if data[c].nunique(dropna=True) <= max_unique_numeric_as_cat]
    return sorted(list(dict.fromkeys(cat_cols + low_card_numeric + low_card_dt)))

def selectable_numeric_columns(data: pd.DataFrame) -> list[str]:
    return data.select_dtypes(include=[np.number]).columns.tolist()

def aggregate_for_bar(data: pd.DataFrame, x_col: str, y_col: str | None, agg: str, remove_nulls: bool) -> pd.DataFrame:
    if agg == "count":
        d = data[[x_col]].copy()
        if remove_nulls:
            d = d.dropna(subset=[x_col])
        g = d.groupby(x_col, dropna=False).size().reset_index(name="value")
    elif agg == "nunique(y)":
        assert y_col is not None
        d = data[[x_col, y_col]].copy()
        if remove_nulls:
            d = d.dropna(subset=[x_col, y_col])
        g = d.groupby(x_col, dropna=False).agg(value=(y_col, lambda s: s.nunique(dropna=True))).reset_index()
    else:
        assert y_col is not None
        d = data[[x_col, y_col]].copy()
        if remove_nulls:
            d = d.dropna(subset=[x_col, y_col])
        g = d.groupby(x_col, dropna=False)[y_col].agg(agg).reset_index(name="value")
    return g

# NEW: color-aware bar builder
def build_altair_bar(
    grouped: pd.DataFrame,
    x_col: str,
    y_label: str,
    title: str,
    orientation: str,
    show_labels: bool,
    x_label_angle: int,
    log_scale: bool,
    # --- color controls ---
    color_mode: str,            # "Single", "By X category", "By value"
    single_color: str | None,   # hex string like "#4C78A8"
    palette: str | None,        # e.g., "tableau10", "viridis"
    reverse_palette: bool,
    show_legend: bool,
):
    # orientation encodings
    if orientation == "Vertical":
        x_enc = alt.X(f"{x_col}:N", title=x_col, axis=alt.Axis(labelAngle=x_label_angle))
        y_enc = alt.Y("value:Q", title=y_label, scale=alt.Scale(type="log") if log_scale else alt.Scale())
    else:
        x_enc = alt.X("value:Q", title=y_label, scale=alt.Scale(type="log") if log_scale else alt.Scale())
        y_enc = alt.Y(f"{x_col}:N", title=x_col)

    # base encodings
    base = alt.Chart(grouped).encode(
        x=x_enc,
        y=y_enc,
        tooltip=[alt.Tooltip(f"{x_col}:N", title=x_col), alt.Tooltip("value:Q", title=y_label)],
    )

    # color encodings
    color_kw = {}
    if color_mode == "Single":
        # apply a single bar color via mark_bar(color=...)
        bars = base.mark_bar(color=single_color or "#4C78A8")
    elif color_mode == "By X category":
        # color by the category on x-axis (nominal)
        c = alt.Color(
            f"{x_col}:N",
            legend=alt.Legend() if show_legend else None,
            scale=alt.Scale(scheme=palette or "tableau10", reverse=reverse_palette),
        )
        bars = base.mark_bar().encode(color=c)
    else:  # "By value"
        c = alt.Color(
            "value:Q",
            legend=alt.Legend() if show_legend else None,
            scale=alt.Scale(scheme=palette or "viridis", reverse=reverse_palette),
        )
        bars = base.mark_bar().encode(color=c)

    chart = bars

    if show_labels:
        if orientation == "Vertical":
            text = base.mark_text(dy=-6).encode(text="value:Q")
        else:
            text = base.mark_text(dx=6, align="left").encode(text="value:Q")
        # Keep text uncolored for readability
        chart = bars + text

    chart = chart.properties(height=360, title=title).interactive()
    st.altair_chart(chart, use_container_width=True)
    return chart

def default_config(cat_cols: list[str], num_cols: list[str]) -> dict:
    return {
        "x_col": cat_cols[0] if cat_cols else None,
        "y_col": num_cols[0] if num_cols else None,
        "agg": "sum",
        "sort_by": "value",
        "ascending": False,
        "top_n": 20,
        "remove_nulls": True,
        "title": "",
        "x_label": "",
        "y_label": "",
        "orientation": "Vertical",   # or "Horizontal"
        "show_labels": False,
        "x_label_angle": 0,
        "log_scale": False,
        # --- new color controls defaults ---
        "color_mode": "Single",         # "Single", "By X category", "By value"
        "single_color": "#4C78A8",      # matches Altair default blue
        "palette": "tableau10",         # discrete default
        "reverse_palette": False,
        "show_legend": True,
    }

# -------------------- Session State for chart configs --------------------
cat_cols = selectable_categorical_columns(df)
num_cols = selectable_numeric_columns(df)

if "bar_chart_configs" not in st.session_state or not st.session_state["bar_chart_configs"]:
    st.session_state["bar_chart_configs"] = [default_config(cat_cols, num_cols)]

configs: list[dict] = st.session_state["bar_chart_configs"]
max_charts = 10

# -------------------- Toolbar --------------------
t1, t2, t3 = st.columns([1,1,4])
with t1:
    if st.button("➕ Add chart", disabled=len(configs) >= max_charts):
        if len(configs) < max_charts:
            configs.append(default_config(cat_cols, num_cols))
            st.rerun()
with t2:
    if st.button("🗑️ Remove all", type="secondary"):
        st.session_state["bar_chart_configs"] = []
        st.rerun()

st.caption("Tip: You can duplicate any chart with its full configuration via **Copy visual**.")

# -------------------- Render grid (2 per row) --------------------
if not configs:
    st.info("No charts configured. Click **Add chart** to start.")
else:
    rows_needed = int(np.ceil(len(configs) / 2))
    idx = 0
    for _ in range(rows_needed):
        cL, cR = st.columns(2)
        for col in (cL, cR):
            if idx >= len(configs):
                break
            cfg = configs[idx]

            with col:
                st.subheader(f"Chart {idx+1}")

                # --- Controls (two columns) ---
                cc1, cc2 = st.columns(2)
                with cc1:
                    cfg["x_col"] = st.selectbox(
                        "X (categorical)", cat_cols,
                        index=(cat_cols.index(cfg["x_col"]) if cfg["x_col"] in cat_cols else 0),
                        key=f"x_{idx}", help="Categorical / low-cardinality column for grouping."
                    )
                    # y_col optional only when agg == count
                    y_opts = ["<none> (for count)"] + num_cols
                    selected_y = cfg["y_col"] if cfg["y_col"] in num_cols else "<none> (for count)"
                    y_sel = st.selectbox(
                        "Y (numeric)", y_opts,
                        index=(y_opts.index(selected_y) if selected_y in y_opts else 0),
                        key=f"y_{idx}", help="Numeric column to aggregate; choose <none> for count."
                    )
                    cfg["y_col"] = None if y_sel.startswith("<none>") else y_sel

                    cfg["agg"] = st.selectbox(
                        "Aggregation", ["sum", "mean", "median", "min", "max", "count", "nunique(y)"],
                        index=(["sum", "mean", "median", "min", "max", "count", "nunique(y)"].index(cfg["agg"])
                               if cfg["agg"] in ["sum","mean","median","min","max","count","nunique(y)"] else 0),
                        key=f"agg_{idx}"
                    )

                    cfg["top_n"] = st.number_input("Top N", min_value=1, max_value=200,
                                                   value=int(cfg["top_n"]), step=1, key=f"topn_{idx}")
                    cfg["remove_nulls"] = st.checkbox("Remove nulls in X/Y", value=bool(cfg["remove_nulls"]),
                                                      key=f"nulls_{idx}")

                with cc2:
                    cfg["sort_by"] = st.selectbox("Sort by", ["value", "x"],
                                                  index=(0 if cfg["sort_by"]=="value" else 1), key=f"sort_{idx}")
                    cfg["ascending"] = st.checkbox("Ascending sort", value=bool(cfg["ascending"]), key=f"asc_{idx}")
                    cfg["orientation"] = st.selectbox("Orientation", ["Vertical", "Horizontal"],
                                                      index=(0 if cfg["orientation"]=="Vertical" else 1), key=f"ori_{idx}")
                    cfg["show_labels"] = st.checkbox("Show data labels", value=bool(cfg["show_labels"]),
                                                     key=f"labels_{idx}")
                    cfg["x_label_angle"] = st.slider("X label angle", 0, 90, int(cfg["x_label_angle"]),
                                                     step=5, key=f"angle_{idx}")
                    cfg["log_scale"] = st.checkbox("Log scale (value)", value=bool(cfg["log_scale"]), key=f"log_{idx}")

                # --- Title & Axis labels ---
                cfg["title"] = st.text_input("Chart title (optional)", value=cfg["title"], key=f"title_{idx}")
                cfg["x_label"] = st.text_input("X-axis label (optional)", value=cfg["x_label"], key=f"xlab_{idx}")
                cfg["y_label"] = st.text_input("Y-axis label (optional)", value=cfg["y_label"], key=f"ylab_{idx}")

                # --- Color controls (dynamic) ---
                with st.expander("🎨 Appearance · Colors", expanded=False):
                    cfg["color_mode"] = st.selectbox(
                        "Color mode",
                        ["Single", "By X category", "By value"],
                        index=(["Single","By X category","By value"].index(cfg["color_mode"])
                               if cfg.get("color_mode") in ["Single","By X category","By value"] else 0),
                        key=f"c_mode_{idx}",
                        help="Single = one color; By X category = separate color per category; By value = gradient by aggregated value."
                    )

                    # sensible palette shortlist
                    discrete_palettes = ["tableau10", "category10", "set2", "set3", "paired", "pastel1", "pastel2"]
                    continuous_palettes = ["viridis", "plasma", "magma", "inferno", "blues", "greens", "reds", "purples"]
                    if cfg["color_mode"] == "Single":
                        cfg["single_color"] = st.color_picker("Bar color", value=cfg.get("single_color", "#4C78A8"),
                                                              key=f"c_single_{idx}")
                        cfg["show_legend"] = False
                    elif cfg["color_mode"] == "By X category":
                        cfg["palette"] = st.selectbox("Palette (discrete)", discrete_palettes,
                                                      index=(discrete_palettes.index(cfg.get("palette","tableau10"))
                                                             if cfg.get("palette") in discrete_palettes else 0),
                                                      key=f"c_pal_disc_{idx}")
                        cfg["reverse_palette"] = st.checkbox("Reverse palette", value=bool(cfg.get("reverse_palette", False)),
                                                             key=f"c_rev_{idx}")
                        cfg["show_legend"] = st.checkbox("Show legend", value=bool(cfg.get("show_legend", True)),
                                                         key=f"c_leg_{idx}")
                    else:  # By value
                        cfg["palette"] = st.selectbox("Palette (continuous)", continuous_palettes,
                                                      index=(continuous_palettes.index(cfg.get("palette","viridis"))
                                                             if cfg.get("palette") in continuous_palettes else 0),
                                                      key=f"c_pal_cont_{idx}")
                        cfg["reverse_palette"] = st.checkbox("Reverse palette", value=bool(cfg.get("reverse_palette", False)),
                                                             key=f"c_rev_{idx}")
                        cfg["show_legend"] = st.checkbox("Show legend", value=bool(cfg.get("show_legend", True)),
                                                         key=f"c_leg_{idx}")

                # --- Aggregate & sort ---
                if cfg["agg"] == "count":
                    grouped = aggregate_for_bar(df, cfg["x_col"], None, cfg["agg"], cfg["remove_nulls"])
                    y_label_default = "count"
                elif cfg["agg"] == "nunique(y)":
                    if cfg["y_col"] is None:
                        st.error("Select a Y column for nunique(y).")
                        grouped = None
                    else:
                        grouped = aggregate_for_bar(df, cfg["x_col"], cfg["y_col"], cfg["agg"], cfg["remove_nulls"])
                        y_label_default = "nunique"
                else:
                    if cfg["y_col"] is None:
                        st.error("Select a Y column for this aggregation.")
                        grouped = None
                    else:
                        grouped = aggregate_for_bar(df, cfg["x_col"], cfg["y_col"], cfg["agg"], cfg["remove_nulls"])
                        y_label_default = f"{cfg['agg']}({cfg['y_col']})"

                if grouped is not None:
                    # sort and top-N
                    if cfg["sort_by"] == "value":
                        grouped = grouped.sort_values("value", ascending=bool(cfg["ascending"]))
                    else:
                        grouped = grouped.sort_values(cfg["x_col"], ascending=bool(cfg["ascending"]),
                                                      key=lambda s: s.astype(str))
                    grouped = grouped.head(int(cfg["top_n"]))

                    # resolve labels
                    title = cfg["title"] or f"{y_label_default} by {cfg['x_col']} (Top {cfg['top_n']})"
                    x_axis_label = cfg["x_label"] or cfg["x_col"]
                    y_axis_label = cfg["y_label"] or y_label_default

                    # render
                    if alt:
                        chart = build_altair_bar(
                            grouped,
                            x_col=cfg["x_col"],
                            y_label=y_axis_label,
                            title=title,
                            orientation=cfg["orientation"],
                            show_labels=cfg["show_labels"],
                            x_label_angle=int(cfg["x_label_angle"]),
                            log_scale=bool(cfg["log_scale"]),
                            # color params
                            color_mode=cfg["color_mode"],
                            single_color=cfg.get("single_color"),
                            palette=cfg.get("palette"),
                            reverse_palette=bool(cfg.get("reverse_palette", False)),
                            show_legend=bool(cfg.get("show_legend", True)),
                        )
                    else:
                        st.info("Altair not installed; showing basic bar chart.")
                        st.caption(title)
                        chart = None
                        if cfg["orientation"] == "Vertical":
                            st.bar_chart(grouped.set_index(cfg["x_col"])["value"])
                        else:
                            st.bar_chart(grouped.set_index(cfg["x_col"])["value"])  # Streamlit native lacks horizontal

                    # --- Actions: data & spec export ---
                    a1, a2, a3 = st.columns(3)
                    with a1:
                        csv = grouped.to_csv(index=False).encode("utf-8")
                        st.download_button("⬇️ Download CSV", csv,
                                           file_name=f"bar_chart_{idx+1}.csv",
                                           mime="text/csv", key=f"csv_{idx}")
                    with a2:
                        if alt and chart is not None:
                            spec = chart.to_json()
                            st.download_button("⬇️ Vega-Lite JSON", spec,
                                               file_name=f"bar_chart_{idx+1}.json",
                                               mime="application/json", key=f"json_{idx}")
                        else:
                            st.caption("Install Altair for JSON export.")
                    with a3:
                        if st.button("📋 Copy visual", key=f"copy_{idx}"):
                            if len(configs) < max_charts:
                                new_cfg = {k: (v.copy() if isinstance(v, dict) else v) for k, v in cfg.items()}
                                configs.insert(idx + 1, new_cfg)
                                st.rerun()
                            else:
                                st.warning(f"Maximum of {max_charts} charts reached.", icon="⚠️")

                    # --- Image Export (PNG-only via reusable component) ---
                    if alt and chart is not None:
                        export_controls_altair_png(chart, key_suffix=str(idx))
                    else:
                        st.caption("Install Altair to enable image export.")

                # remove button
                if st.button("🗑️ Remove this chart", key=f"del_{idx}"):
                    del configs[idx]
                    st.rerun()

            idx += 1

# Persist updates
st.session_state["bar_chart_configs"] = configs
