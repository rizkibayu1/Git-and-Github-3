import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

# Streamlit App Title
st.title("📊 Auto Report Processor & Dashboard")

# Initialize session state for file uploads and checkboxes
if "uploaded_file_1" not in st.session_state:
    st.session_state.uploaded_file_1 = None
if "uploaded_file_2" not in st.session_state:
    st.session_state.uploaded_file_2 = None
if "compute_text_to_column_overdue" not in st.session_state:
    st.session_state.compute_text_to_column_overdue = False
if "compute_overdue_table" not in st.session_state:
    st.session_state.compute_overdue_table = False
if "compute_overdue_chart" not in st.session_state:
    st.session_state.compute_overdue_chart = False
if "compute_text_to_column_edi" not in st.session_state:
    st.session_state.compute_text_to_column_edi = False

# Sidebar Menu
with st.sidebar:
    st.header("Navigation")
    selected_menu = st.radio(
        "Choose a Section",
        ["Upload Files", "Results"]
    )

if selected_menu == "Upload Files":
    # Upload Piutang Overdue
    st.header("Upload Piutang Overdue Report")
    st.session_state.uploaded_file_1 = st.file_uploader(
        "Upload Piutang Overdue (.txt or .xlsx)", type=["txt", "xlsx"], key="file1"
    )
    st.session_state.compute_text_to_column_overdue = st.checkbox("Data Rapi (Piutang Overdue)")
    st.session_state.compute_overdue_table = st.checkbox("Tabel Over Due")
    st.session_state.compute_overdue_chart = st.checkbox("Grafik Over Due")

    # Upload EDI File
    st.header("Upload EDI File")
    st.session_state.uploaded_file_2 = st.file_uploader(
        "Upload EDI File (.txt or .xlsx)", type=["txt", "xlsx"], key="file2"
    )
    st.session_state.compute_text_to_column_edi = st.checkbox("Data Rapi (EDI File)")

# Function to process Piutang Overdue report
def process_piutang_overdue(file):
    if file:
        try:
            # Determine file type
            if file.name.endswith(".xlsx"):
                df = pd.read_excel(file)
            else:
                df = pd.read_csv(file, delimiter="|", on_bad_lines="skip", low_memory=False)

            # Data Rapi
            if st.session_state.compute_text_to_column_overdue:
                st.write("### Data Rapi (Piutang Overdue)")
                st.dataframe(df)

            # Tabel Over Due
            if st.session_state.compute_overdue_table:
                st.write("### Tabel Over Due")
                if "OVER DUE" in df.columns and "MTXVAL" in df.columns:
                    bins = [1, 14, 30, 60, float("inf")]
                    labels = ["1-14", "15-30", "31-60", "60+"]
                    df["OVER DUE Category"] = pd.cut(df["OVER DUE"], bins=bins, labels=labels, right=True)

                    overdue_summary = df.groupby("OVER DUE Category").agg(
                        MTXVAL_Sum=("MTXV
