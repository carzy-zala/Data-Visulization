import streamlit as st
import pandas as pd
import numpy as np

from utils.visual_components import export_controls_altair_png

try:
    import altair as alt
except Exception:
    alt = None

st.set_page_config(page_title="Visualization · Distribution", page_icon="📈", layout="wide")
st.title("📈 Visualization → Distribution")

# -------------------- Data --------------------
df: pd.DataFrame | None = st.session_state.get("uploaded_df")
if df is None:
    st.warning("⚠️ No dataset found. Please upload one first from the **Upload Dataset** page.")
    st.stop()

# -------------------- Helpers --------------------
CAT_INCLUDE_DTYPES = ["object", "category", "bool"]

def is_categorical(series: pd.Series, low_card_threshold: int) -> bool:
    if str(series.dtype) in CAT_INCLUDE_DTYPES:
        return True
    if pd.api.types.is_numeric_dtype(series):
        return series.nunique(dropna=True) <= low_card_threshold
    if pd.api.types.is_datetime64_any_dtype(series):
        return series.nunique(dropna=True) <= low_card_threshold
    return False

# -------------------- Controls (MAIN BODY) --------------------
st.subheader("Controls")
cc1, cc2, cc3, cc4, cc5 = st.columns([2.2, 2.2, 1.6, 1.8, 2.4])

all_cols = df.columns.tolist()
with cc1:
    target_col = st.selectbox("Column", all_cols, index=0, key="dist_col")

with cc2:
    low_card_threshold = st.slider(
        "Low-cardinality threshold (categorical if ≤)", 5, 100, 30, step=1, key="dist_low_card"
    )

with cc3:
    drop_na = st.checkbox("Exclude nulls", value=True, key="dist_dropna")

with cc4:
    auto_mode = st.checkbox("Automatic chart type", value=True, key="dist_auto")

# Decide chart type
col_s = df[target_col]
treat_as_cat = is_categorical(col_s, low_card_threshold)
default_type = "Bar (categorical)" if treat_as_cat else "Histogram (numeric)"

with cc5:
    chart_type = st.selectbox(
        "Chart type",
        ["Bar (categorical)", "Histogram (numeric)"],
        index=(0 if default_type.startswith("Bar") else 1),
        disabled=auto_mode,
        key="dist_chart_type",
    )
if auto_mode:
    chart_type = default_type

# Optional pre-processing (shown irrespective, applies only to histogram)
with st.expander("⚙️ Advanced preprocessing (numeric only)", expanded=False):
    if chart_type.startswith("Histogram"):
        winsor = st.checkbox("Winsorize (clip) extremes", value=False, help="Clip values by percentile range.", key="dist_winsor")
        p1, p2 = st.columns(2)
        with p1:
            p_low = st.number_input("Lower percentile", 0.0, 49.0, 1.0, step=0.5, key="dist_p_low")
        with p2:
            p_high = st.number_input("Upper percentile", 51.0, 100.0, 99.0, step=0.5, key="dist_p_high")
    else:
        winsor, p_low, p_high = False, 1.0, 99.0

# Prepare working series
x = col_s.copy()
if drop_na:
    x = x.dropna()

if chart_type.startswith("Histogram") and winsor and pd.api.types.is_numeric_dtype(x):
    lo = np.nanpercentile(x.values, p_low)
    hi = np.nanpercentile(x.values, p_high)
    x = x.clip(lower=lo, upper=hi)

# -----------------------------------------------------------------------------
# Categorical: Bar chart of value counts
# -----------------------------------------------------------------------------
if chart_type.startswith("Bar"):
    st.subheader(f"Distribution of **{target_col}** (categorical)")

    # value counts frame
    counts = (
        x.value_counts(dropna=False)
        .rename_axis(target_col)
        .reset_index(name="count")
    )
    total = counts["count"].sum()
    counts["percent"] = (counts["count"] / total * 100).round(2)

    # Sorting / Top-N
    c1, c2, c3 = st.columns(3)
    with c1:
        sort_by = st.selectbox("Sort by", ["count", target_col], index=0, key=f"cat_sort_{target_col}")
    with c2:
        ascending = st.checkbox("Ascending sort", value=False, key=f"cat_asc_{target_col}")
    with c3:
        top_n = st.number_input(
            "Top N",
            min_value=1,
            max_value=max(1, len(counts)),
            value=min(20, len(counts)),
            step=1,
            key=f"cat_top_{target_col}",
        )
    counts = counts.sort_values(sort_by, ascending=ascending).head(int(top_n))

    # Color controls (in expander; chart rendered below)
    color_exp = st.expander("🎨 Appearance · Colors", expanded=False)
    with color_exp:
        color_mode = st.selectbox(
            "Color mode", ["Single", "By category"], index=0, key=f"cat_color_mode_{target_col}"
        )
        if color_mode == "Single":
            single_color = st.color_picker("Bar color", value="#4C78A8", key=f"cat_bar_color_{target_col}")
            palette, reverse_palette, show_legend = None, False, False
        else:
            single_color = None
            discrete_palettes = ["tableau10", "category10", "set2", "set3", "paired", "pastel1", "pastel2"]
            palette = st.selectbox("Palette", discrete_palettes, index=0, key=f"cat_palette_{target_col}")
            reverse_palette = st.checkbox("Reverse palette", value=False, key=f"cat_rev_{target_col}")
            show_legend = st.checkbox("Show legend", value=True, key=f"cat_leg_{target_col}")

    # Build chart OUTSIDE expander
    if alt:
        x_enc = alt.X(f"{target_col}:N", title=target_col, axis=alt.Axis(labelAngle=0))
        y_enc = alt.Y("count:Q", title="Count")
        base = alt.Chart(counts).encode(
            x=x_enc, y=y_enc,
            tooltip=[
                alt.Tooltip(f"{target_col}:N", title=target_col),
                alt.Tooltip("count:Q", title="Count"),
                alt.Tooltip("percent:Q", title="Percent"),
            ]
        )
        if color_mode == "Single":
            bars = base.mark_bar(color=single_color)
        else:
            bars = base.mark_bar().encode(
                color=alt.Color(
                    f"{target_col}:N",
                    legend=alt.Legend() if show_legend else None,
                    scale=alt.Scale(scheme=palette, reverse=reverse_palette),
                )
            )
        title = f"Value counts of {target_col}"
        chart = bars.properties(height=360, title=title).interactive()
        st.altair_chart(chart, use_container_width=True)

        with st.expander("🔎 Data table"):
            st.dataframe(counts, use_container_width=True)

        export_controls_altair_png(chart, key_suffix=f"dist_cat_{target_col}")
    else:
        st.info("Altair not installed; showing basic bar chart.")
        st.bar_chart(counts.set_index(target_col)["count"])

