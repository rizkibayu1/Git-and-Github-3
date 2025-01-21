import streamlit as st
import pandas as pd
import plotly.express as px
from io import BytesIO

# Streamlit App Title
st.title("📊 Auto Report Processor & Dashboard")

# Initialize session state for file uploads and checkboxes
if "uploaded_file_1" not in st.session_state:
    st.session_state.uploaded_file_1 = None
if "uploaded_file_2" not in st.session_state:
    st.session_state.uploaded_file_2 = None

# Function to create Excel file from DataFrame
def to_excel(df):
    # Convert dataframe to Excel and save in BytesIO buffer
    output = BytesIO()
    df.to_excel(output, index=False, engine='openpyxl')
    output.seek(0)
    return output

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
            st.write("### Data Rapi (Piutang Overdue)")
            st.dataframe(df)

            # Create Excel file for download
            excel_file = to_excel(df)
            st.download_button(
                label="Download as Excel",
                data=excel_file,
                file_name="data_rapi_piutang_overdue.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

            # Tabel Over Due and Chart
            if "OVER DUE" in df.columns and "MTXVAL" in df.columns:
                bins = [1, 14, 30, 60, float("inf")]
                labels = ["1-14", "15-30", "31-60", "60+"]
                df["OVER DUE Category"] = pd.cut(df["OVER DUE"], bins=bins, labels=labels, right=True)

                overdue_summary = df.groupby("OVER DUE Category").agg(
                    MTXVAL_Sum=("MTXVAL", "sum"),
                    Count=("MTXVAL", "size"),
                ).reset_index()

                st.write("### Tabel Over Due")
                st.dataframe(overdue_summary)

                # Create Excel file for download
                excel_file = to_excel(overdue_summary)
                st.download_button(
                    label="Download Overdue Summary as Excel",
                    data=excel_file,
                    file_name="overdue_summary.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )

                # Interactive Chart
                st.write("### Grafik Over Due")
                fig = px.bar(
                    overdue_summary,
                    x="OVER DUE Category",
                    y="MTXVAL_Sum",
                    text="MTXVAL_Sum",
                    labels={"MTXVAL_Sum": "Sum of MTXVAL", "OVER DUE Category": "Overdue Category"},
                    title="Interactive Grafik Over Due"
                )
                fig.update_traces(texttemplate="Rp%{text:,.0f}", textposition="outside")
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("The required columns 'OVER DUE' or 'MTXVAL' are missing in the data.")

        except Exception as e:
            st.error(f"An unexpected error occurred: {e}")

# Function to process EDI File report
def process_edi_file(file):
    if file:
        try:
            # Determine file type
            if file.name.endswith(".xlsx"):
                df = pd.read_excel(file)
            else:
                df = pd.read_csv(file, delimiter="|", on_bad_lines="skip", low_memory=False)

            # Data Rapi
            st.write("### Data Rapi (EDI File)")
            st.dataframe(df)

            # Create Excel file for download
            excel_file = to_excel(df)
            st.download_button(
                label="Download as Excel",
                data=excel_file,
                file_name="data_rapi_edi_file.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

        except Exception as e:
            st.error(f"An unexpected error occurred: {e}")

# Tabs for Piutang Overdue and EDI File
tabs = st.tabs(["Piutang Overdue", "EDI File"])

# Piutang Overdue Tab
with tabs[0]:
    st.header("Piutang Overdue Report")
    st.session_state.uploaded_file_1 = st.file_uploader(
        "Upload Piutang Overdue (.txt or .xlsx)", type=["txt", "xlsx"], key="file1"
    )
    if st.session_state.uploaded_file_1:
        process_piutang_overdue(st.session_state.uploaded_file_1)

# EDI File Tab
with tabs[1]:
    st.header("EDI File Report")
    st.session_state.uploaded_file_2 = st.file_uploader(
        "Upload EDI File (.txt or .xlsx)", type=["txt", "xlsx"], key="file2"
    )
    if st.session_state.uploaded_file_2:
        process_edi_file(st.session_state.uploaded_file_2)
