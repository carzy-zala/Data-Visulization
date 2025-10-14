import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="View Dataset", page_icon="📊", layout="wide")
st.title("📊 View Uploaded Dataset")

# Expecting df saved earlier as st.session_state["uploaded_df"]
df: pd.DataFrame | None = st.session_state.get("uploaded_df")

if df is None:
    st.warning("⚠️ No dataset found. Please upload one first from the **Upload Dataset** page.")
    st.stop()

# ---------- Quick stats ----------
st.success("✅ Data loaded from session.")
n_rows, n_cols = df.shape
mem_bytes = df.memory_usage(deep=True).sum()
mem_mb = mem_bytes / (1024 ** 2)

st.subheader("Quick Stats")
c1, c2, c3, c4 = st.columns(4)
c1.metric("Rows", f"{n_rows:,}")
c2.metric("Columns", f"{n_cols:,}")
c3.metric("Memory", f"{mem_mb:,.2f} MB")
c4.metric("Duplicated Rows", f"{df.duplicated().sum():,}")

# ---------- Full dataframe (optionally limited for performance) ----------
with st.expander("🔎 View DataFrame", expanded=False):
    max_rows = st.slider("Max rows to render", 50, min(2000, max(2000, n_rows)), 500, step=50)
    st.dataframe(df.head(max_rows), use_container_width=True)

# ---------- Head / Tail ----------
st.subheader("Preview")
tab_head, tab_tail = st.tabs(["Head (10)", "Tail (10)"])
with tab_head:
    st.dataframe(df.head(10), use_container_width=True)
with tab_tail:
    st.dataframe(df.tail(10), use_container_width=True)

# ---------- Column names & dtypes ----------
st.subheader("Columns by Type")
dtype_map = {
    "Numeric": df.select_dtypes(include=[np.number]).columns.tolist(),
    "Categorical": df.select_dtypes(include=["object", "category"]).columns.tolist(),
    "Datetime": df.select_dtypes(include=["datetime64[ns]", "datetime64[ns, UTC]"]).columns.tolist(),
    "Boolean": df.select_dtypes(include=["bool"]).columns.tolist(),
}
other_cols = [c for c in df.columns if c not in sum(dtype_map.values(), [])]
dtype_map["Other"] = other_cols

colA, colB = st.columns(2)
with colA:
    for label in ["Numeric", "Categorical", "Datetime"]:
        cols = dtype_map[label]
        st.markdown(f"**{label} ({len(cols)})**")
        st.write(cols if cols else "—")
with colB:
    for label in ["Boolean", "Other"]:
        cols = dtype_map[label]
        st.markdown(f"**{label} ({len(cols)})**")
        st.write(cols if cols else "—")

with st.expander("🧬 Raw dtypes table"):
    st.dataframe(df.dtypes.rename("dtype").to_frame(), use_container_width=True)

# ---------- Missing / Nulls ----------
st.subheader("Missing & Null Values")
null_counts = df.isnull().sum()
null_pct = (null_counts / len(df) * 100).round(2)
missing_df = (
    pd.DataFrame({"missing_count": null_counts, "missing_pct": null_pct})
    .sort_values("missing_pct", ascending=False)
)
left, right = st.columns(2)
with left:
    st.metric("Columns with any missing", int((null_counts > 0).sum()))
with right:
    overall_missing = int(df.isnull().values.sum())
    st.metric("Total missing cells", f"{overall_missing:,}")

st.dataframe(missing_df, use_container_width=True)

# ---------- Duplicates ----------
st.subheader("Duplicates")
dup_count = df.duplicated().sum()
dup_exists = dup_count > 0
st.write(f"**Duplicate rows exist?** {'✅ Yes' if dup_exists else '❌ No'}")
if dup_exists:
    st.write(f"Number of duplicated rows: **{dup_count:,}**")
    with st.expander("Show duplicated rows"):
        st.dataframe(df[df.duplicated(keep=False)], use_container_width=True)

# ---------- Describe / Summary ----------
st.subheader("Descriptive Statistics")
tab_num, tab_cat, tab_all = st.tabs(["Numeric", "Categorical", "All (mixed)"])

with tab_num:
    if dtype_map["Numeric"]:
        st.dataframe(df[dtype_map["Numeric"]].describe().T, use_container_width=True)
    else:
        st.info("No numeric columns.")

with tab_cat:
    if dtype_map["Categorical"]:
        st.dataframe(df[dtype_map["Categorical"]].describe(include=["object", "category"]).T, use_container_width=True)
    else:
        st.info("No categorical columns.")

with tab_all:
    # include='all' can be slow; allow user to trigger
    if st.checkbox("Compute describe(include='all') (may be slow on large data)"):
        st.dataframe(df.describe(include="all", datetime_is_numeric=True).T, use_container_width=True)
    else:
        st.caption("Enable the checkbox to compute a full mixed-type describe.")

# ---------- Unique values (quick look) ----------
st.subheader("Unique Values per Column")
uni = df.nunique(dropna=True).rename("unique_values").to_frame()
st.dataframe(uni.sort_values("unique_values", ascending=False), use_container_width=True)

with st.expander("🔢 Value counts for categorical columns (top 10 each)"):
    top_k = st.slider("Top K", 3, 30, 10, step=1)
    if dtype_map["Categorical"]:
        for col in dtype_map["Categorical"]:
            st.markdown(f"**{col}**")
            vc = df[col].value_counts(dropna=False).head(top_k)
            st.dataframe(vc.rename("count").to_frame(), use_container_width=True)
    else:
        st.info("No categorical columns.")

# ---------- Optional: simple correlations (numeric only) ----------
with st.expander("📈 Correlations (numeric-only)"):
    if len(dtype_map["Numeric"]) >= 2:
        corr = df[dtype_map["Numeric"]].corr(numeric_only=True)
        st.dataframe(corr, use_container_width=True)
    else:
        st.info("Need at least two numeric columns to compute correlations.")
