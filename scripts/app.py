import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import requests
import zipfile
import csv
import os
import numpy as np

# Ensure the necessary directories exist
os.makedirs('data/raw', exist_ok=True)
os.makedirs('data/processed', exist_ok=True)
os.makedirs('data/historical_stats', exist_ok=True)

frequencies = pd.read_csv('data/historical_stats/numbers_frequency.csv')

@st.cache_data
def load_data():
    try:
        lotto_data = pd.read_csv('data/processed/lotto_historical.csv')
    except (FileNotFoundError, pd.errors.EmptyDataError):
        lotto_data = pd.DataFrame(columns=['date', 'wheel', 'n1', 'n2', 'n3', 'n4', 'n5'])
    
    try:
        most_frequent = pd.read_csv('data/historical_stats/most_frequent.csv')
    except (FileNotFoundError, pd.errors.EmptyDataError):
        most_frequent = pd.DataFrame(columns=['wheel', 'number', 'frequency'])
    
    try:
        least_frequent = pd.read_csv('data/historical_stats/least_frequent.csv')
    except (FileNotFoundError, pd.errors.EmptyDataError):
        least_frequent = pd.DataFrame(columns=['wheel', 'number', 'frequency'])
    
    return lotto_data, most_frequent, least_frequent

lotto_data, most_frequent, least_frequent = load_data()

if not lotto_data.empty:
    lotto_data['date'] = pd.to_datetime(lotto_data['date'])

def refresh_data():
    URL = "https://www.igt.it/STORICO_ESTRAZIONI_LOTTO/storico01-oggi.zip"
    response = requests.get(URL)
    with open("data/raw/lotto_historical.zip", "wb") as f:
        f.write(response.content)

    with zipfile.ZipFile("data/raw/lotto_historical.zip", 'r') as zip_ref:
        zip_ref.extractall("data/raw/")
    
    input_file = "data/raw/storico01-oggi.txt"
    output_file = "data/processed/lotto_historical.csv"

    with open(input_file, "r") as txt_file, open(output_file, "w", newline='') as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow(["date", "wheel", "n1", "n2", "n3", "n4", "n5"])
        
        for line in txt_file:
            parts = line.strip().split("\t")
            if parts[1] == "NA":
                parts[1] = "NAT"
            csv_writer.writerow(parts)
    
    # Clear cache to load new data
    st.cache_data.clear()

