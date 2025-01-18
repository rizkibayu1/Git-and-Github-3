import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from io import BytesIO

# Streamlit App Title
st.title("📊 Auto Report Processor & Dashboard")

# Sidebar Menu
with st.sidebar:
    st.header("Navigation")
    selected_menu = st.radio(
        "Choose a Section",
        ["Upload Files", "Results"]
    )

# Initialize session state for uploaded files
if 'uploaded_file_1' not in st.session_state:
    st.session_state['uploaded_file_1'] = None

if 'uploaded_file_2' not in st.session_state:
    st.session_state['uploaded_file_2'] = None

# File upload section
if selected_menu == "Upload Files":
    # Upload Piutang Overdue
    st.header("Upload Piutang Overdue Report")
    uploaded_file_1 = st.file_uploader(
        "Upload Piutang Overdue (.txt or .xlsx)", type=["txt", "xlsx"], key="file1", label_visibility="collapsed"
    )

    # Checkbox values (Defined here so that they're always available)
    compute_text_to_column_overdue = st.checkbox("Data Rapi (Piutang Overdue)", key="compute_text_to_column_overdue")
    compute_overdue_table = st.checkbox("Tabel Over Due", key="compute_overdue_table")
    compute_overdue_chart = st.checkbox("Grafik Over Due", key="compute_overdue_chart")

    # Upload EDI File
    st.header("Upload EDI File")
    uploaded_file_2 = st.file_uploader(
        "Upload EDI File (.txt or .xlsx)", type=["txt", "xlsx"], key="file2", label_visibility="collapsed"
    )
    compute_text_to_column_edi = st.checkbox("Data Rapi (EDI File)", key="compute_text_to_column_edi")

    # Update session state with the uploaded files
    if uploaded_file_1 is not None:
        st.session_state['uploaded_file_1'] = uploaded_file_1

    if uploaded_file_2 is not None:
        st.session_state['uploaded_file_2'] = uploaded_file_2

# Function to create Excel file from DataFrame
def to_excel(df):
    # Convert dataframe to Excel and save in BytesIO buffer
    output = BytesIO()
    df.to_excel(output, index=False, engine='openpyxl')
    output.seek(0)
    return output

# Function to process Piutang Overdue report
def process_piutang_overdue(file, compute_text_to_column_overdue, compute_overdue_table, compute_overdue_chart):
    if file:
        try:
            # Determine file type
            if file.name.endswith(".xlsx"):
                df = pd.read_excel(file)
            else:
                df = pd.read_csv(file, delimiter="|", on_bad_lines="skip", low_memory=False)

            # Data Rapi
            if compute_text_to_column_overdue:
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
            if compute_overdue_table:
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
            if compute_overdue_chart:
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
                    fig, ax = plt.subplots(figsize=(8, 4))  # Smaller figure size
                    bars = ax.bar(overdue_summary["OVER DUE Category"], overdue_summary["MTXVAL_Sum"])

                    for bar, count, sum_val in zip(bars, overdue_summary["Count"], overdue_summary["MTXVAL_Sum"]):
                        yval = bar.get_height()
                        formatted_sum = f"Rp{yval:,.0f}"
                        label = f"{formatted_sum}\nCount: {count}"
                        ax.text(bar.get_x() + bar.get_width() / 2, yval + 50000, label, ha="center", va="bottom", fontsize=8)

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
def process_edi_file(file, compute_text_to_column_edi):
    if file:
        try:
            # Determine file type
            if file.name.endswith(".xlsx"):
                df = pd.read_excel(file)
            else:
                df = pd.read_csv(file, delimiter="|", on_bad_lines="skip", low_memory=False)

            # Data Rapi
            if compute_text_to_column_edi:
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

# Results section with file persistence
if selected_menu == "Results":
    st.header("Results")

    # Retrieve uploaded files from session state
    uploaded_file_1 = st.session_state.get('uploaded_file_1', None)
    uploaded_file_2 = st.session_state.get('uploaded_file_2', None)

    # Layout in two columns for space efficiency
    col1, col2 = st.columns(2)

    with col1:
        if uploaded_file_1:
            process_piutang_overdue(uploaded_file_1, compute_text_to_column_overdue, compute_overdue_table, compute_overdue_chart)

    with col2:
        if uploaded_file_2:
            process_edi_file(uploaded_file_2, compute_text_to_column_edi)
