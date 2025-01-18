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
if "results_state" not in st.session_state:
    st.session_state.results_state = {}

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
    uploaded_file_1 = st.file_uploader(
        "Upload Piutang Overdue (.txt or .xlsx)", type=["txt", "xlsx"], key="file1"
    )
    if uploaded_file_1:
        st.session_state.uploaded_file_1 = uploaded_file_1
    
    st.session_state.results_state['compute_text_to_column_overdue'] = st.checkbox(
        "Data Rapi (Piutang Overdue)", 
        value=st.session_state.results_state.get('compute_text_to_column_overdue', False)
    )
    st.session_state.results_state['compute_overdue_table'] = st.checkbox(
        "Tabel Over Due",
        value=st.session_state.results_state.get('compute_overdue_table', False)
    )
    st.session_state.results_state['compute_overdue_chart'] = st.checkbox(
        "Grafik Over Due",
        value=st.session_state.results_state.get('compute_overdue_chart', False)
    )

    st.header("Upload EDI File")
    uploaded_file_2 = st.file_uploader(
        "Upload EDI File (.txt or .xlsx)", type=["txt", "xlsx"], key="file2"
    )
    if uploaded_file_2:
        st.session_state.uploaded_file_2 = uploaded_file_2

    st.session_state.results_state['compute_text_to_column_edi'] = st.checkbox(
        "Data Rapi (EDI File)",
        value=st.session_state.results_state.get('compute_text_to_column_edi', False)
    )

# Helper Function to Create Excel Files
def to_excel(df):
    output = BytesIO()
    df.to_excel(output, index=False, engine='openpyxl')
    output.seek(0)
    return output

# Function to Process Piutang Overdue
def process_piutang_overdue(file):
    try:
        if file.name.endswith(".xlsx"):
            df = pd.read_excel(file)
        else:
            df = pd.read_csv(file, delimiter="|", on_bad_lines="skip", low_memory=False)

        # Store processed data in session state for Results section
        st.session_state.results_state['piutang_overdue_df'] = df

        return df
    except Exception as e:
        st.error(f"Error processing file: {e}")
        return None

# Function to Generate Grafik Over Due
def generate_overdue_chart(df):
    try:
        if "OVER DUE" in df.columns and "MTXVAL" in df.columns:
            bins = [1, 14, 30, 60, float("inf")]
            labels = ["1-14", "15-30", "31-60", "60+"]
            df["OVER DUE Category"] = pd.cut(df["OVER DUE"], bins=bins, labels=labels, right=True)

            overdue_summary = df.groupby("OVER DUE Category").agg(
                MTXVAL_Sum=("MTXVAL", "sum"),
                Count=("MTXVAL", "size"),
            ).reset_index()

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
            return fig
        else:
            st.warning("The required columns 'OVER DUE' or 'MTXVAL' are missing in the data.")
            return None
    except Exception as e:
        st.error(f"Error generating chart: {e}")
        return None

# Results Section
if selected_menu == "Results":
    st.header("Results")

    # Check if Piutang Overdue file was uploaded
    if st.session_state.uploaded_file_1:
        df = st.session_state.results_state.get('piutang_overdue_df') or process_piutang_overdue(st.session_state.uploaded_file_1)
        
        st.session_state.results_state['compute_text_to_column_overdue'] = st.checkbox(
            "Data Rapi (Piutang Overdue)",
            value=st.session_state.results_state.get('compute_text_to_column_overdue', False)
        )
        st.session_state.results_state['compute_overdue_table'] = st.checkbox(
            "Tabel Over Due",
            value=st.session_state.results_state.get('compute_overdue_table', False)
        )
        st.session_state.results_state['compute_overdue_chart'] = st.checkbox(
            "Grafik Over Due",
            value=st.session_state.results_state.get('compute_overdue_chart', False)
        )

        if st.session_state.results_state['compute_text_to_column_overdue']:
            st.write("### Data Rapi (Piutang Overdue)")
            st.dataframe(df)

        if st.session_state.results_state['compute_overdue_chart']:
            fig = generate_overdue_chart(df)
            if fig:
                st.pyplot(fig)

    # Check if EDI File was uploaded
    if st.session_state.uploaded_file_2:
        st.write("EDI File processing goes here... (similar logic as above)")
