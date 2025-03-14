import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import requests
import zipfile
import csv
import os
import numpy as np

st.set_page_config(layout="wide", page_title="Lotto Predictor", page_icon="🎡")

os.makedirs('data/raw', exist_ok=True)
os.makedirs('data/processed', exist_ok=True)
os.makedirs('data/historical_stats', exist_ok=True)

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
    
    try:
        frequencies = pd.read_csv('data/historical_stats/numbers_frequency.csv')
    except (FileNotFoundError, pd.errors.EmptyDataError):
        frequencies = pd.DataFrame(columns=['wheel', 'number', 'frequency'])
    
    return lotto_data, most_frequent, least_frequent, frequencies

lotto_data, most_frequent, least_frequent, frequencies = load_data()

if not lotto_data.empty:
    lotto_data['date'] = pd.to_datetime(lotto_data['date'])

def calculate_frequencies():
    last_100_extractions = lotto_data.groupby('wheel').tail(100)
    calculated_frequencies = last_100_extractions.melt(
        id_vars=['wheel'], 
        value_vars=['n1', 'n2', 'n3', 'n4', 'n5'],
        var_name='num_pos', 
        value_name='number'
    ).groupby(['wheel', 'number']).size().reset_index(name='frequency')
    
    calculated_most_frequent = calculated_frequencies.groupby('wheel').apply(
        lambda x: x.nlargest(10, 'frequency')
    ).reset_index(drop=True)
    
    calculated_least_frequent = calculated_frequencies.groupby('wheel').apply(
        lambda x: x.nsmallest(10, 'frequency')
    ).reset_index(drop=True)
    
    calculated_most_frequent.to_csv('data/historical_stats/most_frequent.csv', index=False)
    calculated_least_frequent.to_csv('data/historical_stats/least_frequent.csv', index=False)
    calculated_frequencies.to_csv('data/historical_stats/numbers_frequency.csv', index=False)
    
    return calculated_frequencies, calculated_most_frequent, calculated_least_frequent

def calculate_delays():
    today = pd.Timestamp.now().floor('D')
    delays = {}
    
    for wheel in lotto_data['wheel'].unique():
        wheel_data = lotto_data[lotto_data['wheel'] == wheel].sort_values('date', ascending=False)
        wheel_delays = {}
        
        for number in range(1, 91):
            for _, row in wheel_data.iterrows():
                if number in [row['n1'], row['n2'], row['n3'], row['n4'], row['n5']]:
                    last_date = row['date']
                    days_since = (today - last_date).days
                    wheel_delays[number] = days_since
                    break
            else:
                wheel_delays[number] = 999
        
        delays[wheel] = wheel_delays
    
    return delays

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
                parts[1] = "NAPOLI"
            elif parts[1] == "BA":
                parts[1] = "BARI"
            elif parts[1] == "CA":
                parts[1] = "CAGLIARI"
            elif parts[1] == "FI":
                parts[1] = "FIRENZE"
            elif parts[1] == "GE":
                parts[1] = "GENOVA"
            elif parts[1] == "MI":
                parts[1] = "MILANO"
            elif parts[1] == "PA":
                parts[1] = "PALERMO"
            elif parts[1] == "RM":
                parts[1] = "ROMA"
            elif parts[1] == "TO":
                parts[1] = "TORINO"
            elif parts[1] == "VE":
                parts[1] = "VENEZIA"
            elif parts[1] == "RN":
                parts[1] = "NAZIONALE"
            csv_writer.writerow(parts)
    
    global lotto_data, most_frequent, least_frequent, frequencies
    lotto_data = pd.read_csv('data/processed/lotto_historical.csv')
    lotto_data['date'] = pd.to_datetime(lotto_data['date'])
    
    frequencies, most_frequent, least_frequent = calculate_frequencies()
    
    st.cache_data.clear()

