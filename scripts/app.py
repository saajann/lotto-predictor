import streamlit as st
import pandas as pd

@st.cache_data
def load_data():
    lotto_data = pd.read_csv('data/processed/lotto_historical.csv')
    most_frequent = pd.read_csv('data/historical_stats/most_frequent.csv')
    least_frequent = pd.read_csv('data/historical_stats/least_frequent.csv')
    return lotto_data, most_frequent, least_frequent

lotto_data, most_frequent, least_frequent = load_data()

lotto_data['date'] = pd.to_datetime(lotto_data['date'])

def main():
    st.title('Lotto Draws Visualizer')
    
    # Sidebar menu
    st.sidebar.title("Menu")
    option = st.sidebar.radio("Choose an option:", 
                              ("View Draws by Date", "Most Frequent Numbers", "Least Frequent Numbers"))
    
    if option == "View Draws by Date":
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
    
    elif option == "Most Frequent Numbers":
        st.write("Most Frequent Numbers (last 1000 extractions):")
        
        wheels = most_frequent['wheel'].unique()
        
        selected_wheel = st.selectbox("Select Wheel", wheels)
        
        wheel_data = most_frequent[most_frequent['wheel'] == selected_wheel]
        
        st.write(f"Most frequent numbers for wheel **{selected_wheel}**:")
        
        cols = st.columns(5)
        for idx, (_, row) in enumerate(wheel_data.iterrows()):
            with cols[idx % 5]:  
                st.markdown(f"**Number {row['number']}**")
                st.write(f"Frequency: {row['frequency']}")
    
    elif option == "Least Frequent Numbers":
        st.write("Least Frequent Numbers (last 1000 extractions):")
        
        wheels = least_frequent['wheel'].unique()
        
        selected_wheel = st.selectbox("Select Wheel", wheels)
        
        wheel_data = least_frequent[least_frequent['wheel'] == selected_wheel]
        
        st.write(f"Least frequent numbers for wheel **{selected_wheel}**:")
        
        cols = st.columns(5)
        for idx, (_, row) in enumerate(wheel_data.iterrows()):
            with cols[idx % 5]:  
                st.markdown(f"**Number {row['number']}**")
                st.write(f"Frequency: {row['frequency']}")

if __name__ == '__main__':
    main()