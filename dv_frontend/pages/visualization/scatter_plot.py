import streamlit as st
import pandas as pd
import numpy as np

from utils.visual_components import export_controls_altair_png

try:
    import altair as alt
except Exception:
    alt = None

st.set_page_config(page_title="Visualization · Scatter Plot", page_icon="🔬", layout="wide")
st.title("🔬 Visualization → Scatter Plot")

# -------------------- Data --------------------
df: pd.DataFrame | None = st.session_state.get("uploaded_df")
if df is None:
    st.warning("⚠️ No dataset found. Please upload one first from the **Upload Dataset** page.")
    st.stop()

# -------------------- Helpers --------------------
def datetime_cols(data: pd.DataFrame) -> list[str]:
    return data.select_dtypes(include=["datetime64[ns]", "datetime64[ns, UTC]"]).columns.tolist()

def numeric_cols(data: pd.DataFrame) -> list[str]:
    return data.select_dtypes(include=[np.number]).columns.tolist()

def categorical_cols(data: pd.DataFrame, max_unique_numeric_as_cat: int = 30) -> list[str]:
    base = data.select_dtypes(include=["object", "category", "bool"]).columns.tolist()
    low_card_num = [c for c in numeric_cols(data) if data[c].nunique(dropna=True) <= max_unique_numeric_as_cat]
    return sorted(list(dict.fromkeys(base + low_card_num)))

def maybe_parse_datetime(s: pd.Series, force_parse: bool) -> pd.Series:
    if pd.api.types.is_datetime64_any_dtype(s):
        return s
    if force_parse:
        return pd.to_datetime(s, errors="coerce")
    return s

# -------------------- Controls (MAIN BODY) --------------------
st.subheader("Controls")

num_candidates = numeric_cols(df)
dt_candidates = datetime_cols(df)
cat_candidates = categorical_cols(df)

c1, c2, c3, c4 = st.columns([2.2, 2.2, 1.8, 1.8])
with c1:
    x_col = st.selectbox("X (numeric or datetime)", df.columns.tolist(), index=0, key="sc_x")
with c2:
    y_col = st.selectbox("Y (numeric)", num_candidates, index=0, key="sc_y")
with c3:
    treat_x_as_time = st.checkbox("Treat X as datetime", value=(x_col in dt_candidates), key="sc_x_time")
with c4:
    sample_n = st.number_input("Sample rows (0 = all)", min_value=0, max_value=len(df), value=min(5000, len(df)), step=500, key="sc_sample")

c5, c6, c7, c8 = st.columns([2.2, 2.2, 2.2, 2.2])
with c5:
    color_mode = st.selectbox("Color", ["None", "By category", "By numeric"], index=0, key="sc_color_mode")
with c6:
    size_mode = st.selectbox("Size", ["Fixed", "By numeric"], index=0, key="sc_size_mode")
with c7:
    facet_col = st.selectbox("Facet by (optional category)", ["<none>"] + cat_candidates, index=0, key="sc_facet")
    facet_col = None if facet_col == "<none>" else facet_col
with c8:
    jitter = st.checkbox("Jitter points", value=False, key="sc_jitter")

r1, r2, r3, r4 = st.columns([2.2, 2.2, 2.2, 2.2])
with r1:
    x_log = st.checkbox("Log X", value=False, key="sc_x_log")
with r2:
    y_log = st.checkbox("Log Y", value=False, key="sc_y_log")
with r3:
    opacity = st.slider("Opacity", 0.05, 1.0, 0.75, 0.05, key="sc_opacity")
with r4:
    point_size = st.number_input("Point size (when fixed)", min_value=1, max_value=2000, value=60, step=5, key="sc_pt_size")

# Trendline
with st.expander("📈 Trendline & Smoothing", expanded=False):
    t1, t2, t3 = st.columns(3)
    with t1:
        trend = st.selectbox("Trendline", ["None", "Linear", "LOESS"], index=0, key="sc_trend")
    with t2:
        trend_per_group = st.checkbox("Compute per color group", value=True, key="sc_trend_group")
    with t3:
        loess_bandwidth = st.slider("LOESS bandwidth", 0.1, 1.0, 0.3, 0.05, key="sc_loess_bw")

# Color appearance
color_scheme_disc = ["tableau10", "category10", "set2", "set3", "paired", "pastel1"]
color_scheme_cont = ["viridis", "plasma", "magma", "inferno", "blues", "greens", "reds"]

with st.expander("🎨 Colors & Legend", expanded=False):
    cA, cB, cC = st.columns(3)
    with cA:
        palette_disc = st.selectbox("Discrete palette", color_scheme_disc, index=0, key="sc_pal_disc")
    with cB:
        palette_cont = st.selectbox("Continuous palette", color_scheme_cont, index=0, key="sc_pal_cont")
    with cC:
        reverse_palette = st.checkbox("Reverse palette", value=False, key="sc_pal_rev")
    legend = st.checkbox("Show legend", value=True, key="sc_legend")

# Size mapping
if size_mode == "By numeric":
    s1, s2 = st.columns(2)
    with s1:
        size_col = st.selectbox("Size column (numeric)", num_candidates, index=0, key="sc_size_col")
    with s2:
        size_range = st.slider("Size range (px)", 10, 2000, (30, 400), step=10, key="sc_size_range")
