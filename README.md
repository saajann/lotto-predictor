# Lotto Draws Visualizer

> No machine learning, just statistics.

A streamlit web app for visualizing and analyzing Italian lotto draws using historical data.

## Overview

This application provides a simple way to:
- View historical lottery draws by date
- Analyze number frequency patterns
- Visualize number trends with an intuitive grid system

## Features

- **Draws by Date**: Browse historical lottery draws with a clean, tabular interface
- **Frequency Analysis**: View histograms showing the occurrence patterns of numbers for each wheel
- **Number Grid**: Quickly identify hot and cold numbers with an intuitive color-coded grid

## Getting Started

Ecco la versione corretta:  

## Getting Started

1. Clone this repository:
   ```sh
   git clone https://github.com/saajann/lotto-predictor.git
   ```
2. Navigate into the project directory:
   ```sh
   cd lotto-predictor
   ```
3. Install requirements:
   ```sh
   pip install -r requirements.txt
   ```
4. Run the application:
   ```sh
   streamlit run scripts/app.py
   ```

## Data Structure

The application organizes data in three main directories:
- `data/raw`: Contains the original downloaded zip file and extracted text data
- `data/processed`: Contains cleaned and formatted historical draw data
- `data/historical_stats`: Contains pre-calculated frequency statistics

## Usage

1. Click "Refresh Data" to download the latest lottery data
2. Navigate between tabs to explore different views of the data
3. Use the dropdowns and sliders to customize your analysis