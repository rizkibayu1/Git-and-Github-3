import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Title
st.title("📊 Auto Report Processor & Dashboard")

# Sidebar for collapsible menu
with st.sidebar:
    st.header("Menu")
    # Collapsible sections in the sidebar
    with st.expander("Step 1: Upload Files", expanded=True):
        st.write("Upload your reports below:")
        uploaded_file_1 = st.file_uploader("Upload Piutang Overdue (.txt or .xlsx)", type=["txt", "xlsx"])
        uploaded_file_2 = st.file_uploader("Upload EDI File (.txt or .xlsx)", type=["txt", "xlsx"])

        # Checkbox options for each file
        st.write("### Options for Piutang Overdue")
        compute_text_to_column_overdue = st.checkbox("Data Rapi (Piutang Overdue)")
        compute_overdue_table = st.checkbox("Tabel Over Due")
        compute_overdue_chart = st.checkbox("Grafik Over Due")

        st.write("### Options for EDI File")
        compute_text_to_column_edi = st.checkbox("Data Rapi (EDI File)")

# Main logic for processing files
def process_piutang_overdue(file):
    if file:
        try:
            # Handle .xlsx and .txt differently
            if file.name.endswith(".xlsx"):
                df = pd.read_excel(file)
            else:
                df = pd.read_csv(file, delimiter="|", on_bad_lines="skip", low_memory=False)

            if compute_text_to_column_overdue:
                st.subheader("Data Rapi (Piutang Overdue)")
                st.dataframe(df)

            if compute_overdue_table:
                st.subheader("Tabel Over Due")
                if "OVER DUE" in df.columns and "MTXVAL" in df.columns:
                    bins = [1, 14, 30, 60, float("inf")]
                    labels = ["1-14", "15-30", "31-60", "60+"]
                    df["OVER DUE Category"] = pd.cut(df["OVER DUE"], bins=bins, labels=labels, right=True)
                    overdue_summary = df.groupby("OVER DUE Category").agg(
                        MTXVAL_Sum=("MTXVAL", "sum"),
                        Count=("MTXVAL", "size")
                    ).reset_index()
                    st.dataframe(overdue_summary)
                else:
                    st.warning("Columns 'OVER DUE' or 'MTXVAL' are missing in the data.")

            if compute_overdue_chart:
                st.subheader("Grafik Over Due")
                if "OVER DUE" in df.columns and "MTXVAL" in df.columns:
                    bins = [1, 14, 30, 60, float("inf")]
                    labels = ["1-14", "15-30", "31-60", "60+"]
                    df["OVER DUE Category"] = pd.cut(df["OVER DUE"], bins=bins, labels=labels, right=True)
                    overdue_summary = df.groupby("OVER DUE Category").agg(
                        MTXVAL_Sum=("MTXVAL", "sum"),
                        Count=("MTXVAL", "size")
                    ).reset_index()

                    # Plot
                    fig, ax = plt.subplots(figsize=(10, 6))
                    bars = ax.bar(overdue_summary["OVER DUE Category"], overdue_summary["MTXVAL_Sum"])
                    for bar, count, sum_val in zip(bars, overdue_summary["Count"], overdue_summary["MTXVAL_Sum"]):
                        yval = bar.get_height()
                        label = f"Rp{yval:,.0f}\nCount: {count}"
                        ax.text(bar.get_x() + bar.get_width() / 2, yval, label, ha="center", va="bottom", fontsize=9)

                    ax.set_xlabel("OVER DUE Categories")
                    ax.set_ylabel("Sum of MTXVAL")
                    ax.set_title("Sum of MTXVAL for Different OVER DUE Categories")
                    st.pyplot(fig)
                else:
                    st.warning("Columns 'OVER DUE' or 'MTXVAL' are missing in the data.")

        except Exception as e:
            st.error(f"Error: {e}")

def process_edi_file(file):
    if file:
        try:
            if file.name.endswith(".xlsx"):
                df = pd.read_excel(file)
            else:
                df = pd.read_csv(file, delimiter="|", on_bad_lines="skip", low_memory=False)

            if compute_text_to_column_edi:
                st.subheader("Data Rapi (EDI File)")
                st.dataframe(df)

        except Exception as e:
            st.error(f"Error: {e}")

# Results in the main app
st.header("Processing Results")
if uploaded_file_1:
    process_piutang_overdue(uploaded_file_1)
if uploaded_file_2:
    process_edi_file(uploaded_file_2)
if not uploaded_file_1 and not uploaded_file_2:
    st.info("Upload files from the sidebar to see results.")
