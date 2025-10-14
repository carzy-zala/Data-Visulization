import streamlit as st
import pandas as pd
import io
import csv

st.set_page_config(page_title="Upload Dataset", page_icon="📂", layout="wide")
st.title("📂 Upload Dataset")

st.markdown(
    """
    **💡 Tip:** For best performance, please upload datasets **≤ 150 MB**.  
    Larger files may slow down processing or exceed browser/memory limits.
    """
)

# --- uploader key versioning to allow clearing after processing ---
if "uploader_key" not in st.session_state:
    st.session_state["uploader_key"] = 0  # will be appended to the widget key

# One-time toast after a successful upload+rerun
if st.session_state.get("just_uploaded"):
    st.success("✅ Dataset is ready and stored in session.")
    st.session_state.pop("just_uploaded", None)

def _read_csv_with_sniff(file_bytes: bytes) -> pd.DataFrame:
    """Try reading CSV with delimiter sniffing fallback."""
    bio = io.BytesIO(file_bytes)
    try:
        return pd.read_csv(bio)
    except Exception:
        pass

    bio.seek(0)
    head = bio.read(4096).decode(errors="ignore")
    sniffer = csv.Sniffer()
    try:
        dialect = sniffer.sniff(head, delimiters=[",", ";", "|", "\t"])
        delim = dialect.delimiter
    except Exception:
        delim = ","
    bio.seek(0)
    return pd.read_csv(bio, sep=delim)

# Use a versioned key so we can "clear" the uploader by bumping the key
uploaded_file = st.file_uploader(
    "Upload CSV or Excel file",
    type=["csv", "xlsx", "xls"],
    key=f"uploader_{st.session_state['uploader_key']}"
)

if uploaded_file is not None:
    # Optional: fingerprint to avoid accidental reprocessing
    fp = (uploaded_file.name, uploaded_file.size)
    if st.session_state.get("last_file_fp") != fp:
        with st.status("Processing file…", expanded=True) as status:
            try:
                size_mb = (uploaded_file.size or 0) / (1024**2)
                st.write(f"• File: **{uploaded_file.name}**  \n• Size: **{size_mb:,.2f} MB**")

                status.update(label="Reading file…")
                if uploaded_file.name.lower().endswith(".csv"):
                    file_bytes = uploaded_file.getvalue()
                    df = _read_csv_with_sniff(file_bytes)
                else:
                    df = pd.read_excel(uploaded_file)

                status.update(label="Optimizing & validating…")
                # light datetime inference
                for col in df.columns:
                    s = df[col]
                    if s.dtype == "object":
                        try:
                            converted = pd.to_datetime(s, errors="ignore", infer_datetime_format=True)
                            if getattr(converted.dtype, "kind", "") == "M":
                                df[col] = converted
                        except Exception:
                            pass

                status.update(label="Saving to session…")
                st.session_state["uploaded_df"] = df
                st.session_state["just_uploaded"] = True
                st.session_state["last_file_fp"] = fp

                # CLEAR the uploader by bumping the versioned key, then rerun
                st.session_state["uploader_key"] += 1

                status.update(label="Done! Rerendering pages…", state="complete", expanded=False)

            except Exception as e:
                status.update(label="Failed to process file.", state="error", expanded=True)
                st.exception(e)
            else:
                st.rerun()
    # If fingerprint matches, do nothing (prevents reprocessing)

# Preview if dataset is already in session
if st.session_state.get("uploaded_df") is not None and uploaded_file is None:
    df = st.session_state["uploaded_df"]
    n_rows, n_cols = df.shape
    st.caption(f"Current dataset in session: **{n_rows:,} rows × {n_cols:,} cols**")
    st.dataframe(df.head(10), use_container_width=True)
else:
    st.info("Upload a CSV or Excel file to continue.")
