import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO
import plotly.express as px

# Streamlit App Title
st.title("📊 Auto Report Processor & Dashboard")

# Initialize session state for file uploads and checkboxes
for key in [
    "uploaded_file_piutang", "uploaded_file_edi", 
    "compute_text_to_column_overdue", "compute_overdue_table", "compute_overdue_chart",
    "compute_text_to_column_edi"
]:
    if key not in st.session_state:
        st.session_state[key] = None if key.startswith("uploaded_file") else False

# Function to create Excel file from DataFrame
def to_excel(df):
    output = BytesIO()
    df.to_excel(output, index=False, engine="openpyxl")
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
            if st.session_state.compute_text_to_column_overdue:
                st.write("### Data Rapi (Piutang Overdue)")
                st.dataframe(df)

                excel_file = to_excel(df)
                st.download_button(
                    label="Download as Excel",
                    data=excel_file,
                    file_name="data_rapi_piutang_overdue.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                )

            # Tabel Over Due
            if st.session_state.compute_overdue_table:
                st.write("### Tabel Over Due")
                if "OVER DUE" in df.columns and "MTXVAL" in df.columns:
                    bins = [1, 14, 30, 60, float("inf")]
                    labels = ["1-14", "15-30", "31-60", "60+"]
                    df["OVER DUE Category"] = pd.cut(
                        df["OVER DUE"], bins=bins, labels=labels, right=True
                    )

                    overdue_summary = df.groupby("OVER DUE Category").agg(
                        MTXVAL_Sum=("MTXVAL", "sum"),
                        Count=("MTXVAL", "size"),
                    ).reset_index()

                    st.dataframe(overdue_summary)

                    excel_file = to_excel(overdue_summary)
                    st.download_button(
                        label="Download Overdue Summary as Excel",
                        data=excel_file,
                        file_name="overdue_summary.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    )
                else:
                    st.warning(
                        "The required columns 'OVER DUE' or 'MTXVAL' are missing in the data."
                    )

            # Grafik Over Due
            if st.session_state.compute_overdue_chart:
                st.write("### Grafik Over Due")
                if "OVER DUE" in df.columns and "MTXVAL" in df.columns:
                    bins = [1, 14, 30, 60, float("inf")]
                    labels = ["1-14", "15-30", "31-60", "60+"]
                    df["OVER DUE Category"] = pd.cut(
                        df["OVER DUE"], bins=bins, labels=labels, right=True
                    )

                    overdue_summary = df.groupby("OVER DUE Category").agg(
                        MTXVAL_Sum=("MTXVAL", "sum"),
                        Count=("MTXVAL", "size"),
                    ).reset_index()

                    # Interactive Chart with Plotly
                    fig = px.bar(
                        overdue_summary,
                        x="OVER DUE Category",
                        y="MTXVAL_Sum",
                        text="MTXVAL_Sum",
                        labels={"MTXVAL_Sum": "Total (MTXVAL)"},
                        title="Sum of MTXVAL for Different OVER DUE Categories",
                    )
                    fig.update_traces(texttemplate="%{text:.2s}", textposition="outside")
                    fig.update_layout(yaxis=dict(title="Sum of MTXVAL"))
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.warning(
                        "The required columns 'OVER DUE' or 'MTXVAL' are missing in the data."
                    )

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
            if st.session_state.compute_text_to_column_edi:
                st.write("### Data Rapi (EDI File)")
                st.dataframe(df)

                excel_file = to_excel(df)
                st.download_button(
                    label="Download as Excel",
                    data=excel_file,
                    file_name="data_rapi_edi_file.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                )

        except Exception as e:
            st.error(f"An unexpected error occurred: {e}")

# Main Tabs for Piutang Overdue and EDI File
tab1, tab2 = st.tabs(["📄 Piutang Overdue", "📁 EDI File"])

with tab1:
    st.header("Piutang Overdue Report")
    st.session_state.uploaded_file_piutang = st.file_uploader(
        "Upload Piutang Overdue (.txt or .xlsx)",
        type=["txt", "xlsx"],
        key="file_piutang",
    )
    st.session_state.compute_text_to_column_overdue = st.checkbox("Data Rapi (Piutang Overdue)")
    st.session_state.compute_overdue_table = st.checkbox("Tabel Over Due")
    st.session_state.compute_overdue_chart = st.checkbox("Grafik Over Due")

    if st.session_state.uploaded_file_piutang:
        process_piutang_overdue(st.session_state.uploaded_file_piutang)

with tab2:
    st.header("EDI File Report")
    st.session_state.uploaded_file_edi = st.file_uploader(
        "Upload EDI File (.txt or .xlsx)", type=["txt", "xlsx"], key="file_edi"
    )
    st.session_state.compute_text_to_column_edi = st.checkbox("Data Rapi (EDI File)")

    if st.session_state.uploaded_file_edi:
        process_edi_file(st.session_state.uploaded_file_edi)
