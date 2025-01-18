import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Title
st.title("📊 Collapsible Menu Example")

# Collapsible Menu: File Uploads
with st.expander("Step 1: Upload Files", expanded=True):
    st.write("Upload your reports below:")
    uploaded_file_1 = st.file_uploader("Upload Piutang Overdue (.txt or .xlsx)", type=["txt", "xlsx"])
    uploaded_file_2 = st.file_uploader("Upload EDI File (.txt or .xlsx)", type=["txt", "xlsx"])

# Process the files
piutang_overdue_data = None
edi_data = None

if uploaded_file_1:
    try:
        if uploaded_file_1.name.endswith(".xlsx"):
            piutang_overdue_data = pd.read_excel(uploaded_file_1)
        else:
            piutang_overdue_data = pd.read_csv(uploaded_file_1, delimiter="|", on_bad_lines="skip", low_memory=False)
    except Exception as e:
        st.error(f"Error processing Piutang Overdue file: {e}")

if uploaded_file_2:
    try:
        if uploaded_file_2.name.endswith(".xlsx"):
            edi_data = pd.read_excel(uploaded_file_2)
        else:
            edi_data = pd.read_csv(uploaded_file_2, delimiter="|", on_bad_lines="skip", low_memory=False)
    except Exception as e:
        st.error(f"Error processing EDI file: {e}")

# Collapsible Menu: Results
with st.expander("Step 2: View Results"):
    st.write("The results of your uploaded files will appear here.")

    # Display results for Piutang Overdue
    if piutang_overdue_data is not None:
        st.write("### Piutang Overdue - Data Preview")
        st.dataframe(piutang_overdue_data.head())

        # Example: Additional processing
        if "OVER DUE" in piutang_overdue_data.columns:
            st.write("### Overdue Summary")
            overdue_summary = piutang_overdue_data["OVER DUE"].describe()
            st.write(overdue_summary)

    # Display results for EDI File
    if edi_data is not None:
        st.write("### EDI File - Data Preview")
        st.dataframe(edi_data.head())

        # Example: Additional processing
        if "COLUMN_NAME" in edi_data.columns:  # Replace with an actual column name
            st.write("### EDI File Column Summary")
            edi_summary = edi_data["COLUMN_NAME"].value_counts()
            st.write(edi_summary)

    if piutang_overdue_data is None and edi_data is None:
        st.warning("Please upload files in Step 1 to see the results.")
