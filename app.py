import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

# Streamlit App Title
st.title("📊 Auto Report Processor & Dashboard")

# First Report: Piutang Overdue
st.header("📂 Piutang Overdue Report")

# Checklist for analysis options
piutang_options = st.multiselect(
    "Select the analyses to perform on Piutang Overdue report:",
    options=["Summary of OVER DUE Categories", "Bar Plot Visualization", "Highest & Lowest Values"],
    default=["Summary of OVER DUE Categories", "Bar Plot Visualization"]
)

# File uploader
uploaded_file_1 = st.file_uploader("Upload your .txt or .xlsx Piutang Overdue report file", type=["txt", "xlsx"], key="file1")

# Second Report: EDI File
st.header("📂 EDI File Report")

# Checklist for analysis options
edi_options = st.multiselect(
    "Select the analyses to perform on EDI File report:",
    options=["Summary Statistics", "Data Description", "Custom Analysis"],
    default=["Summary Statistics", "Data Description"]
)

# File uploader
uploaded_file_2 = st.file_uploader("Upload your .txt or .xlsx EDI File report", type=["txt", "xlsx"], key="file2")

# --- Processing the first report (Piutang Overdue) ---
if uploaded_file_1:
    try:
        if uploaded_file_1.name.endswith(".xlsx"):
            df1 = pd.read_excel(uploaded_file_1)
        elif uploaded_file_1.name.endswith(".txt"):
            df1 = pd.read_csv(uploaded_file_1, delimiter="|", on_bad_lines='skip', low_memory=False)

        st.write("### Uploaded Piutang Overdue Report:")
        st.dataframe(df1)

        # 1. Summary of OVER DUE Categories
        if "Summary of OVER DUE Categories" in piutang_options:
            if "OVER DUE" in df1.columns and "MTXVAL" in df1.columns:
                bins = [1, 14, 30, 60, float('inf')]
                labels = ["1-14", "15-30", "31-60", "60+"]
                df1["OVER DUE Category"] = pd.cut(df1["OVER DUE"], bins=bins, labels=labels, right=True)

                overdue_summary = df1.groupby("OVER DUE Category").agg(
                    MTXVAL_Sum=("MTXVAL", "sum"),
                    Count=("MTXVAL", "size")
                ).reset_index()

                total_mtxval_sum = df1["MTXVAL"].sum()
                overdue_summary["MTXVAL_Ratio"] = overdue_summary["MTXVAL_Sum"] / total_mtxval_sum

                st.write("### OVER DUE Categories and Sum of MTXVAL")
                st.dataframe(overdue_summary)

        # 2. Bar Plot Visualization
        if "Bar Plot Visualization" in piutang_options:
            fig, ax = plt.subplots(figsize=(10, 6))
            bars = ax.bar(overdue_summary["OVER DUE Category"], overdue_summary["MTXVAL_Sum"])

            for bar, count, sum_val in zip(bars, overdue_summary["Count"], overdue_summary["MTXVAL_Sum"]):
                yval = bar.get_height()
                formatted_sum = f"Rp{yval:,.0f}"
                label = f"{formatted_sum}\nCount: {count}"
                ax.text(bar.get_x() + bar.get_width() / 2, yval + 50000, label, ha='center', va='bottom', fontsize=10)

            ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, _: f'Rp{x:,.0f}'))
            ax.set_xlabel("OVER DUE Categories")
            ax.set_ylabel("Sum of MTXVAL")
            ax.set_title("Sum of MTXVAL for Different OVER DUE Categories")

            st.pyplot(fig)

        # 3. Highest & Lowest Values
        if "Highest & Lowest Values" in piutang_options:
            numeric_columns = df1.select_dtypes(include=['number']).columns
            if numeric_columns.any():
                selected_column = st.selectbox("Select a numeric column for analysis:", numeric_columns)

                if selected_column:
                    highest_value = df1[selected_column].max()
                    lowest_value = df1[selected_column].min()

                    st.write(f"**Highest Value in {selected_column}:** {highest_value}")
                    st.write(f"**Lowest Value in {selected_column}:** {lowest_value}")

                    st.write("### Detailed View (Editable)")
                    st.dataframe(df1.sort_values(by=selected_column, ascending=False))

# --- Processing the second report (EDI File) ---
if uploaded_file_2:
    try:
        if uploaded_file_2.name.endswith(".xlsx"):
            df2 = pd.read_excel(uploaded_file_2)
        elif uploaded_file_2.name.endswith(".txt"):
            df2 = pd.read_csv(uploaded_file_2, delimiter="|", on_bad_lines='skip', low_memory=False)

        st.write("### Uploaded EDI File Report:")
        st.dataframe(df2)

        # 1. Summary Statistics
        if "Summary Statistics" in edi_options:
            st.write("### Summary Statistics for EDI File:")
            st.dataframe(df2.describe())

        # 2. Data Description
        if "Data Description" in edi_options:
            st.write("### Data Description:")
            st.write(df2.info())

        # 3. Custom Analysis
        if "Custom Analysis" in edi_options:
            st.write("### Custom Analysis for EDI File:")
            st.write("This section can be customized to perform specific analyses for the EDI file.")
            st.dataframe(df2.head())

    except Exception as e:
        st.error(f"An error occurred while processing the EDI File report: {e}")
