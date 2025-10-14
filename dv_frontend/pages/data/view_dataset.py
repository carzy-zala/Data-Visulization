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

# ---------- PDF EXPORT (Selectable, 2-decimals, fixed layout) ----------
from io import BytesIO
from datetime import datetime

# -------- formatting helpers (readable & fixed) --------
def _format_df_for_pdf(
    df: pd.DataFrame,
    *,
    max_rows: int = 30,
    max_cols: int = 12,
    str_maxlen: int = 60,
) -> pd.DataFrame:
    """
    Make a DataFrame readable for PDF:
    - keep at most max_rows x max_cols
    - round numeric columns to 2 decimals
    - truncate long strings with ellipsis
    - stringify everything (reportlab-friendly)
    """
    if df is None or df.empty:
        return pd.DataFrame()

    d = df.copy()

    # limit rows/cols
    if d.shape[0] > max_rows:
        d = d.head(max_rows)
    if d.shape[1] > max_cols:
        keep = list(d.columns[:max_cols])
        d = d[keep]

    # round numeric to 2 decimals
    num_cols = d.select_dtypes(include=[np.number]).columns
    if len(num_cols) > 0:
        d[num_cols] = d[num_cols].round(2)

    # truncate long strings (columns and values)
    def _trunc(x):
        if pd.isna(x):
            return ""
        s = str(x)
        return (s[:str_maxlen - 1] + "…") if len(s) > str_maxlen else s

    d.columns = [_trunc(c) for c in d.columns]
    d = d.applymap(_trunc)

    # ensure string type
    return d.astype(str)


def _table_from_df(df: pd.DataFrame, style, repeat_header=True):
    """Basic reportlab Table from DataFrame; lets reportlab handle widths."""
    from reportlab.platypus import Table
    if df is None or df.empty:
        df = pd.DataFrame({"info": ["(no data)"]})

    # add index as first column
    data = [["#"] + list(df.columns)]
    for idx, row in df.iterrows():
        data.append([str(idx)] + [str(v) for v in row.tolist()])

    tbl = Table(data, repeatRows=1 if repeat_header else 0)
    tbl.setStyle(style)
    return tbl