def main():
    st.markdown("<h1 style='text-align: center;'>Lotto Draws Visualizer</h1>", unsafe_allow_html=True)

    if not lotto_data.empty:
        last_update_date = lotto_data['date'].max().strftime('%B %d, %Y')
        
        st.markdown(
            f"<div style='text-align: center; padding: 10px; background-color: #1e88e5; color: white; border-radius: 5px; margin-bottom: 20px;'>"
            f"<b>Last data update:</b> {last_update_date}"
            f"</div>",
            unsafe_allow_html=True
        )
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button('Refresh Data', key="refresh_button", use_container_width=True, type="primary"):
            refresh_data()
            st.success("Data refreshed successfully!")
    
    tab1, tab2, tab3, tab4 = st.tabs(["Draws by Date", "Frequency Analysis", "Number Grid", "Delays Analysis"])    
    with tab1:
        if lotto_data.empty:
            st.warning("No data available. Please refresh the data.")
        else:
            st.markdown("<h3 style='text-align: center;'>View Draws by Date</h3>", unsafe_allow_html=True)
            
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
                selected_day = st.selectbox('Select Day', available_days, index=available_days.index(default_day))
            
            with col2:
                selected_month = st.selectbox('Select Month', available_months, index=available_months.index(default_month))
            
            with col3:
                selected_year = st.selectbox('Select Year', available_years, index=available_years.index(default_year))
                
            selected_date = pd.to_datetime(f"{selected_year}/{selected_month}/{selected_day}").date()
            filtered_data = lotto_data[lotto_data['date'].dt.date == selected_date]
            
            if not filtered_data.empty:
                st.markdown("<h4 style='text-align: center;'>Numbers drawn on {}</h4>".format(selected_date), unsafe_allow_html=True)
                
                table_html = "<table style='width: 80%; margin: 0 auto; border-collapse: collapse;'>"
                table_html += "<tr><th style='border: 1px solid #ddd; padding: 8px; text-align: left;'>Wheel</th>"
                
                for i in range(1, 6):
                    table_html += f"<th style='border: 1px solid #ddd; padding: 8px; text-align: center;'>Number {i}</th>"
                table_html += "</tr>"
                
                for _, wheel_data in filtered_data.iterrows():
                    table_html += f"<tr><td style='border: 1px solid #ddd; padding: 8px; font-weight: bold;'>{wheel_data['wheel']}</td>"
                    
                    for col in ['n1', 'n2', 'n3', 'n4', 'n5']:
                        if pd.notna(wheel_data[col]):
                            table_html += f"<td style='border: 1px solid #ddd; padding: 8px; text-align: center;'>{wheel_data[col]}</td>"
                        else:
                            table_html += f"<td style='border: 1px solid #ddd; padding: 8px; text-align: center;'>-</td>"
                    
                    table_html += "</tr>"
                
                table_html += "</table>"
                st.markdown(table_html, unsafe_allow_html=True)
            else:
                st.warning("No draws found for the selected date.")
    
    with tab2:
        if most_frequent.empty or least_frequent.empty:
            st.warning("No frequency data available. Please refresh the data.")
        else:
            st.markdown("<h3 style='text-align: center;'>Number Frequency Analysis</h3>", unsafe_allow_html=True)
            
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                wheels = most_frequent['wheel'].unique()
                selected_wheel = st.selectbox("Select Wheel", wheels, key="freq_wheel_select")
            
            st.markdown(f"<h4 style='text-align: center;'>Frequency Histogram for {selected_wheel}</h4>", unsafe_allow_html=True)
            
            wheel_frequencies = frequencies[frequencies['wheel'] == selected_wheel]
            freq_dict = dict(zip(wheel_frequencies['number'], wheel_frequencies['frequency']))
            
            all_numbers = range(1, 91)
            all_frequencies = [freq_dict.get(num, 0) for num in all_numbers]
            
            fig, ax = plt.subplots(figsize=(12, 6))
            bars = ax.bar(all_numbers, all_frequencies, color='#1e88e5')
            
            for i, freq in enumerate(all_frequencies):
                if i+1 in most_frequent[most_frequent['wheel'] == selected_wheel]['number'].tolist():
                    bars[i].set_color('#4caf50')
                elif i+1 in least_frequent[least_frequent['wheel'] == selected_wheel]['number'].tolist():
                    bars[i].set_color('#f44336')
            
            ax.set_xlabel('Number')
            ax.set_ylabel('Frequency')
            ax.set_title(f'Number Frequency for Wheel {selected_wheel}')
            ax.set_xticks(range(1, 91, 5))
            ax.grid(axis='y', linestyle='--', alpha=0.7)
            
            col1, col2, col3 = st.columns([1, 10, 1])
            with col2:
                st.pyplot(fig)
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("<h4 style='text-align: center;'>Most Frequent Numbers</h4>", unsafe_allow_html=True)
                most_wheel_data = most_frequent[most_frequent['wheel'] == selected_wheel].head(5)
                
                most_table = "<table style='width: 100%; border-collapse: collapse;'>"
                most_table += "<tr><th style='border: 1px solid #ddd; padding: 8px; background-color: #1e88e5; color: white;'>Number</th>"
                most_table += "<th style='border: 1px solid #ddd; padding: 8px; background-color: #1e88e5; color: white;'>Frequency</th></tr>"
                
                for _, row in most_wheel_data.iterrows():
                    most_table += f"<tr><td style='border: 1px solid #ddd; padding: 8px; text-align: center;'>{row['number']}</td>"
                    most_table += f"<td style='border: 1px solid #ddd; padding: 8px; text-align: center;'>{row['frequency']}</td></tr>"
                
                most_table += "</table>"
                st.markdown(most_table, unsafe_allow_html=True)
            
            with col2:
                st.markdown("<h4 style='text-align: center;'>Least Frequent Numbers</h4>", unsafe_allow_html=True)
                least_wheel_data = least_frequent[least_frequent['wheel'] == selected_wheel].head(5)
                
                least_table = "<table style='width: 100%; border-collapse: collapse;'>"
                least_table += "<tr><th style='border: 1px solid #ddd; padding: 8px; background-color: #f44336; color: white;'>Number</th>"
                least_table += "<th style='border: 1px solid #ddd; padding: 8px; background-color: #f44336; color: white;'>Frequency</th></tr>"
                
                for _, row in least_wheel_data.iterrows():
                    least_table += f"<tr><td style='border: 1px solid #ddd; padding: 8px; text-align: center;'>{row['number']}</td>"
                    least_table += f"<td style='border: 1px solid #ddd; padding: 8px; text-align: center;'>{row['frequency']}</td></tr>"
                
                least_table += "</table>"
                st.markdown(least_table, unsafe_allow_html=True)
            
            st.markdown("<h4 style='text-align: center;'>Last Draws</h4>", unsafe_allow_html=True)
            
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                num_draws = st.slider("Select number of last draws to display", min_value=1, max_value=10, value=3)
            
            last_draws = lotto_data[lotto_data['wheel'] == selected_wheel].sort_values(by='date', ascending=False).head(num_draws)
            
            if not last_draws.empty:
                for idx, (_, draw) in enumerate(last_draws.iterrows()):
                    st.markdown(f"<h5 style='text-align: center;'>{draw['date'].strftime('%Y-%m-%d')}</h5>", unsafe_allow_html=True)
                    
                    numbers_html = "<div style='display: flex; gap: 10px; margin-bottom: 15px; justify-content: center;'>"
                    most_freq_nums = most_frequent[most_frequent['wheel'] == selected_wheel]['number'].tolist()
                    least_freq_nums = least_frequent[least_frequent['wheel'] == selected_wheel]['number'].tolist()
                    
                    for col in ['n1', 'n2', 'n3', 'n4', 'n5']:
                        if col in draw and pd.notna(draw[col]):
                            num = draw[col]
                            if int(num) in most_freq_nums:
                                numbers_html += f"<div style='background-color:#1e88e5;color:#ffffff;padding:15px;text-align:center;border-radius:4px;font-weight:bold;width:50px'>{num}</div>"
                            elif int(num) in least_freq_nums:
                                numbers_html += f"<div style='background-color:#f44336;color:#ffffff;padding:15px;text-align:center;border-radius:4px;font-weight:bold;width:50px'>{num}</div>"
                            else:
                                numbers_html += f"<div style='background-color:#f5f5f5;color:#212121;padding:15px;text-align:center;border-radius:4px;font-weight:bold;width:50px'>{num}</div>"
                    
                    numbers_html += "</div>"
                    st.markdown(numbers_html, unsafe_allow_html=True)
            else:
                st.warning("No draws found for the selected wheel.")
            
            st.markdown("<hr>", unsafe_allow_html=True)
            st.markdown("<h3 style='text-align: center;'>Pattern Analysis</h3>", unsafe_allow_html=True)

            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                pattern_draws = st.slider("Number of draws to analyze patterns", 
                                        min_value=10, 
                                        max_value=100, 
                                        value=30,
                                        key="pattern_slider")

            wheel_data = lotto_data[lotto_data['wheel'] == selected_wheel].sort_values(by='date', ascending=False).head(pattern_draws)

            if not wheel_data.empty:
                total_draws = len(wheel_data)
                odd_even_ratios = []
                high_low_ratios = []
                consecutive_counts = []
                decade_distributions = {f"{i}-{i+9}": 0 for i in range(1, 91, 10)}
                
                for _, draw in wheel_data.iterrows():
                    numbers = [draw[f'n{i}'] for i in range(1, 6)]
                    numbers = [int(n) for n in numbers if pd.notna(n)]
                    
                    odd_count = sum(1 for n in numbers if n % 2 == 1)
                    even_count = len(numbers) - odd_count
                    odd_even_ratios.append((odd_count, even_count))
                    
                    high_count = sum(1 for n in numbers if n > 45)
                    low_count = len(numbers) - high_count
                    high_low_ratios.append((low_count, high_count))
                    
                    sorted_nums = sorted(numbers)
                    consecutive = 0
                    for i in range(len(sorted_nums) - 1):
                        if sorted_nums[i + 1] - sorted_nums[i] == 1:
                            consecutive += 1
                    consecutive_counts.append(consecutive)
                    
                    for num in numbers:
                        decade_start = 1 + ((num - 1) // 10) * 10
                        decade_key = f"{decade_start}-{decade_start+9}"
                        decade_distributions[decade_key] += 1
                
                odd_even_counts = {"5-0": 0, "4-1": 0, "3-2": 0, "2-3": 0, "1-4": 0, "0-5": 0}
                for odd, even in odd_even_ratios:
                    key = f"{odd}-{even}"
                    if key in odd_even_counts:
                        odd_even_counts[key] += 1
                    
                high_low_counts = {"5-0": 0, "4-1": 0, "3-2": 0, "2-3": 0, "1-4": 0, "0-5": 0}
                for low, high in high_low_ratios:
                    key = f"{low}-{high}"
                    if key in high_low_counts:
                        high_low_counts[key] += 1
                        
                consecutive_distribution = {0: 0, 1: 0, 2: 0, 3: 0, 4: 0}
                for count in consecutive_counts:
                    if count in consecutive_distribution:
                        consecutive_distribution[count] += 1
                        
                for key in decade_distributions:
                    decade_distributions[key] /= total_draws
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("<h4 style='text-align: center;'>Odd-Even Distribution</h4>", unsafe_allow_html=True)
                    
                    fig, ax = plt.subplots(figsize=(8, 5))
                    patterns = list(odd_even_counts.keys())
                    values = list(odd_even_counts.values())
                    percentages = [v / total_draws * 100 for v in values]
                    
                    bars = ax.bar(patterns, percentages, color='#1e88e5')
                    ax.set_ylabel('Percentage of Draws (%)')
                    ax.set_title('Odd-Even Number Patterns')
                    
                    for i, v in enumerate(percentages):
                        ax.text(i, v + 1, f"{v:.1f}%", ha='center')
                    
                    st.pyplot(fig)
                    
                    most_common_odd_even = max(odd_even_counts.items(), key=lambda x: x[1])
                    st.markdown(f"<div style='text-align: center; padding: 10px; background-color: #f5f5f5; border-radius: 5px;'>"
                                f"<b>Most common pattern:</b> {most_common_odd_even[0]} (Odd-Even) in {most_common_odd_even[1]} of {total_draws} draws "
                                f"({most_common_odd_even[1]/total_draws*100:.1f}%)"
                                f"</div>", 
                                unsafe_allow_html=True)
                
                with col2:
                    st.markdown("<h4 style='text-align: center;'>High-Low Distribution</h4>", unsafe_allow_html=True)
                    
                    fig, ax = plt.subplots(figsize=(8, 5))
                    patterns = list(high_low_counts.keys())
                    values = list(high_low_counts.values())
                    percentages = [v / total_draws * 100 for v in values]
                    
                    bars = ax.bar(patterns, percentages, color='#4caf50')
                    ax.set_ylabel('Percentage of Draws (%)')
                    ax.set_title('Low (1-45) - High (46-90) Number Patterns')
                    
                    for i, v in enumerate(percentages):
                        ax.text(i, v + 1, f"{v:.1f}%", ha='center')
                    
                    st.pyplot(fig)
                    
                    most_common_high_low = max(high_low_counts.items(), key=lambda x: x[1])
                    st.markdown(f"<div style='text-align: center; padding: 10px; background-color: #f5f5f5; border-radius: 5px;'>"
                                f"<b>Most common pattern:</b> {most_common_high_low[0]} (Low-High) in {most_common_high_low[1]} of {total_draws} draws "
                                f"({most_common_high_low[1]/total_draws*100:.1f}%)"
                                f"</div>", 
                                unsafe_allow_html=True)
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("<h4 style='text-align: center;'>Consecutive Numbers</h4>", unsafe_allow_html=True)
                    
                    fig, ax = plt.subplots(figsize=(8, 5))
                    patterns = list(consecutive_distribution.keys())
                    values = list(consecutive_distribution.values())
                    percentages = [v / total_draws * 100 for v in values]
                    
                    bars = ax.bar(patterns, percentages, color='#ff9800')
                    ax.set_xlabel('Number of Consecutive Pairs')
                    ax.set_ylabel('Percentage of Draws (%)')
                    ax.set_title('Consecutive Number Pairs Distribution')
                    
                    for i, v in enumerate(percentages):
                        ax.text(i, v + 1, f"{v:.1f}%", ha='center')
                    
                    st.pyplot(fig)
                    
                    most_common_consecutive = max(consecutive_distribution.items(), key=lambda x: x[1])
                    st.markdown(f"<div style='text-align: center; padding: 10px; background-color: #f5f5f5; border-radius: 5px;'>"
                                f"<b>Most common:</b> {most_common_consecutive[0]} consecutive pairs in {most_common_consecutive[1]} of {total_draws} draws "
                                f"({most_common_consecutive[1]/total_draws*100:.1f}%)"
                                f"</div>", 
                                unsafe_allow_html=True)
                
                with col2:
                    st.markdown("<h4 style='text-align: center;'>Number Range Distribution</h4>", unsafe_allow_html=True)
                    
                    fig, ax = plt.subplots(figsize=(8, 5))
                    decades = list(decade_distributions.keys())
                    values = list(decade_distributions.values())
                    
                    percentages = [v / 5 * 100 for v in values]
                    
                    bars = ax.bar(decades, percentages, color='#9c27b0')
                    ax.set_xlabel('Number Range')
                    ax.set_ylabel('Percentage (%)')
                    ax.set_title('Number Range Distribution')
                    plt.xticks(rotation=45)
                    
                    for i, v in enumerate(percentages):
                        ax.text(i, v + 0.5, f"{v:.1f}%", ha='center')
                    
                    st.pyplot(fig)
                    
                    most_common_decade = max(decade_distributions.items(), key=lambda x: x[1])
                    st.markdown(f"<div style='text-align: center; padding: 10px; background-color: #f5f5f5; border-radius: 5px;'>"
                                f"<b>Most common range:</b> {most_common_decade[0]} appearing in {most_common_decade[1]/total_draws*100:.1f}% of draws"
                                f"</div>", 
                                unsafe_allow_html=True)
                
                st.markdown("<h4 style='text-align: center;'>Pattern Analysis Summary</h4>", unsafe_allow_html=True)
                
                summary_html = f"""
                <table style='width: 100%; border-collapse: collapse; margin-top: 15px;'>
                    <tr>
                        <th style='border: 1px solid #ddd; padding: 12px; text-align: left; background-color: #1e88e5; color: white;'>Pattern Type</th>
                        <th style='border: 1px solid #ddd; padding: 12px; text-align: left; background-color: #1e88e5; color: white;'>Common Patterns</th>
                    </tr>
                    <tr>
                        <td style='border: 1px solid #ddd; padding: 12px;'><b>Odd-Even Balance</b></td>
                        <td style='border: 1px solid #ddd; padding: 12px;'>
                            Most draws have a {most_common_odd_even[0]} (Odd-Even) distribution<br>
                            Odd number frequency: {sum([odd for odd, _ in odd_even_ratios])/(total_draws*5)*100:.1f}%<br>
                            Even number frequency: {sum([even for _, even in odd_even_ratios])/(total_draws*5)*100:.1f}%
                        </td>
                    </tr>
                    <tr>
                        <td style='border: 1px solid #ddd; padding: 12px;'><b>High-Low Balance</b></td>
                        <td style='border: 1px solid #ddd; padding: 12px;'>
                            Most draws have a {most_common_high_low[0]} (Low-High) distribution<br>
                            Low numbers (1-45) frequency: {sum([low for low, _ in high_low_ratios])/(total_draws*5)*100:.1f}%<br>
                            High numbers (46-90) frequency: {sum([high for _, high in high_low_ratios])/(total_draws*5)*100:.1f}%
                        </td>
                    </tr>
                    <tr>
                        <td style='border: 1px solid #ddd; padding: 12px;'><b>Consecutive Numbers</b></td>
                        <td style='border: 1px solid #ddd; padding: 12px;'>
                            {consecutive_distribution[0]/total_draws*100:.1f}% of draws have no consecutive numbers<br>
                            {sum([consecutive_distribution[i] for i in range(1,5)])/total_draws*100:.1f}% of draws have at least one consecutive pair<br>
                            Average consecutive pairs per draw: {sum([i*consecutive_distribution[i] for i in consecutive_distribution])/total_draws:.2f}
                        </td>
                    </tr>
                    <tr>
                        <td style='border: 1px solid #ddd; padding: 12px;'><b>Number Range</b></td>
                        <td style='border: 1px solid #ddd; padding: 12px;'>
                            Most common range: {most_common_decade[0]} ({most_common_decade[1]/total_draws*5*100:.1f}% of all numbers)<br>
                            Least common range: {min(decade_distributions.items(), key=lambda x: x[1])[0]} ({min(decade_distributions.values())/total_draws*5*100:.1f}% of all numbers)
                        </td>
                    </tr>
                </table>
                """
                
                st.markdown(summary_html, unsafe_allow_html=True)
            else:
                st.warning("No data available for pattern analysis. Please refresh data.")
    
    with tab3:
        if lotto_data.empty or most_frequent.empty or least_frequent.empty:
            st.warning("No data available. Please refresh the data.")
        else:
            st.markdown("<h3 style='text-align: center;'>Number Grid Analysis</h3>", unsafe_allow_html=True)
            
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                wheels = lotto_data['wheel'].unique()
                selected_wheel = st.selectbox("Select Wheel", wheels, key="grid_wheel_selector")
                
                num_draws_to_consider = st.slider(
                    "Select number of draws to consider", 
                    min_value=1, 
                    max_value=20, 
                    value=10, 
                    key="grid_draws_slider"
                )
            
            last_n_draws = lotto_data[lotto_data['wheel'] == selected_wheel].sort_values(by='date', ascending=False).head(num_draws_to_consider)
            
            recent_numbers = []
            for col in ['n1', 'n2', 'n3', 'n4', 'n5']:
                recent_numbers.extend(last_n_draws[col].tolist())
            recent_numbers = [int(n) for n in recent_numbers]
            
            top_10_frequent = most_frequent[most_frequent['wheel'] == selected_wheel].head(10)['number'].tolist()
            top_10_frequent = [int(n) for n in top_10_frequent]
            
            bottom_10_frequent = least_frequent[least_frequent['wheel'] == selected_wheel].head(10)['number'].tolist()
            bottom_10_frequent = [int(n) for n in bottom_10_frequent]
            
            colors = {
                'neutral': '#f5f5f5',
                'recent': '#4caf50',
                'most_freq': '#1e88e5',
                'least_freq': '#f44336',
                'recent_most': '#8bc34a',
                'recent_least': '#ff9800',
                'text_dark': '#212121',
                'text_light': '#ffffff'
            }
            
            st.markdown("<div style='display: flex; justify-content: center;'>", unsafe_allow_html=True)
            legend_col1, legend_col2, legend_col3 = st.columns(3)
            
            with legend_col1:
                st.markdown(f"""
                <div style='display:flex;align-items:center;margin-bottom:10px'>
                    <div style='background-color:{colors["recent"]};width:20px;height:20px;margin-right:10px'></div>
                    <div>Recently drawn</div>
                </div>
                
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
            st.markdown("</div>", unsafe_allow_html=True)
            
            col1, col2, col3 = st.columns([1, 10, 1])
            with col2:
                grid_rows = 9
                grid_cols = 10
                
                for i in range(grid_rows):
                    cols = st.columns(grid_cols)
                    for j in range(grid_cols):
                        number = i * grid_cols + j + 1
                        if number <= 90:
                            is_recent = number in recent_numbers
                            is_most_frequent = number in top_10_frequent
                            is_least_frequent = number in bottom_10_frequent
                            
                            bg_color = colors['neutral']
                            text_color = colors['text_dark']
                            symbol = ""
                            
                            if is_recent and is_most_frequent:
                                bg_color = colors['recent_most']
                                text_color = colors['text_dark']
                                symbol = "+"
                            elif is_recent and is_least_frequent:
                                bg_color = colors['recent_least']
                                text_color = colors['text_dark']
                                symbol = "-"
                            elif is_recent:
                                bg_color = colors['recent']
                                text_color = colors['text_light']
                            elif is_most_frequent:
                                bg_color = colors['most_freq']
                                text_color = colors['text_light']
                            elif is_least_frequent:
                                bg_color = colors['least_freq']
                                text_color = colors['text_light']
                            
                            cols[j].markdown(
                                f"<div style='background-color:{bg_color};color:{text_color};padding:10px;text-align:center;border-radius:4px;font-weight:bold;'>{number}{symbol}</div>",
                                unsafe_allow_html=True
                            )

    with tab4:
        st.markdown("<h3 style='text-align: center;'>Delays Analysis</h3>", unsafe_allow_html=True)
        if lotto_data.empty:
            st.warning("No data available. Please refresh the data.")
        else:
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                wheels = lotto_data['wheel'].unique()
                selected_wheel = st.selectbox("Select a wheel", wheels, key="delay_wheel_selector")
            
            delays = calculate_delays()
            wheel_delays = delays[selected_wheel]
            
            delay_df = pd.DataFrame({
                'Number': list(wheel_delays.keys()),
                'Delay (days)': list(wheel_delays.values())
            }).sort_values('Delay (days)', ascending=False)
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("<h4 style='text-align: center;'>Numbers with the Longest Delays</h4>", unsafe_allow_html=True)
                top_delays = delay_df.head(10)
                
                delay_table = "<table style='width: 100%; border-collapse: collapse;'>"
                delay_table += "<tr><th style='border: 1px solid #ddd; padding: 8px; background-color: #f44336; color: white; text-align: center;'>Number</th>"
                delay_table += "<th style='border: 1px solid #ddd; padding: 8px; background-color: #f44336; color: white; text-align: center;'>Delay (days)</th></tr>"
                
                for _, row in top_delays.iterrows():
                    delay_table += f"<tr><td style='border: 1px solid #ddd; padding: 8px; text-align: center;'>{row['Number']}</td>"
                    delay_table += f"<td style='border: 1px solid #ddd; padding: 8px; text-align: center;'>{row['Delay (days)']}</td></tr>"
                
                delay_table += "</table>"
                st.markdown(delay_table, unsafe_allow_html=True)
                
            with col2:
                st.markdown("<h4 style='text-align: center;'>Recently Drawn Numbers</h4>", unsafe_allow_html=True)
                recent_numbers = delay_df.tail(10).sort_values('Delay (days)')
                
                recent_table = "<table style='width: 100%; border-collapse: collapse;'>"
                recent_table += "<tr><th style='border: 1px solid #ddd; padding: 8px; background-color: #4caf50; color: white; text-align: center;'>Number</th>"
                recent_table += "<th style='border: 1px solid #ddd; padding: 8px; background-color: #4caf50; color: white; text-align: center;'>Delay (days)</th></tr>"
                
                for _, row in recent_numbers.iterrows():
                    recent_table += f"<tr><td style='border: 1px solid #ddd; padding: 8px; text-align: center;'>{row['Number']}</td>"
                    recent_table += f"<td style='border: 1px solid #ddd; padding: 8px; text-align: center;'>{row['Delay (days)']}</td></tr>"
                
                recent_table += "</table>"
                st.markdown(recent_table, unsafe_allow_html=True)
            
            st.markdown("<h4 style='text-align: center;'>Delay Chart</h4>", unsafe_allow_html=True)
            
            fig, ax = plt.subplots(figsize=(12, 6))
            
            normalized_delays = delay_df['Delay (days)'] / delay_df['Delay (days)'].max()
            colors = plt.cm.RdYlGn_r(normalized_delays)
            
            bars = ax.bar(delay_df['Number'], delay_df['Delay (days)'], color=colors)
            
            ax.set_xlabel('Number')
            ax.set_ylabel('Delay (days)')
            ax.set_title(f'Number Delays for {selected_wheel} Wheel')
            ax.set_xticks(range(1, 91, 5))
            ax.grid(axis='y', linestyle='--', alpha=0.7)
            
            col1, col2, col3 = st.columns([1, 10, 1])
            with col2:
                st.pyplot(fig)

if __name__ == '__main__':
    main()