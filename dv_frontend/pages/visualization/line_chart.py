import streamlit as st
import pandas as pd
import numpy as np

from utils.visual_components import export_controls_altair_png

try:
    import altair as alt
except Exception:
    alt = None

st.set_page_config(page_title="Visualization · Line Chart", page_icon="📈", layout="wide")
st.title("📈 Visualization → Line Chart")

# -------------------- Data --------------------
df: pd.DataFrame | None = st.session_state.get("uploaded_df")
if df is None:
    st.warning("⚠️ No dataset found. Please upload one first from the **Upload Dataset** page.")
    st.stop()

# -------------------- Helpers --------------------
def datetime_cols(data: pd.DataFrame) -> list[str]:
    dt = data.select_dtypes(include=["datetime64[ns]", "datetime64[ns, UTC]"]).columns.tolist()
    # also suggest object columns that *look* like datetimes (heuristic: try few rows)
    for c in data.select_dtypes(include=["object"]).columns:
        s = data[c].dropna().astype(str)
        if s.empty:
            continue
        try:
            pd.to_datetime(s.sample(min(20, len(s))), errors="raise")  # try small sample
            if c not in dt:
                dt.append(c)
        except Exception:
            pass
    return dt

def numeric_cols(data: pd.DataFrame) -> list[str]:
    return data.select_dtypes(include=[np.number]).columns.tolist()

def categorical_cols(data: pd.DataFrame, max_unique_numeric_as_cat: int = 30) -> list[str]:
    base = data.select_dtypes(include=["object", "category", "bool"]).columns.tolist()
    low_card_num = [c for c in numeric_cols(data) if data[c].nunique(dropna=True) <= max_unique_numeric_as_cat]
    return sorted(list(dict.fromkeys(base + low_card_num)))

def maybe_to_datetime(series: pd.Series, do_parse: bool) -> pd.Series:
    if pd.api.types.is_datetime64_any_dtype(series):
        return series
    if do_parse:
        return pd.to_datetime(series, errors="coerce")
    return series

# -------------------- Controls (MAIN BODY) --------------------
st.subheader("Controls")
c1, c2, c3 = st.columns([2.2, 2.2, 2.2])
c4, c5, c6 = st.columns([2.2, 2.2, 2.2])

dt_candidates = datetime_cols(df)
num_candidates = numeric_cols(df)
cat_candidates = categorical_cols(df)

with c1:
    x_col = st.selectbox("X axis (time or numeric/category)", df.columns.tolist(), index=0, key="line_x")

with c2:
    y_cols = st.multiselect("Y columns (numeric)", num_candidates, default=num_candidates[:1], key="line_ys")

with c3:
    group_col = st.selectbox("Group by (optional, categorical)", ["<none>"] + cat_candidates, index=0, key="line_group")
    group_col = None if group_col == "<none>" else group_col

with c4:
    is_time = st.checkbox("Treat X as datetime", value=(x_col in dt_candidates), key="line_is_time")

with c5:
    if is_time:
        freq = st.selectbox("Resample frequency", ["Auto (no resample)", "D", "W", "M", "Q", "Y"], index=0, key="line_freq",
                            help="D=Day, W=Week, M=Month, Q=Quarter, Y=Year")
    else:
        freq = "Auto (no resample)"

with c6:
    agg = st.selectbox("Aggregation", ["sum", "mean", "median", "min", "max"], index=0, key="line_agg")

r1, r2, r3, r4 = st.columns([2.2, 2.2, 2.2, 2.2])
with r1:
    missing = st.selectbox("Missing values", ["drop", "ffill", "interpolate"], index=1, key="line_missing")
with r2:
    rolling = st.number_input("Rolling window (0=off)", min_value=0, max_value=365, value=0, step=1, key="line_roll")
with r3:
    normalize = st.checkbox("Normalize each series to 100 (index)", value=False, key="line_norm")
with r4:
    topn_groups = st.number_input("Top N groups (if grouped)", min_value=1, max_value=100, value=10, step=1, key="line_topn")

# Appearance controls
with st.expander("🎨 Appearance · Style", expanded=False):
    a1, a2, a3, a4 = st.columns(4)
    with a1:
        orientation = st.selectbox("Orientation", ["Vertical (time on X)", "Horizontal (swap axes)"], index=0, key="line_orient")
    with a2:
        show_markers = st.checkbox("Show markers", value=False, key="line_markers")
    with a3:
        area_fill = st.checkbox("Fill area under line", value=False, key="line_area")
    with a4:
        log_scale = st.checkbox("Log scale (Y)", value=False, key="line_log")

    # color / legend
    a5, a6, a7 = st.columns(3)
    with a5:
        palette = st.selectbox("Palette (scheme)", ["tableau10", "category10", "set2", "set3", "paired", "viridis", "plasma"], index=0, key="line_palette")
    with a6:
        reverse_palette = st.checkbox("Reverse palette", value=False, key="line_palette_rev")
    with a7:
        show_legend = st.checkbox("Show legend", value=True, key="line_legend")

# -------------------- Prepare data --------------------
if not y_cols:
    st.info("Select at least one numeric Y column.")
    st.stop()

work = df[[x_col] + y_cols + ([group_col] if group_col else [])].copy()

# Parse/convert X
work[x_col] = maybe_to_datetime(work[x_col], do_parse=is_time)

