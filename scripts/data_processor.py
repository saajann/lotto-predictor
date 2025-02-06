import csv

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