# -----------------------------------------------------------------------------
# Numeric: Histogram (+ density/rug)
# -----------------------------------------------------------------------------
else:
    st.subheader(f"Distribution of **{target_col}** (numeric)")

    # Controls row
    n_unique = x.nunique(dropna=True)
    h1, h2, h3, h4 = st.columns(4)
    with h1:
        default_bins = min(30, max(10, int(np.sqrt(max(n_unique, 1)))))
        bins = st.number_input(
            "Bins", min_value=5, max_value=200, value=default_bins, step=1, help="Number of histogram bins",
            key=f"hist_bins_{target_col}"
        )
    with h2:
        norm = st.selectbox("Normalize", ["count", "density", "percent"], index=0, key=f"hist_norm_{target_col}")
    with h3:
        show_density = st.checkbox("Overlay density (KDE)", value=True, key=f"hist_kde_{target_col}")
    with h4:
        show_rug = st.checkbox("Rug ticks", value=False, key=f"hist_rug_{target_col}")

    # Appearance (expander for controls only)
    color_exp = st.expander("🎨 Appearance · Colors", expanded=False)
    with color_exp:
        bar_color = st.color_picker("Bar color", value="#4C78A8", key=f"hist_bar_color_{target_col}")
        density_color = st.color_picker("Density line color", value="#333333", key=f"hist_density_color_{target_col}")

    # Build chart OUTSIDE expander
    if alt:
        hist_df = pd.DataFrame({target_col: x})
        base = alt.Chart(hist_df)

        # Histogram layer (handle normalization)
        y_title = {"count": "Count", "density": "Density", "percent": "Percent"}[norm]

        if norm == "count":
            hist = (
                base.mark_bar(color=bar_color)
                .encode(
                    x=alt.X(f"{target_col}:Q", bin=alt.Bin(maxbins=int(bins)), title=target_col),
                    y=alt.Y("count()", title=y_title),
                    tooltip=[
                        alt.Tooltip(f"{target_col}:Q", bin=alt.Bin(maxbins=int(bins)), title="Range"),
                        alt.Tooltip("count():Q", title="Count"),
                    ],
                )
            )
        elif norm == "percent":
            hist = (
                base.transform_bin("binned", field=target_col, maxbins=int(bins))
                    .transform_aggregate(count="count()", groupby=["binned"])
                    .transform_joinaggregate(total="sum(count)")
                    .transform_calculate(percent="100 * datum.count / datum.total")
                    .mark_bar(color=bar_color)
                    .encode(
                        x=alt.X("binned:Q", bin=alt.Bin(maxbins=int(bins)), title=target_col),
                        y=alt.Y("percent:Q", title=y_title),
                    )
            )
        else:  # density (keep bar counts for shape; density line overlays)
            hist = (
                base.mark_bar(color=bar_color)
                .encode(
                    x=alt.X(f"{target_col}:Q", bin=alt.Bin(maxbins=int(bins)), title=target_col),
                    y=alt.Y("count()", title=y_title),
                )
            )

        layers = [hist]

        if show_density:
            dens = (
                base.transform_density(target_col, as_=[target_col, 'density'])
                    .mark_line(stroke=density_color, strokeWidth=2)
                    .encode(
                        x=f"{target_col}:Q",
                        y="density:Q",
                        tooltip=[alt.Tooltip("density:Q", title="Density")]
                    )
            )
            layers.append(dens)

        if show_rug:
            rug = base.mark_tick(opacity=0.35, thickness=1).encode(x=f"{target_col}:Q", y=alt.value(0))
            layers.append(rug)

        chart = alt.layer(*layers).properties(height=360, title=f"Histogram of {target_col}").interactive()
        st.altair_chart(chart, use_container_width=True)

        with st.expander("🧮 Summary stats"):
            desc = x.describe(percentiles=[0.01, 0.05, 0.25, 0.5, 0.75, 0.95, 0.99]).to_frame("value")
            st.dataframe(desc, use_container_width=True)

        export_controls_altair_png(chart, key_suffix=f"dist_num_{target_col}")

    else:
        st.info("Altair not installed; cannot render histogram.")
