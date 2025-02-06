import streamlit as st
import pandas as pd

@st.cache_data
def load_data():
    return pd.read_csv('data/processed/lotto_historical.csv')

data = load_data()

data['date'] = pd.to_datetime(data['date'])

def main():
    st.title('Lotto Draws Visualizer')
    
    available_dates = data['date'].dt.date.unique()
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
    filtered_data = data[data['date'].dt.date == selected_date]
    
    if not filtered_data.empty:
        st.write(f"Numbers drawn on {selected_date}:")
        st.dataframe(filtered_data[['wheel', 'n1', 'n2', 'n3', 'n4', 'n5']], use_container_width=True)
    else:
        st.warning("No draws found for the selected date.")

if __name__ == '__main__':
    main()