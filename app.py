import streamlit as st
import pandas as pd
from io import BytesIO

# Streamlit App Title
st.title("Dashboard Monitoring AOS")

# Initialize session state for file uploads and checkboxes
if "uploaded_file_1" not in st.session_state:
    st.session_state.uploaded_file_1 = None
if "compute_text_to_column_overdue" not in st.session_state:
    st.session_state.compute_text_to_column_overdue = False
if "uploaded_file_2" not in st.session_state:
    st.session_state.uploaded_file_2 = None
if "compute_text_to_column_opname" not in st.session_state:
    st.session_state.compute_text_to_column_opname = False

# Tabs for Piutang Overdue and Opname Faktur
tab1, tab2 = st.tabs(["📊 Piutang Overdue", "📋 Opname Faktur"])

# Function to create an Excel file from a DataFrame
def to_excel(df):
    output = BytesIO()
    df.to_excel(output, index=False, engine="openpyxl")
    output.seek(0)
    return output

# Tab 1: Piutang Overdue
with tab1:
    st.header("Piutang Overdue")
    st.session_state.uploaded_file_1 = st.file_uploader(
        "Upload Piutang Overdue (.txt or .xlsx)", type=["txt", "xlsx"], key="file1"
    )
    st.session_state.compute_text_to_column_overdue = st.checkbox("Data Rapi (Piutang Overdue)")

    # Process Piutang Overdue
    if st.session_state.uploaded_file_1 and st.session_state.compute_text_to_column_overdue:
        try:
            # Determine file type and read the file
            file = st.session_state.uploaded_file_1
            if file.name.endswith(".xlsx"):
                df = pd.read_excel(file)
            else:
                df = pd.read_csv(file, delimiter="|", on_bad_lines="skip", low_memory=False)

            # Display processed data
            st.write("### Data Rapi (Piutang Overdue)")
            st.dataframe(df)

            # Download processed data as Excel
            excel_file = to_excel(df)
            st.download_button(
                label="Download as Excel",
                data=excel_file,
                file_name="data_rapi_piutang_overdue.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )
        except Exception as e:
            st.error(f"An unexpected error occurred: {e}")

# Tab 2: Opname Faktur
with tab2:
    st.header("Opname Faktur")
    st.session_state.uploaded_file_2 = st.file_uploader(
        "Upload Opname Faktur (.txt or .xlsx)", type=["txt", "xlsx"], key="file2"
    )
    st.session_state.compute_text_to_column_opname = st.checkbox("Data Rapi (Opname Faktur)")

    # Process Opname Faktur
    if st.session_state.uploaded_file_2 and st.session_state.compute_text_to_column_opname:
        try:
            # Determine file type and read the file
            file = st.session_state.uploaded_file_2
            if file.name.endswith(".xlsx"):
                df = pd.read_excel(file)
            else:
                df = pd.read_csv(file, delimiter="|", on_bad_lines="skip", low_memory=False)

            # Display processed data
            st.write("### Data Rapi (Opname Faktur)")
            st.dataframe(df)

            # Download processed data as Excel
            excel_file = to_excel(df)
            st.download_button(
                label="Download as Excel",
                data=excel_file,
                file_name="data_rapi_opname_faktur.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )
        except Exception as e:
            st.error(f"An unexpected error occurred: {e}")
