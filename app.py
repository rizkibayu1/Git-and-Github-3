import pandas as pd
import streamlit as st
import plotly.graph_objects as go
from io import BytesIO

# Helper function to format numbers as Rupiah
def format_rupiah(value):
    try:
        return f"Rp{value:,.0f}".replace(",", ".")
    except (ValueError, TypeError):
        return "Rp0"

# Helper function to convert dataframe to Excel
def to_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False, sheet_name="Sheet1")
        writer.save()
    return output.getvalue()

# Streamlit app
st.title("Dashboard Monitoring AOS")

# Tab layout
tab1, tab2 = st.tabs(["Piutang Overdue", "Opname Faktur"])

# Tab 1: Piutang Overdue
with tab1:
    st.header("Piutang Overdue")
    st.session_state.uploaded_file_overdue = st.file_uploader(
        "Upload Piutang Overdue (.txt or .xlsx)", type=["txt", "xlsx"], key="file_overdue"
    )

    process_options = {
        "Data Rapi": st.checkbox("Data Rapi"),
        "Tabel": st.checkbox("Tabel"),
        "Grafik": st.checkbox("Grafik"),
    }

    if st.session_state.uploaded_file_overdue:
        try:
            # Determine file type and read the file
            file = st.session_state.uploaded_file_overdue
            if file.name.endswith(".xlsx"):
                df = pd.read_excel(file)
            else:
                df = pd.read_csv(file, delimiter="|", on_bad_lines="skip", low_memory=False)

            # Data Rapi
            if process_options["Data Rapi"]:
                if "MTXVAL" in df.columns:
                    df["MTXVAL"] = df["MTXVAL"].astype(str).str.replace(r"[^\d]", "", regex=True)
                    df["MTXVAL"] = pd.to_numeric(df["MTXVAL"], errors="coerce").fillna(0)
                    df["MTXVAL"] = df["MTXVAL"].apply(format_rupiah)
                if "TGL INVOICE" in df.columns:
                    df["TGL INVOICE"] = pd.to_datetime(df["TGL INVOICE"], format="%Y%m%d", errors="coerce").dt.strftime("%d-%m-%Y")
                if "TGL JATUH TEMPO" in df.columns:
                    df["TGL JATUH TEMPO"] = pd.to_datetime(df["TGL JATUH TEMPO"], format="%Y%m%d", errors="coerce").dt.strftime("%d-%m-%Y")
                st.write("### Data Rapi")
                st.dataframe(df)

                # Download processed data
                excel_file = to_excel(df)
                st.download_button(
                    label="Download Data Rapi as Excel",
                    data=excel_file,
                    file_name="piutang_overdue_data_rapi.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                )

            # Tabel
            if process_options["Tabel"]:
                st.write("### Tabel Data (Piutang Overdue)")
                st.dataframe(df)

            # Grafik
            if process_options["Grafik"] and "OVER DUE" in df.columns and "MTXVAL" in df.columns:
                df["MTXVAL_NUMERIC"] = df["MTXVAL"].str.replace(r"[^\d]", "", regex=True).astype(float)

                summary = df.groupby("OVER DUE")["MTXVAL_NUMERIC"].agg(["sum", "count"]).reset_index()
                summary["MTXVAL_FORMATTED"] = summary["sum"].apply(format_rupiah)

                fig = go.Figure()

                # Bar chart for monetary value
                fig.add_trace(
                    go.Bar(
                        x=summary["OVER DUE"],
                        y=summary["sum"],
                        name="Total Nominal (Rp)",
                        text=summary["MTXVAL_FORMATTED"],
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

        except Exception as e:
            st.error(f"An unexpected error occurred: {e}")

# Tab 2: Opname Faktur
with tab2:
    st.header("Opname Faktur")
    st.session_state.uploaded_file_opname = st.file_uploader(
        "Upload Opname Faktur (.txt)", type=["txt"], key="file_opname"
    )

    if st.session_state.uploaded_file_opname:
        try:
            file = st.session_state.uploaded_file_opname
            df = pd.read_csv(file, delimiter="|", on_bad_lines="skip", low_memory=False)

            st.write("### Data Opname Faktur (Text to Column)")
            st.dataframe(df)

            # Download processed data
            excel_file = to_excel(df)
            st.download_button(
                label="Download Opname Faktur as Excel",
                data=excel_file,
                file_name="opname_faktur.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )

        except Exception as e:
            st.error(f"An unexpected error occurred: {e}")
