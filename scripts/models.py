import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split
from sklearn.multioutput import MultiOutputRegressor
from xgboost import XGBRegressor
from sklearn.metrics import mean_squared_error, mean_absolute_error

# Configurations
SEQUENCE_LENGTH = 10  # Time window length
WHEEL = 'BA'
RANDOM_STATE = 42

# Load and prepare data
df = pd.read_csv('data/processed/lotto_historical.csv')
df['date'] = pd.to_datetime(df['date'])

# Filter for the chosen wheel and sort chronologically
df_wheel = df[df['wheel'] == WHEEL].sort_values('date')

# Extract only the winning numbers (n1-n5)
numbers = df_wheel[['n1', 'n2', 'n3', 'n4', 'n5']].values

# Calculate frequency of each number
number_counts = pd.Series(numbers.flatten()).value_counts().sort_index()
number_freq = number_counts / number_counts.sum()

# Normalize the numbers to the range [0,1]
scaler = MinMaxScaler(feature_range=(0, 1))
scaled_numbers = scaler.fit_transform(numbers)

# Create time sequences by sliding a window over the normalized data
# Flatten each sequence to create a 1D feature vector for tree-based models
X, y = [], []
for i in range(len(scaled_numbers) - SEQUENCE_LENGTH):
    sequence = scaled_numbers[i:i+SEQUENCE_LENGTH].flatten()
    freq_features = number_freq[numbers[i+SEQUENCE_LENGTH-1]].values
    X.append(np.concatenate([sequence, freq_features]))  # add frequency features
    y.append(scaled_numbers[i+SEQUENCE_LENGTH])
X = np.array(X)
y = np.array(y)

# Split data into training and testing sets (80% train, 20% test)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=RANDOM_STATE)

# Build an XGBoost multi-output regressor
model = MultiOutputRegressor(
    XGBRegressor(n_estimators=100, learning_rate=0.1, random_state=RANDOM_STATE)
)
model.fit(X_train, y_train)

# Evaluate model performance
y_pred = model.predict(X_test)
print("MSE:", mean_squared_error(y_test, y_pred))
print("MAE:", mean_absolute_error(y_test, y_pred))

# Use the last sequence from the test set to make a prediction
last_sequence = X_test[-1].reshape(1, -1)
predicted_scaled = model.predict(last_sequence)
predicted_numbers = scaler.inverse_transform(predicted_scaled).astype(int).flatten()

print("Last real draw:", numbers[-1])
print("Predicted numbers:", predicted_numbers)

