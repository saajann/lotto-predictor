# Lotto Predictor

**Lotto Predictor** is a data-driven project designed to analyze and predict the numbers of the Italian Lotto. It integrates official historical data, advanced statistical analysis, and machine learning models to provide insights and predictions. The project includes a user-friendly dashboard built with Streamlit for interactive exploration.

---

## Table of Contents
1. [Project Overview](#project-overview)
2. [Features](#features)
3. [Project Structure](#project-structure)
4. [Setup and Installation](#setup-and-installation)
5. [Usage](#usage)
6. [Technologies Used](#technologies-used)
7. [Limitations and Ethical Considerations](#limitations-and-ethical-considerations)
8. [Future Enhancements](#future-enhancements)
9. [Contributing](#contributing)
10. [License](#license)

---

## Project Overview

The Lotto Predictor project aims to:
- Automatically download and process historical Lotto data from official sources.
- Perform advanced statistical analysis to identify patterns, frequencies, and trends.
- Train machine learning models (e.g., ARIMA, LSTM) to predict future Lotto numbers.
- Provide an interactive dashboard for users to explore data and predictions.

---

## Features

- **Data Collection**: Automated download of historical Lotto data (1939–present) from official sources.
- **Data Processing**: Cleaning, normalization, and transformation of raw data into a structured format.
- **Statistical Analysis**:
  - Frequency analysis (most/least drawn numbers).
  - Identification of "ritardatari" (numbers not drawn for a long time).
  - Temporal patterns (e.g., day-of-week trends).
  - Correlations between different Lotto wheels.
- **Machine Learning Models**:
  - ARIMA for time-series forecasting.
  - LSTM (Long Short-Term Memory) for sequence prediction.
  - Bayesian analysis for conditional probabilities.
  - Ensemble learning for combining multiple models.
- **Interactive Dashboard**:
  - Built with Streamlit and Plotly.
  - Visualizations: Heatmaps, bar charts, and interactive tables.
  - Customizable parameters (e.g., Lotto wheel, prediction method).

---

## Project Structure

```
lotto-predictor/
├── data/
│   ├── raw/ (raw data downloaded from official sources)
│   ├── processed/ (cleaned and structured data in CSV/Parquet format)
│   └── historical_stats/ (aggregated statistics)
├── scripts/
│   ├── data_collection.py (automated data download)
│   ├── data_processor.py (data cleaning and transformation)
│   ├── analysis.py (statistical analysis)
│   ├── models.py (machine learning models)
│   └── app.py (Streamlit dashboard)
├── models/ (saved machine learning models)
├── tests/ (unit and integration tests)
├── requirements.txt (Python dependencies)
└── README.md (project documentation)
```

---

## Setup and Installation

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/user/lotto-predictor
   cd lotto-predictor
   ```

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the Streamlit Dashboard**:
   ```bash
   streamlit run scripts/app.py
   ```

4. **Download Historical Data**:
   - Run the `data_collection.py` script to download and extract historical Lotto data:
     ```bash
     python scripts/data_collection.py
     ```

5. **Preprocess Data**:
   - Run the `data_processor.py` script to clean and structure the data:
     ```bash
     python scripts/data_processor.py
     ```

---

## Usage

1. **Dashboard**:
   - Launch the Streamlit dashboard:
     ```bash
     streamlit run scripts/app.py
     ```
   - Select a Lotto wheel (e.g., Nazionale, Milano, Roma) and a prediction method (e.g., Frequencies, Ritardatari, LSTM).
   - Explore visualizations and predictions.

2. **Statistical Analysis**:
   - Use the `analysis.py` script to generate insights such as frequency distributions, ritardatari, and temporal patterns.

3. **Machine Learning Models**:
   - Train and evaluate models using the `models.py` script.
   - Save trained models in the `models/` directory for future use.

---

## Technologies Used

- **Programming Language**: Python 3.10+
- **Libraries**:
  - Data Processing: Pandas, NumPy, PyArrow
  - Machine Learning: TensorFlow, Scikit-learn, Statsmodels
  - Visualization: Plotly, Matplotlib, Seaborn
  - Dashboard: Streamlit
- **Database**: DuckDB (for fast querying on CSV/Parquet files)
- **Scheduling**: Apache Airflow (for automated data updates)

---

## Limitations and Ethical Considerations

- **Randomness of Lotto**: The Lotto is a game of chance, and predictions do not guarantee wins.
- **Responsible Gambling**: The dashboard includes warnings about responsible gambling practices.
- **Data Accuracy**: Only official data sources are used to ensure reliability.

---

## Future Enhancements

1. **API Integration**: Export results in PDF/Excel format via an API.
2. **Simbolotto Analysis**: Incorporate Simbolotto data (available since 2019).
3. **Email Notifications**: Send alerts for "critical" numbers (e.g., ritardatari).
4. **Advanced Models**: Experiment with reinforcement learning and graph-based models.

---

## Contributing

Contributions are welcome! Please follow these steps:
1. Fork the repository.
2. Create a new branch for your feature or bugfix.
3. Submit a pull request with a detailed description of your changes.

---

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

*Disclaimer*: This project is for educational and entertainment purposes only. It does not guarantee any winnings in the Lotto or other gambling activities.