# Handle missing X or Y rows
if missing == "drop":
    work = work.dropna(subset=[x_col] + y_cols)
else:
    # keep rows; we'll fill later after sorting/grouping
    pass

# For grouped lines, keep top-N groups by aggregate on first Y column
if group_col:
    totals = work.groupby(group_col, dropna=False)[y_cols[0]].sum(numeric_only=True)
    keep = totals.sort_values(ascending=False).head(int(topn_groups)).index
    work = work[work[group_col].isin(keep)]

# Resample if datetime + freq selected
def resample_if_needed(d: pd.DataFrame) -> pd.DataFrame:
    if not is_time or freq == "Auto (no resample)":
        return d
    # ensure time index
    d = d.sort_values(x_col)
    gcols = [group_col] if group_col else []
    out = []
    if gcols:
        for key, sub in d.groupby(gcols, dropna=False):
            sub = sub.set_index(x_col)
            r = sub.resample(freq)[y_cols].agg(agg)
            r[gcols] = key if isinstance(key, tuple) else key
            out.append(r.reset_index())
        d = pd.concat(out, ignore_index=True)
    else:
        d = d.set_index(x_col).resample(freq)[y_cols].agg(agg).reset_index()
    return d

work = resample_if_needed(work)

# Fill/interpolate after resample/sort
if missing in ("ffill", "interpolate"):
    work = work.sort_values([c for c in ([group_col] if group_col else [])] + [x_col])
    if missing == "ffill":
        work[y_cols] = work.groupby(group_col)[y_cols].ffill() if group_col else work[y_cols].ffill()
    elif missing == "interpolate":
        # time-aware interpolation if datetime
        if is_time:
            if group_col:
                work[y_cols] = work.groupby(group_col)[y_cols].apply(lambda g: g.set_index(work.loc[g.index, x_col]).interpolate(method="time").reset_index(drop=True))
            else:
                work = work.set_index(x_col)
                work[y_cols] = work[y_cols].interpolate(method="time")
                work = work.reset_index()
        else:
            work[y_cols] = work.groupby(group_col)[y_cols].interpolate() if group_col else work[y_cols].interpolate()

# Rolling smoothing
if rolling and rolling > 0:
    if group_col:
        work[y_cols] = work.groupby(group_col, group_keys=False)[y_cols].apply(lambda s: s.rolling(int(rolling), min_periods=1).mean())
    else:
        work[y_cols] = work[y_cols].rolling(int(rolling), min_periods=1).mean()

# Normalize to 100 per series (use first non-null per series)
if normalize:
    if group_col:
        for g in work[group_col].dropna().unique():
            mask = work[group_col] == g
            for y in y_cols:
                first = work.loc[mask & work[y].notna(), y].iloc[:1]
                if not first.empty and first.values[0] != 0:
                    work.loc[mask, y] = work.loc[mask, y] / first.values[0] * 100.0
    else:
        for y in y_cols:
            first = work.loc[work[y].notna(), y].iloc[:1]
            if not first.empty and first.values[0] != 0:
                work[y] = work[y] / first.values[0] * 100.0

# -------------------- Build Altair chart --------------------
if alt:
    # Melt to long form: columns -> series per Y (and optionally group)
    id_vars = [x_col] + ([group_col] if group_col else [])
    long = work.melt(id_vars=id_vars, value_vars=y_cols, var_name="series", value_name="value")

    # Combine group + series if grouping to color lines distinctly
    if group_col:
        long["series_label"] = long[group_col].astype(str) + " · " + long["series"].astype(str)
    else:
        long["series_label"] = long["series"].astype(str)

    # Encodings
    if is_time:
        x_enc = alt.X(f"{x_col}:T", title=x_col)
    else:
        # numeric or category
        x_type = "Q" if pd.api.types.is_numeric_dtype(df[x_col]) else "N"
        x_enc = alt.X(f"{x_col}:{x_type}", title=x_col, sort=None)

    y_scale = alt.Scale(type="log") if log_scale else alt.Scale()
    y_enc = alt.Y("value:Q", title=", ".join(y_cols) if len(y_cols) > 1 else y_cols[0], scale=y_scale)

    color = alt.Color(
        "series_label:N",
        legend=alt.Legend() if show_legend else None,
        scale=alt.Scale(scheme=palette, reverse=reverse_palette),
        title="Series"
    )

    base = alt.Chart(long)

    mark_kwargs = {}
    if show_markers:
        mark_kwargs["point"] = True

    line = base.mark_line(**mark_kwargs)
    if area_fill:
        area = base.mark_area(opacity=0.2)
        chart = (area.encode(x=x_enc, y=y_enc, color=color) + line.encode(x=x_enc, y=y_enc, color=color))
    else:
        chart = line.encode(x=x_enc, y=y_enc, color=color)

    # Orientation swap (horizontal)
    if orientation.startswith("Horizontal"):
        chart = chart.encode(x=y_enc, y=x_enc)

    chart = chart.properties(height=420, title="Line Chart").interactive()

    st.altair_chart(chart, use_container_width=True)

    # Data preview
    with st.expander("🔎 Data (long-form used for plotting)"):
        st.dataframe(long.head(500), use_container_width=True)

    # Export PNG
    export_controls_altair_png(chart, key_suffix="line")

else:
    st.info("Altair not installed; cannot render line chart.")
