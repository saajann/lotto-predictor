import requests
import zipfile
import csv
# import os

URL = "https://www.igt.it/STORICO_ESTRAZIONI_LOTTO/storico01-oggi.zip"

response = requests.get(URL)
with open("data/raw/lotto_historical.zip", "wb") as f:
    f.write(response.content)

with zipfile.ZipFile("data/raw/lotto_historical.zip", 'r') as zip_ref:
    zip_ref.extractall("data/raw/")

# os.remove("data/raw/lotto_historical.zip")