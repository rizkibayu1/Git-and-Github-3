import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from io import BytesIO

# Streamlit App Title
st.title("Dashboard Monitoring AOS")

# Tabs for Piutang Overdue and Opname Faktur
tab1, tab2 = st.tabs(["📊 Piutang Overdue", "📋 Opname Faktur"])

# Function to create an Excel file from a DataFrame
def to_excel(df):
    output = BytesIO()
    df.to_excel(output, index=False, engine="openpyxl")
    output.seek(0)
    return output

# Tab 1: Piutang Overdue
with tab1:
    st.header("Piutang Overdue")
    uploaded_file_overdue = st.file_uploader("Upload Piutang Overdue (.txt or .xlsx)", type=["txt", "xlsx"])

    if uploaded_file_overdue:
        try:
            # Read file
            if uploaded_file_overdue.name.endswith(".xlsx"):
                df_overdue = pd.read_excel(uploaded_file_overdue)
            else:
                df_overdue = pd.read_csv(uploaded_file_overdue, delimiter="|", on_bad_lines="skip", low_memory=False)

            # Example transformation (replace with your own processing logic)
            if "MTXVAL" in df_over
