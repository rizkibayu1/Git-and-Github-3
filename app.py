import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from io import BytesIO

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

# Upload Files Section
if selected_menu == "Upload Files":
    st.header("Upload Piutang Overdue Report")
    if not st.session_state.uploaded_file_1:
        st.session_state.uploaded_file_1 = st.file_uploader(
            "Upload Piutang Overdue (.txt or .xlsx)", type=["txt", "xlsx"], key="file1"
        )
    
    st.session_state.compute_text_to_column_overdue = st.checkbox("Data Rapi (Piutang Overdue)", value=st.session_state.compute_text_to_column_overdue)
    st.session_state.compute_overdue_table = st.checkbox("Tabel Over Due", value=st.session_state.compute_overdue_table)
    st.session_state.compute_overdue_chart = st.checkbox("Grafik Over Due", value=st.session_state.compute_overdue_chart)

    st.header("Upload EDI File")
    if not st.session_state.uploaded_file_2:
        st.session_state.uploaded_file_2 = st.file_uploader(
            "Upload EDI File (.txt or .xlsx)", type=["txt", "xlsx"], key="file2"
        )
    
    st.session_state.compute_text_to_column_edi = st.checkbox("Data Rapi (EDI File)", value=st.session_state.compute_text_to_column_edi)

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
            if st.session_state.compute_text_to_column_overdue:
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

            # Tabel Over Due
            if st.session_state.compute_overdue_table:
                st.write("### Tabel Over Due")
                if "OVER DUE" in df.columns and "MTXVAL" in df.columns:
                    bins = [1, 14, 30, 60, float("inf")]
                    labels = ["1-14", "15-30", "31-60", "60+"]
                    df["OVER DUE Category"] = pd.cut(df["OVER DUE"], bins=bins, labels=labels, right=True)

                    overdue_summary = df.groupby("OVER DUE Category").agg(
                        MTXVAL_Sum=("MTXVAL", "sum"),
                        Count=("MTXVAL", "size"),
                    ).reset_index()

                    st.dataframe(overdue_summary)

                    # Create Excel file for download
                    excel_file = to_excel(overdue_summary)
                    st.download_button(
                        label="Download Overdue Summary as Excel",
                        data=excel_file,
                        file_name="overdue_summary.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
                else:
                    st.warning("The required columns 'OVER DUE' or 'MTXVAL' are missing in the data.")

            # Grafik Over Due
            if st.session_state.compute_overdue_chart:
                st.write("### Grafik Over Due")
                if "OVER DUE" in df.columns and "MTXVAL" in df.columns:
                    bins = [1, 14, 30, 60, float("inf")]
                    labels = ["1-14", "15-30", "31-60", "60+"]
                    df["OVER DUE Category"] = pd.cut(df["OVER DUE"], bins=bins, labels=labels, right=True)

                    overdue_summary = df.groupby("OVER DUE Category").agg(
                        MTXVAL_Sum=("MTXVAL", "sum"),
                        Count=("MTXVAL", "size"),
                    ).reset_index()

                    # Plot
                    fig, ax = plt.subplots(figsize=(10, 6))
                    bars = ax.bar(overdue_summary["OVER DUE Category"], overdue_summary["MTXVAL_Sum"])

                    for bar, count, sum_val in zip(bars, overdue_summary["Count"], overdue_summary["MTXVAL_Sum"]):
                        yval = bar.get_height()
                        formatted_sum = f"Rp{yval:,.0f}"
                        label = f"{formatted_sum}\nCount: {count}"
                        ax.text(bar.get_x() + bar.get_width() / 2, yval + 50000, label, ha="center", va="bottom", fontsize=10)

                    ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, _: f"Rp{x:,.0f}"))
                    ax.set_xlabel("OVER DUE Categories")
                    ax.set_ylabel("Sum of MTXVAL")
                    ax.set_title("Sum of MTXVAL for Different OVER DUE Categories")
                    st.pyplot(fig)
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
            if st.session_state.compute_text_to_column_edi:
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

# Results Section
if selected_menu == "Results":
    st.header("Results")
    
    # Show file name and options to modify checkboxes in Results
    if st.session_state.uploaded_file_1:
        st.write(f"### Piutang Overdue Report: {st.session_state.uploaded_file_1.name}")
        st.session_state.compute_text_to_column_overdue = st.checkbox("Data Rapi (Piutang Overdue)", value=st.session_state.compute_text_to_column_overdue)
        st.session_state.compute_overdue_table = st.checkbox("Tabel Over Due", value=st.session_state.compute_overdue_table)
        st.session_state.compute_overdue_chart = st.checkbox("Grafik Over Due", value=st.session_state.compute_overdue_chart)
        
        # Trigger file processing based on checkbox states
        process_piutang_overdue(st.session_state.uploaded_file_1)

    if st.session_state.uploaded_file_2:
        st.write(f"### EDI File: {st.session_state.uploaded_file_2.name}")
        st.session_state.compute_text_to_column_edi = st.checkbox("Data Rapi (EDI File)", value=st.session_state.compute_text_to_column_edi)
        
        # Trigger file processing based on checkbox states
        process_edi_file(st.session_state.uploaded_file_2)