def main():
    st.title('Lotto Draws Visualizer')
    
    # Sidebar menu
    st.sidebar.title("Menu")
    if st.sidebar.button('Refresh Data'):
        refresh_data()
        st.sidebar.success("Data refreshed successfully!")
    
    option = st.sidebar.radio("Choose an option:", 
                              ("View Draws by Date", "Most/Least Frequent Numbers", "Number Grid Analysis"))
    
    if option == "View Draws by Date":
        if lotto_data.empty:
            st.warning("No data available. Please refresh the data.")
            return
        
        available_dates = lotto_data['date'].dt.date.unique()
        available_years = sorted(list({date.year for date in available_dates}))
        available_months = sorted(list({date.month for date in available_dates}))
        available_days = sorted(list({date.day for date in available_dates}))
        
        last_date = available_dates[-1]
        default_year = last_date.year
        default_month = last_date.month
        default_day = last_date.day
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            selected_year = st.selectbox('Select Year', available_years, index=available_years.index(default_year))
        
        with col2:
            selected_month = st.selectbox('Select Month', available_months, index=available_months.index(default_month))
        
        with col3:
            selected_day = st.selectbox('Select Day', available_days, index=available_days.index(default_day))
        
        selected_date = pd.to_datetime(f"{selected_year}/{selected_month}/{selected_day}").date()
        filtered_data = lotto_data[lotto_data['date'].dt.date == selected_date]
        
        if not filtered_data.empty:
            st.write(f"Numbers drawn on {selected_date}:")
            st.dataframe(filtered_data[['wheel', 'n1', 'n2', 'n3', 'n4', 'n5']], use_container_width=True)
        else:
            st.warning("No draws found for the selected date.")
    
    elif option == "Most/Least Frequent Numbers":
        if most_frequent.empty or least_frequent.empty:
            st.warning("No frequency data available. Please refresh the data.")
            return

        st.write("Most/Least Frequent Numbers (last 100 extractions):")

        wheels = most_frequent['wheel'].unique()
        
        selected_wheel = st.selectbox("Select Wheel", wheels)
        
        st.write(f"Frequency histogram for wheel **{selected_wheel}**:")
        
        wheel_frequencies = frequencies[frequencies['wheel'] == selected_wheel]
        
        freq_dict = dict(zip(wheel_frequencies['number'], wheel_frequencies['frequency']))
        
        all_numbers = range(1, 91)
        all_frequencies = [freq_dict.get(num, 0) for num in all_numbers]
        
        fig, ax = plt.subplots()
        ax.bar(all_numbers, all_frequencies, color='skyblue')
        ax.set_xlabel('Number')
        ax.set_ylabel('Frequency')
        ax.set_title(f'Frequency of Numbers for Wheel {selected_wheel}')
        ax.set_xticks(range(1, 91, 5))
        ax.grid(axis='y', linestyle='--', alpha=0.7)
        
        st.pyplot(fig)
        
        # Most Frequent Numbers
        st.write(f"Most frequent numbers for wheel **{selected_wheel}**:")
        
        most_wheel_data = most_frequent[most_frequent['wheel'] == selected_wheel]
        
        cols = st.columns(5)
        for idx, (_, row) in enumerate(most_wheel_data.iterrows()):
            with cols[idx % 5]:  
                st.markdown(f"**Number {row['number']}**")
                st.write(f"Frequency: {row['frequency']}")
        
        # Least Frequent Numbers
        st.write(f"Least frequent numbers for wheel **{selected_wheel}**:")
        
        least_wheel_data = least_frequent[least_frequent['wheel'] == selected_wheel]
        
        cols = st.columns(5)
        for idx, (_, row) in enumerate(least_wheel_data.iterrows()):
            with cols[idx % 5]:  
                st.markdown(f"**Number {row['number']}**")
                st.write(f"Frequency: {row['frequency']}")
        
        # Last N Draws
        st.write(f"Last draws for wheel **{selected_wheel}**:")
        
        num_draws = st.slider("Select number of last draws to display", min_value=1, max_value=10, value=3)
        
        last_draws = lotto_data[lotto_data['wheel'] == selected_wheel].sort_values(by='date', ascending=False).head(num_draws)
        
        if not last_draws.empty:
            st.write("### Last Draws")
            
            most_frequent_numbers = most_frequent[most_frequent['wheel'] == selected_wheel]['number'].tolist()
            least_frequent_numbers = least_frequent[least_frequent['wheel'] == selected_wheel]['number'].tolist()

            def highlight_frequent(val):
                if val in most_frequent_numbers:
                    return f"{val}*"
                if val in least_frequent_numbers:
                    return f"{val}**"
                return val
            
            last_draws = last_draws[['date', 'n1', 'n2', 'n3', 'n4', 'n5']].rename(columns={
            'date': 'Date',
            'n1': 'Number 1',
            'n2': 'Number 2',
            'n3': 'Number 3',
            'n4': 'Number 4',
            'n5': 'Number 5'
            })
            
            last_draws = last_draws.applymap(highlight_frequent)
            
            st.table(last_draws)
        else:
            st.warning("No draws found for the selected wheel.")

    elif option == "Number Grid Analysis":
        if lotto_data.empty or most_frequent.empty or least_frequent.empty:
            st.warning("No data available. Please refresh the data.")
            return
        
        st.write("## Number Grid Analysis")
        
        wheels = lotto_data['wheel'].unique()
        selected_wheel = st.selectbox("Select Wheel", wheels, key="grid_wheel_selector")
        
        # Get the last 10 draws for the selected wheel
        last_10_draws = lotto_data[lotto_data['wheel'] == selected_wheel].sort_values(by='date', ascending=False).head(10)
        
        # Collect all drawn numbers from the last 10 extractions
        recent_numbers = []
        for col in ['n1', 'n2', 'n3', 'n4', 'n5']:
            recent_numbers.extend(last_10_draws[col].tolist())
        recent_numbers = [int(n) for n in recent_numbers]
        
        # Get the 10 most frequent numbers for the wheel
        top_10_frequent = most_frequent[most_frequent['wheel'] == selected_wheel].head(10)['number'].tolist()
        top_10_frequent = [int(n) for n in top_10_frequent]
        
        # Get the 10 least frequent numbers for the wheel
        bottom_10_frequent = least_frequent[least_frequent['wheel'] == selected_wheel].head(10)['number'].tolist()
        bottom_10_frequent = [int(n) for n in bottom_10_frequent]
        
        # Color definitions - using a more harmonious palette for lottery visualization
        colors = {
            'neutral': '#f5f5f5',  # Light gray for neutral numbers
            'recent': '#4caf50',   # Green for recently drawn numbers
            'most_freq': '#1e88e5', # Blue for most frequent numbers
            'least_freq': '#f44336', # Red for least frequent numbers
            'recent_most': '#8bc34a',  # Light green for recent + most frequent
            'recent_least': '#ff9800', # Orange for recent + least frequent
            'text_dark': '#212121',   # Dark text for light backgrounds
            'text_light': '#ffffff'   # Light text for dark backgrounds
        }
        
        # Create a grid of numbers from 1 to 90
        st.write(f"### Number Grid for Wheel {selected_wheel}")
        
        # Legend with colored boxes
        st.write("### Legend:")
        legend_col1, legend_col2, legend_col3 = st.columns(3)
        
        with legend_col1:
            st.markdown(f"""
            <div style='display:flex;align-items:center;margin-bottom:10px'>
                <div style='background-color:{colors["recent"]};width:20px;height:20px;margin-right:10px'></div>
                <div>Recently drawn (last 10 extractions)</div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown(f"""
            <div style='display:flex;align-items:center;margin-bottom:10px'>
                <div style='background-color:{colors["recent_most"]};width:20px;height:20px;margin-right:10px'></div>
                <div>Recently drawn + Most frequent</div>
            </div>
            """, unsafe_allow_html=True)
        
        with legend_col2:
            st.markdown(f"""
            <div style='display:flex;align-items:center;margin-bottom:10px'>
                <div style='background-color:{colors["most_freq"]};width:20px;height:20px;margin-right:10px'></div>
                <div>Most frequent numbers</div>
            </div>
            
            <div style='display:flex;align-items:center;margin-bottom:10px'>
                <div style='background-color:{colors["recent_least"]};width:20px;height:20px;margin-right:10px'></div>
                <div>Recently drawn + Least frequent</div>
            </div>
            """, unsafe_allow_html=True)
            
        with legend_col3:
            st.markdown(f"""
            <div style='display:flex;align-items:center;margin-bottom:10px'>
                <div style='background-color:{colors["least_freq"]};width:20px;height:20px;margin-right:10px'></div>
                <div>Least frequent numbers</div>
            </div>
            
            <div style='display:flex;align-items:center;margin-bottom:10px'>
                <div style='background-color:{colors["neutral"]};width:20px;height:20px;margin-right:10px'></div>
                <div>Other numbers</div>
            </div>
            """, unsafe_allow_html=True)
        
        # Create the grid with 9 rows and 10 columns
        grid_rows = 9
        grid_cols = 10
        
        for i in range(grid_rows):
            cols = st.columns(grid_cols)
            for j in range(grid_cols):
                number = i * grid_cols + j + 1
                if number <= 90:
                    # Determine cell color and content based on the number's characteristics
                    is_recent = number in recent_numbers
                    is_most_frequent = number in top_10_frequent
                    is_least_frequent = number in bottom_10_frequent
                    
                    bg_color = colors['neutral']  # Default color
                    text_color = colors['text_dark']  # Default text color
                    symbol = ""
                    
                    # Determine the color based on the combination of conditions
                    if is_recent and is_most_frequent:
                        bg_color = colors['recent_most']
                        text_color = colors['text_dark']
                        symbol = "*"
                    elif is_recent and is_least_frequent:
                        bg_color = colors['recent_least']
                        text_color = colors['text_dark']
                        symbol = "†"
                    elif is_recent:
                        bg_color = colors['recent']
                        text_color = colors['text_light']
                    elif is_most_frequent:
                        bg_color = colors['most_freq']
                        text_color = colors['text_light']
                    elif is_least_frequent:
                        bg_color = colors['least_freq']
                        text_color = colors['text_light']
                    
                    # Create the cell with appropriate styling
                    cols[j].markdown(
                        f"<div style='background-color:{bg_color};color:{text_color};padding:10px;text-align:center;border-radius:4px;font-weight:bold;'>{number}{symbol}</div>",
                        unsafe_allow_html=True
                    )

if __name__ == '__main__':
    main()