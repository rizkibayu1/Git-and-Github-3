import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from io import BytesIO

# Streamlit App Title
st.title("📊 Auto Report Processor & Dashboard")

# Initialize session state for file uploads and checkboxes
if "uploaded_file_overdue" not in st.session_state:
    st.session_state.uploaded_file_overdue = None
if "uploaded_file_opname" not in st.session_state:
    st.session_state.uploaded_file_opname = None
if "process_overdue_data" not in st.session_state:
    st.session_state.process_overdue_data = False
if "process_overdue_table" not in st.session_state:
    st.session_state.process_overdue_table = False
if "process_overdue_chart" not in st.session_state:
    st.session_state.process_overdue_chart = False
if "process_opname_data" not in st.session_state:
    st.session_state.process_opname_data = False

# Function to create Excel file from DataFrame
def to_excel(df):
    output = BytesIO()
    df.to_excel(output, index=False, engine="openpyxl")
    output.seek(0)
    return output

# Function to process Piutang Overdue
def process_piutang_overdue(file):
    if file:
        try:
            if file.name.endswith(".xlsx"):
                df = pd.read_excel(file)
            else:
                df = pd.read_csv(file, delimiter="|", on_bad_lines="skip", low_memory=False)

            # Data Rapi
            if st.session_state.process_overdue_data:
                st.write("### Data Rapi (Piutang Overdue)")
                st.dataframe(df)
                excel_file = to_excel(df)
                st.download_button(
                    label="Download Data Rapi (Piutang Overdue)",
                    data=excel_file,
                    file_name="data_rapi_piutang_overdue.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                )

            # Tabel Overdue
            if st.session_state.process_overdue_table:
                st.write("### Tabel Over Due")
                if "OVER DUE" in df.columns and "MTXVAL" in df.columns:
                    bins = [1, 14, 30, 60, float("inf")]
                    labels = ["1-14", "15-30", "31-60", "60+"]
                    df["OVER DUE Category"] = pd.cut(df["OVER DUE"], bins=bins, labels=labels, right=True)

                    overdue_summary = df.groupby("OVER DUE Category").agg(
                        MTXVAL_Sum=("MTXVAL", "sum"), Count=("MTXVAL", "size")
                    ).reset_index()

                    st.dataframe(overdue_summary)
                    excel_file = to_excel(overdue_summary)
                    st.download_button(
                        label="Download Tabel Over Due",
                        data=excel_file,
                        file_name="tabel_overdue.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    )
                else:
                    st.warning("The required columns 'OVER DUE' or 'MTXVAL' are missing in the data.")

            # Grafik Overdue
            if st.session_state.process_overdue_chart:
                st.write("### Grafik Over Due")
                if "OVER DUE" in df.columns and "MTXVAL" in df.columns:
                    bins = [1, 14, 30, 60, float("inf")]
                    labels = ["1-14", "15-30", "31-60", "60+"]
                    df["OVER DUE Category"] = pd.cut(df["OVER DUE"], bins=bins, labels=labels, right=True)

                    overdue_summary = df.groupby("OVER DUE Category").agg(
                        MTXVAL_Sum=("MTXVAL", "sum"), Count=("MTXVAL", "size")
                    ).reset_index()

                    # Interactive Plotly chart
                    fig = go.Figure()
                    fig.add_trace(
                        go.Bar(
                            x=overdue_summary["OVER DUE Category"],
                            y=overdue_summary["MTXVAL_Sum"],
                            text=overdue_summary["Count"],
                            texttemplate="%{y:,.0f}<br>Count: %{text}",
                            textposition="outside",
                            marker=dict(color="skyblue"),
                        )
                    )
                    fig.update_layout(
                        title="Grafik Over Due",
                        xaxis_title="OVER DUE Categories",
                        yaxis_title="Sum of MTXVAL",
                        yaxis=dict(tickprefix="Rp", tickformat=",.0f"),
                        template="plotly_white",
                    )

                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.warning("The required columns 'OVER DUE' or 'MTXVAL' are missing in the data.")

        except Exception as e:
            st.error(f"An unexpected error occurred: {e}")

# Function to process Opname Faktur
def process_opname_faktur(file):
    if file:
        try:
            if file.name.endswith(".xlsx"):
                df = pd.read_excel(file)
            else:
                df = pd.read_csv(file, delimiter="|", on_bad_lines="skip", low_memory=False)

            if st.session_state.process_opname_data:
                st.write("### Data Rapi (Opname Faktur)")
                st.dataframe(df)
                excel_file = to_excel(df)
                st.download_button(
                    label="Download Data Rapi (Opname Faktur)",
                    data=excel_file,
                    file_name="data_rapi_opname_faktur.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                )

        except Exception as e:
            st.error(f"An unexpected error occurred: {e}")

# Tabs for UI
tab1, tab2 = st.tabs(["Piutang Overdue", "Opname Faktur"])

# Tab 1: Piutang Overdue
with tab1:
    st.header("Piutang Overdue")
    st.session_state.uploaded_file_overdue = st.file_uploader(
        "Upload Piutang Overdue Report (.txt or .xlsx)", type=["txt", "xlsx"]
    )
    st.session_state.process_overdue_data = st.checkbox("Data Rapi (Piutang Overdue)")
    st.session_state.process_overdue_table = st.checkbox("Tabel Over Due")
    st.session_state.process_overdue_chart = st.checkbox("Grafik Over Due")
    process_piutang_overdue(st.session_state.uploaded_file_overdue)

# Tab 2: Opname Faktur
with tab2:
    st.header("Opname Faktur")
    st.session_state.uploaded_file_opname = st.file_uploader(
        "Upload Opname Faktur (.txt or .xlsx)", type=["txt", "xlsx"]
    )
    st.session_state.process_opname_data = st.checkbox("Delimited '|' (Opname Faktur)")
    process_opname_faktur(st.session_state.uploaded_file_opname)