else:
    size_col = None
    size_range = (point_size, point_size)

# Color mapping
if color_mode == "By category":
    color_cat = st.selectbox("Color column (categorical)", cat_candidates, index=0 if cat_candidates else None, key="sc_color_cat")
    color_num = None
elif color_mode == "By numeric":
    color_num = st.selectbox("Color column (numeric)", num_candidates, index=0 if num_candidates else None, key="sc_color_num")
    color_cat = None
else:
    color_cat = None
    color_num = None

# -------------------- Prepare data --------------------
work_cols = [x_col, y_col] + ([color_cat] if color_cat else []) + ([color_num] if color_num else []) + ([size_col] if size_col else []) + ([facet_col] if facet_col else [])
work = df[work_cols].copy()

# Parse datetime X if asked
work[x_col] = maybe_parse_datetime(work[x_col], treat_x_as_time)

# Drop rows with missing essential fields
essential = [x_col, y_col] + ([size_col] if size_mode == "By numeric" else [])
work = work.dropna(subset=essential)

# Optional jitter (small random noise) — only for numeric axes
if jitter:
    rng = np.random.default_rng(42)
    # Add jitter of ~0.5% of std for numeric columns involved
    if pd.api.types.is_numeric_dtype(work[x_col]):
        jx = float(work[x_col].std(ddof=0) or 0)
        work["_xj"] = work[x_col] + (rng.normal(0, jx * 0.005, size=len(work)) if jx > 0 else 0)
    else:
        work["_xj"] = work[x_col]
    jy = float(work[y_col].std(ddof=0) or 0)
    work["_yj"] = work[y_col] + (rng.normal(0, jy * 0.005, size=len(work)) if jy > 0 else 0)
    x_field = "_xj"
    y_field = "_yj"
else:
    x_field = x_col
    y_field = y_col

# Sampling
if sample_n and sample_n > 0 and len(work) > sample_n:
    work = work.sample(int(sample_n), random_state=1)

# -------------------- Build Altair chart --------------------
if not alt:
    st.info("Altair not installed; cannot render scatter plot.")
    st.stop()

# Encodings
if treat_x_as_time:
    x_enc = alt.X(f"{x_field}:T", title=x_col)
else:
    x_type = "Q" if pd.api.types.is_numeric_dtype(work[x_field]) else "N"
    x_enc = alt.X(f"{x_field}:{x_type}", title=x_col)

y_scale = alt.Scale(type="log") if y_log else alt.Scale()
x_scale = alt.Scale(type="log") if (x_log and not treat_x_as_time) else alt.Scale()

y_enc = alt.Y(f"{y_field}:Q", title=y_col, scale=y_scale)
# If X is numeric and log selected, override scale
if not treat_x_as_time:
    x_enc = x_enc.scale(x_scale)

tooltip = [alt.Tooltip(x_col if x_field == x_col else x_field, title=x_col),
           alt.Tooltip(y_col if y_field == y_col else y_field, title=y_col)]

# Color encoding
color_enc = None
if color_cat:
    color_enc = alt.Color(f"{color_cat}:N",
                          legend=alt.Legend() if legend else None,
                          scale=alt.Scale(scheme=palette_disc, reverse=reverse_palette),
                          title=color_cat)
elif color_num:
    color_enc = alt.Color(f"{color_num}:Q",
                          legend=alt.Legend() if legend else None,
                          scale=alt.Scale(scheme=palette_cont, reverse=reverse_palette),
                          title=color_num)

# Size encoding
if size_mode == "By numeric" and size_col:
    size_enc = alt.Size(f"{size_col}:Q", scale=alt.Scale(range=list(size_range)), title=size_col)
else:
    size_enc = alt.value(point_size)

base = alt.Chart(work)

points = base.mark_circle(opacity=float(opacity)).encode(
    x=x_enc,
    y=y_enc,
    tooltip=tooltip,
    size=size_enc,
    color=color_enc if color_enc is not None else alt.value("#4C78A8"),
)

layers = [points]

# Trendline layer
if trend != "None":
    trend_kwargs = {}
    if trend == "Linear":
        tr = base.transform_regression(x_field, y_field, groupby=[color_cat] if (trend_per_group and color_cat) else None).mark_line(strokeWidth=2)
    else:  # LOESS
        tr = base.transform_loess(x_field, y_field, groupby=[color_cat] if (trend_per_group and color_cat) else None, bandwidth=float(loess_bandwidth)).mark_line(strokeWidth=2)

    tr_enc = {
        "x": x_enc,
        "y": y_enc,
        "color": color_enc if (trend_per_group and color_enc is not None and color_cat) else alt.value("#333333"),
    }
    layers.append(tr.encode(**tr_enc))

chart = alt.layer(*layers)

# Facet (small multiples)
if facet_col:
    chart = chart.facet(column=alt.Column(f"{facet_col}:N", header=alt.Header(title=facet_col, labelOrient="bottom")))

chart = chart.properties(height=420, title="Scatter Plot").interactive()

st.altair_chart(chart, use_container_width=True)

# Data preview (first 500 rows used)
with st.expander("🔎 Data preview"):
    st.dataframe(work.head(500), use_container_width=True)

# Export to PNG
export_controls_altair_png(chart, key_suffix="scatter")
