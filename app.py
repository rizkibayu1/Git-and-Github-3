import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from io import BytesIO

# Streamlit App Title
st.title("Dashboard Monitoring AOS")

# Initialize session state for file uploads and checkboxes
if "uploaded_file_overdue" not in st.session_state:
    st.session_state.uploaded_file_overdue = None
if "uploaded_file_opname" not in st.session_state:
    st.session_state.uploaded_file_opname = None
if "process_opname" not in st.session_state:
    st.session_state.process_opname = False

# Tabs for Piutang Overdue and Opname Faktur
tab1, tab2 = st.tabs(["📊 Piutang Overdue", "📋 Opname Faktur"])

# Function to format currency in Indonesian Rupiah format
def format_rupiah(value):
    return f"Rp{value:,.0f}".replace(",", ".")

# Function to create an Excel file from a DataFrame
def to_excel(df):
    output = BytesIO()
    df.to_excel(output, index=False, engine="openpyxl")
    output.seek(0)
    return output

# Tab 1: Piutang Overdue
with tab1:
    st.header("Piutang Overdue")
    st.session_state.uploaded_file_overdue = st.file_uploader(
        "Upload Piutang Overdue (.txt or .xlsx)", type=["txt", "xlsx"], key="file_overdue"
    )

    if st.session_state.uploaded_file_overdue:
        try:
            # Determine file type and read the file
            file = st.session_state.uploaded_file_overdue
            if file.name.endswith(".xlsx"):
                df = pd.read_excel(file)
            else:
                df = pd.read_csv(file, delimiter="|", on_bad_lines="skip", low_memory=False)

            # Clean and format data
            if "MTXVAL" in df.columns:
                df["MTXVAL"] = pd.to_numeric(df["MTXVAL"], errors="coerce").fillna(0)
                df["MTXVAL"] = df["MTXVAL"].apply(format_rupiah)

            st.write("### Tabel Data (Piutang Overdue)")
            st.dataframe(df)

            # Create a summary chart
            if "OVER DUE" in df.columns and "MTXVAL" in df.columns:
                df["MTXVAL_NUMERIC"] = df["MTXVAL"].str.replace(r"[^\d]", "", regex=True).astype(float)

                summary = df.groupby("OVER DUE")["MTXVAL_NUMERIC"].agg(["sum", "count"]).reset_index()
                summary["MTXVAL_NUMERIC"] = summary["sum"].apply(format_rupiah)

                fig = go.Figure()

                # Bar chart for monetary value
                fig.add_trace(
                    go.Bar(
                        x=summary["OVER DUE"],
                        y=summary["sum"],
                        name="Total Nominal (Rp)",
                        text=summary["MTXVAL_NUMERIC"],
                        textposition="auto",
                    )
                )

                # Line chart for count
                fig.add_trace(
                    go.Scatter(
                        x=summary["OVER DUE"],
                        y=summary["count"],
                        name="Count",
                        mode="lines+markers",
                        yaxis="y2",
                    )
                )

                # Configure layout with dual axes
                fig.update_layout(
                    xaxis_title="Kategori Over Due",
                    yaxis=dict(title="Total Nominal (Rp)", titlefont=dict(color="blue")),
                    yaxis2=dict(
                        title="Count",
                        titlefont=dict(color="orange"),
                        overlaying="y",
                        side="right",
                    ),
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5),
                )
                st.write("### Grafik Piutang Overdue")
                st.plotly_chart(fig, use_container_width=True)

            # Download processed data as Excel
            excel_file = to_excel(df)
            st.download_button(
                label="Download as Excel",
                data=excel_file,
                file_name="piutang_overdue.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )
        except Exception as e:
            st.error(f"An unexpected error occurred: {e}")

# Tab 2: Opname Faktur
with tab2:
    st.header("Opname Faktur")
    st.session_state.uploaded_file_opname = st.file_uploader(
        "Upload Opname Faktur (.txt or .xlsx)", type=["txt", "xlsx"], key="file_opname"
    )
    st.session_state.process_opname = st.checkbox("Proses Text to Column (Opname Faktur)")

    if st.session_state.uploaded_file_opname and st.session_state.process_opname:
        try:
            # Determine file type and read the file
            file = st.session_state.uploaded_file_opname
            if file.name.endswith(".xlsx"):
                df = pd.read_excel(file)
            else:
                df = pd.read_csv(file, delimiter="|", on_bad_lines="skip", low_memory=False)

            # Display processed data
            st.write("### Data Rapi (Opname Faktur)")
            st.dataframe(df)

            # Download processed data as Excel
            excel_file = to_excel(df)
            st.download_button(
                label="Download as Excel",
                data=excel_file,
                file_name="opname_faktur.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )
        except Exception as e:
            st.error(f"An unexpected error occurred: {e}")
