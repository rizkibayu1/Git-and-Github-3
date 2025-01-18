import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Helper Functions
def process_file(file):
    try:
        if file.name.endswith('.txt'):
            df = pd.read_csv(file, delimiter="\t")  # Default to tab-separated
        elif file.name.endswith('.xlsx'):
            df = pd.read_excel(file)
        else:
            st.error("Unsupported file type. Please upload a .txt or .xlsx file.")
            return None
    except Exception as e:
        st.error(f"Error processing file: {e}")
        return None
    return df

def generate_chart(df, column_name):
    if column_name not in df.columns:
        st.error(f"Column '{column_name}' not found in the dataset.")
        return None
    fig, ax = plt.subplots()
    df[column_name].value_counts().plot(kind='bar', ax=ax)
    ax.set_title(f"Chart for {column_name}")
    return fig

# Streamlit App
st.title("Multi-File Processing App")
st.sidebar.header("Upload Files")

# Session State Initialization
if "uploaded_files" not in st.session_state:
    st.session_state.uploaded_files = {"file_1": None, "file_2": None}
if "results_state" not in st.session_state:
    st.session_state.results_state = {"file_1": {}, "file_2": {}}

# File Upload Section
st.sidebar.subheader("File 1")
file_1 = st.sidebar.file_uploader("Upload File 1", type=["txt", "xlsx"], key="file_1")
if file_1:
    st.session_state.uploaded_files["file_1"] = file_1

st.sidebar.subheader("File 2")
file_2 = st.sidebar.file_uploader("Upload File 2", type=["txt", "xlsx"], key="file_2")
if file_2:
    st.session_state.uploaded_files["file_2"] = file_2

# Processing Files
for file_key in ["file_1", "file_2"]:
    file = st.session_state.uploaded_files[file_key]
    if file:
        if "df" not in st.session_state.results_state[file_key]:
            df = process_file(file)
            if df is not None:
                st.session_state.results_state[file_key]["df"] = df

# Display Results for Each File
for file_key, file_label in [("file_1", "File 1"), ("file_2", "File 2")]:
    df = st.session_state.results_state[file_key].get("df")
    if df is not None:
        st.write(f"### {file_label} Results")

        # Checkbox Options
        data_display = st.checkbox(f"Show Processed Data ({file_label})", key=f"{file_key}_data_display")
        table_display = st.checkbox(f"Show Data Table ({file_label})", key=f"{file_key}_table_display")
        chart_display = st.checkbox(f"Show Chart ({file_label})", key=f"{file_key}_chart_display")

        if data_display:
            st.write(f"#### Processed Data for {file_label}")
            st.write(df.head())

        if table_display:
            st.write(f"#### Full Data Table for {file_label}")
            st.dataframe(df)

        if chart_display:
            st.write(f"#### Generate Chart for {file_label}")
            column_name = st.selectbox(f"Select column for chart ({file_label})", df.columns, key=f"{file_key}_chart_column")
            if column_name:
                chart = generate_chart(df, column_name)
                if chart:
                    st.pyplot(chart)
