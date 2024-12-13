import pandas as pd
import os
import streamlit as st
import plotly.express as px

# Specify the main folder path
main_folder = "C:/Users/ericf/OneDrive - Bentley University/pythonProject/pythonProject1/industries"

# Get a list of subfolders (industries)
subfolders = [f.name for f in os.scandir(main_folder) if f.is_dir()]

# Streamlit App Title
st.title("Industry Data Dashboard")

# Sidebar for industry selection
st.sidebar.title("Industry Navigation")
selected_industry = st.sidebar.radio("Select an Industry:", subfolders)

if selected_industry:
    folder_path = os.path.join(main_folder, selected_industry)
    st.title(f"Data for {selected_industry.capitalize()} Industry")

    # Initialize an empty DataFrame to store data from all files for the charts
    all_data = pd.DataFrame()

    # Process each CSV file in the selected subfolder
    for file_name in os.listdir(folder_path):
        if file_name.endswith(".csv"):
            # Extract the year from the file name (assuming year is part of the file name)
            year = file_name.split(".")[0]  # Adjust this split logic based on your file naming convention

            # Load the data
            file_path = os.path.join(folder_path, file_name)
            data = pd.read_csv(file_path)

            # Filter the data for the required conditions
            filtered_data = data[
                (data["area_title"] == "U.S. TOTAL") & (data["own_title"] == "Private")
            ]

            # Retain only the required columns and add the year
            for column in ["annual_avg_wkly_wage", "avg_annual_pay", "annual_avg_emplvl"]:
                if column in filtered_data.columns:
                    temp_df = filtered_data[[column]].copy()
                    temp_df["Year"] = int(year)
                    temp_df["Metric"] = column
                    temp_df.rename(columns={column: "Value"}, inplace=True)
                    all_data = pd.concat([all_data, temp_df])

    # Ensure the data is sorted by year for the charts
    if not all_data.empty:
        all_data["Year"] = all_data["Year"].astype(int)
        all_data = all_data.sort_values(by="Year")

        # Calculate YoY percentage change
        all_data["YoY Change (%)"] = all_data.groupby("Metric")["Value"].pct_change() * 100

        # Create charts for each metric
        for metric in ["annual_avg_wkly_wage", "avg_annual_pay", "annual_avg_emplvl"]:
            metric_data = all_data[all_data["Metric"] == metric]

            # Create an interactive line chart using Plotly
            st.subheader(f"Change in {metric.replace('_', ' ').title()} Over Years")
            fig = px.line(
                metric_data,
                x="Year",
                y="Value",
                markers=True,
                title=f"{metric.replace('_', ' ').title()} Over Years for {selected_industry.capitalize()}",
                labels={"Value": metric.replace('_', ' ').title(), "Year": "Year"}
            )

            # Add hover tooltips with YoY Change
            fig.update_traces(
                hovertemplate=(
                    "Year: %{x}<br>"
                    "Value: %{y:.2f}<br>"
                    "Year over Year Change: %{customdata[0]:.2f}%"
                ),
                customdata=metric_data[["YoY Change (%)"]]
            )
            fig.update_layout(hovermode="x unified")

            # Display the interactive chart in Streamlit
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning(f"No data available for the {selected_industry.capitalize()} industry.")
