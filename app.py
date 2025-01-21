import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from io import BytesIO

# Streamlit App Title
st.title("📊 Auto Report Processor & Dashboard")

# Initialize session state for file uploads and checkboxes
for key in [
    "uploaded_file_piutang", "compute_text_to_column_overdue", 
    "compute_overdue_table", "compute_overdue_chart"
]:
    if key not in st.session_state:
        st.session_state[key] = None if key.startswith("uploaded_file") else False

# Function to create Excel file from DataFrame
def to_excel(df):
    output = BytesIO()
    df.to_excel(output, index=False, engine="openpyxl")
    output.seek(0)
    return output

# Function to format numbers as monetary values (e.g., Rp5,000)
def format_as_rupiah(value):
    try:
        return f"Rp{value:,.0f}".replace(",", ".")
    except ValueError:
        return value

# Function to process Piutang Overdue report
def process_piutang_overdue(file):
    if file:
        try:
            # Read file (supports .xlsx and .txt)
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

                    # Format MTXVAL as Rupiah
                    overdue_summary["MTXVAL_Sum"] = overdue_summary["MTXVAL_Sum"].apply(format_as_rupiah)
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

                    # Ensure MTXVAL remains numeric for the chart
                    overdue_summary["MTXVAL_Sum_Numeric"] = overdue_summary["MTXVAL_Sum"].apply(
                        lambda x: float(x.replace("Rp", "").replace(".", "")) if isinstance(x, str) else x
                    )

                    # Interactive Dual-Axis Chart with Plotly
                    fig = go.Figure()

                    # Bar chart for MTXVAL
                    fig.add_trace(go.Bar(
                        x=overdue_summary["OVER DUE Category"],
                        y=overdue_summary["MTXVAL_Sum_Numeric"],
                        name="MTXVAL Sum",
                        marker_color="blue",
                        text=overdue_summary["MTXVAL_Sum"],
                        textposition="outside",
                        hovertemplate="MTXVAL Sum: %{y}<extra></extra>",
                    ))

                    # Line chart for Count
                    fig.add_trace(go.Scatter(
                        x=overdue_summary["OVER DUE Category"],
                        y=overdue_summary["Count"],
                        name="Count",
                        mode="lines+markers+text",
                        text=overdue_summary["Count"],
                        textposition="top center",
                        marker=dict(color="red", size=10),
                        hovertemplate="Count: %{y}<extra></extra>",
                        yaxis="y2",  # Secondary y-axis for the Count line
                    ))

                    # Update layout for dual-axis chart
                    fig.update_layout(
                        title="Sum of MTXVAL and Count for Different OVER DUE Categories",
                        xaxis_title="OVER DUE Category",
                        yaxis_title="MTXVAL Sum (Rp)",
                        yaxis2=dict(
                            title="Count",
                            overlaying="y",
                            side="right",
                            showgrid=False,
                        ),
                        legend_title="Legend",
                        yaxis=dict(tickprefix="Rp"),
                        template="plotly_white",
                        hovermode="x unified",
                    )

                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.warning(
                        "The required columns 'OVER DUE' or 'MTXVAL' are missing in the data."
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