def create_pdf_report(df: pd.DataFrame, sections: dict, title: str = "Dataset Profile Report") -> bytes:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, TableStyle, PageBreak

    buf = BytesIO()
    doc = SimpleDocTemplate(
        buf,
        pagesize=A4,
        leftMargin=28, rightMargin=28, topMargin=30, bottomMargin=28,
        title=title,
    )

    styles = getSampleStyleSheet()
    h1 = styles["Heading1"]
    h2 = styles["Heading2"]
    p  = styles["BodyText"]
    p.fontSize = 9
    p.leading = 11

    tstyle = TableStyle([
        ("FONTNAME", (0,0), (-1,-1), "Helvetica"),
        ("FONTSIZE", (0,0), (-1,-1), 8),
        ("GRID", (0,0), (-1,-1), 0.25, colors.grey),
        ("ALIGN", (0,0), (-1,0), "CENTER"),
        ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#F5F5F5")),
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
        ("LEFTPADDING", (0,0), (-1,-1), 4),
        ("RIGHTPADDING", (0,0), (-1,-1), 4),
        ("TOPPADDING", (0,0), (-1,-1), 2),
        ("BOTTOMPADDING", (0,0), (-1,-1), 2),
    ])

    story = []
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    story += [Paragraph(title, h1), Paragraph(f"Generated: {now}", p), Spacer(1, 8)]

    # dtype buckets once
    dtype_map = {
        "Numeric": df.select_dtypes(include=[np.number]).columns.tolist(),
        "Categorical": df.select_dtypes(include=["object", "category"]).columns.tolist(),
        "Datetime": df.select_dtypes(include=["datetime64[ns]", "datetime64[ns, UTC]"]).columns.tolist(),
        "Boolean": df.select_dtypes(include=["bool"]).columns.tolist(),
    }
    other_cols = [c for c in df.columns if c not in sum(dtype_map.values(), [])]
    dtype_map["Other"] = other_cols

    # Quick stats
    if sections.get("quick_stats", True):
        n_rows, n_cols = df.shape
        mem_mb = round(df.memory_usage(deep=True).sum() / (1024**2), 2)
        dup_rows = int(df.duplicated().sum())
        qs = pd.DataFrame({
            "Metric": ["Rows", "Columns", "Memory (MB)", "Duplicated Rows"],
            "Value": [f"{n_rows:,}", f"{n_cols:,}", f"{mem_mb:,.2f}", f"{dup_rows:,}"]
        }).set_index("Metric")
        story += [Paragraph("Quick Stats", h2), _table_from_df(_format_df_for_pdf(qs), tstyle), Spacer(1, 10)]

    # Columns by Type
    if sections.get("columns_by_type", True):
        dtypes_df = pd.DataFrame(
            [(k, len(v), ", ".join(v[:50])) for k, v in dtype_map.items()],
            columns=["Type", "Count", "Columns (first 50)"]
        ).set_index("Type")
        story += [Paragraph("Columns by Type", h2), _table_from_df(_format_df_for_pdf(dtypes_df), tstyle), Spacer(1, 10)]

    # Missing values
    if sections.get("missing", True):
        null_counts = df.isnull().sum()
        null_pct = (null_counts / len(df) * 100).round(2)
        missing_df = pd.DataFrame({"missing_count": null_counts, "missing_pct": null_pct}) \
                        .sort_values("missing_pct", ascending=False)
        story += [Paragraph("Missing & Null Values", h2), _table_from_df(_format_df_for_pdf(missing_df), tstyle), Spacer(1, 10)]

    # Preview head / tail
    if sections.get("preview", True):
        story += [
            Paragraph("Preview (Head 10)", h2), _table_from_df(_format_df_for_pdf(df.head(10)), tstyle), Spacer(1, 6),
            Paragraph("Preview (Tail 10)", h2), _table_from_df(_format_df_for_pdf(df.tail(10)), tstyle),
            PageBreak()
        ]

    # Describe numeric
    if sections.get("describe_numeric", True) and len(dtype_map["Numeric"]) > 0:
        num_desc = df[dtype_map["Numeric"]].describe().T.round(2)
        story += [Paragraph("Descriptive Statistics (Numeric)", h2), _table_from_df(_format_df_for_pdf(num_desc), tstyle), Spacer(1, 10)]

    # Describe categorical
    if sections.get("describe_categorical", True) and len(dtype_map["Categorical"]) > 0:
        cat_desc = df[dtype_map["Categorical"]].describe(include=["object", "category"]).T
        story += [Paragraph("Descriptive Statistics (Categorical)", h2), _table_from_df(_format_df_for_pdf(cat_desc), tstyle), Spacer(1, 10)]

    # Unique values
    if sections.get("unique_values", True):
        uni = df.nunique(dropna=True).rename("unique_values").to_frame().sort_values("unique_values", ascending=False)
        story += [Paragraph("Unique Values per Column", h2), _table_from_df(_format_df_for_pdf(uni), tstyle), Spacer(1, 10)]

    # Correlations (numeric)
    if sections.get("correlations", True) and len(dtype_map["Numeric"]) >= 2:
        corr = df[dtype_map["Numeric"]].corr(numeric_only=True).round(2)
        story += [Paragraph("Correlations (Numeric-Only)", h2), _table_from_df(_format_df_for_pdf(corr), tstyle), Spacer(1, 10)]

    # Duplicates sample
    if sections.get("duplicates", True):
        dup_count = int(df.duplicated().sum())
        if dup_count > 0:
            dups_sample = df[df.duplicated(keep=False)].head(30)
            story += [Paragraph(f"Duplicated Rows (showing first 30 of {dup_count:,})", h2),
                      _table_from_df(_format_df_for_pdf(dups_sample), tstyle), Spacer(1, 10)]

    doc.build(story)
    return buf.getvalue()


# ---- UI: section selector + horizontal Generate/Download ----
st.subheader("📄 PDF Report")
with st.expander("Select sections to include", expanded=False):
    s1, s2, s3 = st.columns(3)
    with s1:
        include_quick = st.checkbox("Quick Stats", True)
        include_cols  = st.checkbox("Columns by Type", True)
        include_miss  = st.checkbox("Missing Values", True)
    with s2:
        include_prev  = st.checkbox("Preview (Head/Tail)", True)
        include_descn = st.checkbox("Describe (Numeric)", True)
        include_descc = st.checkbox("Describe (Categorical)", True)
    with s3:
        include_unique = st.checkbox("Unique Values", True)
        include_corr   = st.checkbox("Correlations", True)
        include_dups   = st.checkbox("Duplicates Sample", True)

sections = {
    "quick_stats": include_quick,
    "columns_by_type": include_cols,
    "missing": include_miss,
    "preview": include_prev,
    "describe_numeric": include_descn,
    "describe_categorical": include_descc,
    "unique_values": include_unique,
    "correlations": include_corr,
    "duplicates": include_dups,
}

if "pdf_bytes_cache" not in st.session_state:
    st.session_state["pdf_bytes_cache"] = None

btn_gen, btn_dl, _sp = st.columns([1.2, 2.2, 6])
with btn_gen:
    if st.button("⚙️ Generate", key="pdf_generate"):
        try:
            st.session_state["pdf_bytes_cache"] = create_pdf_report(
                df, sections, title="Dataset Profile Report"
            )
            st.toast("Report generated.")
        except Exception as e:
            st.session_state["pdf_bytes_cache"] = None
            st.error("Failed to generate PDF report.")
            st.exception(e)

with btn_dl:
    st.download_button(
        "⬇️ Download PDF",
        data=st.session_state["pdf_bytes_cache"] if st.session_state["pdf_bytes_cache"] else b"",
        file_name="dataset_report.pdf",
        mime="application/pdf",
        disabled=st.session_state["pdf_bytes_cache"] is None,
        key="pdf_download",
    )
# ---------- END PDF EXPORT ----------
