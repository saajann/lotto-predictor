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

input_file = "data/raw/storico01-oggi.txt"
output_file = "data/processed/lotto_historical.csv"

with open(input_file, "r") as txt_file, open(output_file, "w", newline='') as csv_file:
    csv_writer = csv.writer(csv_file)
    csv_writer.writerow(["date", "wheel", "n1", "n2", "n3", "n4", "n5"])
    
    for line in txt_file:
        parts = line.strip().split("\t")
        csv_writer.writerow(parts)