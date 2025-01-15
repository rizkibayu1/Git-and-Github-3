import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

# Streamlit App Title
st.title("📊 Auto Report Processor & Dashboard")

# File Upload Section
uploaded_file = st.file_uploader("Upload your .txt or .xlsx report file", type=["txt", "xlsx"])

if uploaded_file:
    try:
        # Process XLSX Files
        if uploaded_file.name.endswith(".xlsx"):
            df = pd.read_excel(uploaded_file)
            st.write("### Uploaded Excel File:")
            st.dataframe(df)

        # Process TXT Files
        elif uploaded_file.name.endswith(".txt"):
            df = pd.read_csv(uploaded_file, delimiter="|", on_bad_lines='skip', low_memory=False)
            st.write("### Uploaded Text File:")
            st.dataframe(df)

        # Check for "OVER DUE" and "MTXVAL" columns
        if "OVER DUE" in df.columns and "MTXVAL" in df.columns:
            # Categorize "OVER DUE" column without the 0 category
            bins = [1, 14, 30, 60, float('inf')]  # Define bin edges
            labels = ["1-14", "15-30", "31-60", "60+"]  # Define labels for the bins
            df["OVER DUE Category"] = pd.cut(df["OVER DUE"], bins=bins, labels=labels, right=True)

            # Group by the new category, sum "MTXVAL", and count the rows in each category
            overdue_summary = df.groupby("OVER DUE Category").agg(
                MTXVAL_Sum=("MTXVAL", "sum"),
                Count=("MTXVAL", "size")
            ).reset_index()

            # Calculate the total sum of MTXVAL for the entire dataset
            total_mtxval_sum = df["MTXVAL"].sum()

            # Calculate the ratio of each category's MTXVAL sum over the total sum
            overdue_summary["MTXVAL_Ratio"] = overdue_summary["MTXVAL_Sum"] / total_mtxval_sum

            # Display the result
            st.write("### OVER DUE Categories and Sum of MTXVAL")
            st.dataframe(overdue_summary)

            # Visualization: Bar Plot of OVER DUE Categories vs Sum of MTXVAL
            fig, ax = plt.subplots(figsize=(10, 6))  # Increased width of the chart

            # Bar plot for MTXVAL sum
            bars = ax.bar(overdue_summary["OVER DUE Category"], overdue_summary["MTXVAL_Sum"])

            # Add labels on top of each bar
            for bar, count, sum_val in zip(bars, overdue_summary["Count"], overdue_summary["MTXVAL_Sum"]):
                yval = bar.get_height()
                # Format the sum as Rp (Rupiah)
                formatted_sum = f"Rp{yval:,.0f}"
                label = f"{formatted_sum}\nCount: {count}"
                ax.text(bar.get_x() + bar.get_width() / 2, yval + 50000, label, ha='center', va='bottom', fontsize=10)

            # Format y-axis as currency
            ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, _: f'Rp{x:,.0f}'))

            # Labels and title
            ax.set_xlabel("OVER DUE Categories")
            ax.set_ylabel("Sum of MTXVAL")
            ax.set_title("Sum of MTXVAL for Different OVER DUE Categories")

            # Show the plot
            st.pyplot(fig)

            # Display the ratio of each category's MTXVAL sum over the total
            st.write("### Ratio of MTXVAL Sum for Each Category Over Total MTXVAL")
            overdue_summary["MTXVAL_Ratio"] = overdue_summary["MTXVAL_Ratio"].apply(lambda x: f"{x * 100:.2f}%")
            st.dataframe(overdue_summary[["OVER DUE Category", "MTXVAL_Ratio"]])

        else:
            st.warning("The required columns 'OVER DUE' or 'MTXVAL' are missing in the data.")

        # Highest & Lowest Values Section
        st.write("## 🔍 Analysis: Highest & Lowest Values")
        numeric_columns = df.select_dtypes(include=['number']).columns

        if numeric_columns.any():
            selected_column = st.selectbox("Select a numeric column for analysis:", numeric_columns)

            if selected_column:
                highest_value = df[selected_column].max()
                lowest_value = df[selected_column].min()

                st.write(f"**Highest Value in {selected_column}:** {highest_value}")
                st.write(f"**Lowest Value in {selected_column}:** {lowest_value}")

                st.write("### Detailed View (Editable)")
                st.dataframe(df.sort_values(by=selected_column, ascending=False))
        else:
            st.warning("No numeric columns found for analysis. Please upload a file with numeric data.")

        # Pivot Table-like Interaction
        st.write("## 📝 Interactive Table (Pivot-like)")

        try:
            editable_df = st.data_editor(df)
            st.write("### Updated Table:")
            st.dataframe(editable_df)
        except Exception as e:
            st.error(f"Error updating table: {e}")

    except pd.errors.ParserError as e:
        st.error(f"Error reading file: {e}")
    except Exception as e:
        st.error(f"An unexpected error occurred: {e}")
