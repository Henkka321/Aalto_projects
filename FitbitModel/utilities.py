import pandas as pd
import os
import json

def load_oura_data(folder_name="K_Oura_14.4"):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    base = os.path.join(script_dir, "data", folder_name, "App Data")

    heart_data = pd.read_csv(os.path.join(base, "heartrate.csv"), sep=";")
    temp_data  = pd.read_csv(os.path.join(base, "temperature.csv"), sep=";")
    sp02_data  = pd.read_csv(os.path.join(base, "dailyspo2.csv"), sep=";")

    # Parse timestamps
    heart_data["timestamp"] = pd.to_datetime(heart_data["timestamp"])
    heart_data["bpm"]       = heart_data["bpm"].astype(int)

    temp_data["timestamp"] = pd.to_datetime(temp_data["timestamp"])
    temp_data["skin_temp"] = temp_data["skin_temp"].astype(float)

    sp02_data["timestamp"]       = pd.to_datetime(sp02_data["day"])
    sp02_data["spo2_percentage"] = sp02_data["spo2_percentage"].apply(
        lambda x: json.loads(x)["average"] if pd.notna(x) else None
    ).astype(float)

    # Extract date for spo2 join — only on heart and temp before merging
    heart_data["date"] = heart_data["timestamp"].dt.date
    temp_data["date"]  = temp_data["timestamp"].dt.date
    sp02_data["date"]  = sp02_data["timestamp"].dt.date
    sp02_data = sp02_data[["date", "spo2_percentage"]]

    # Merge heart and temp — both have "date" so it gets suffixed to date_x, date_y
    merged_data = pd.merge(heart_data, temp_data, on="timestamp", how="outer")
    
    # Consolidate the duplicate date columns into one, then drop the extras
    merged_data["date"] = merged_data["date_x"].combine_first(merged_data["date_y"])
    merged_data = merged_data.drop(columns=["date_x", "date_y"])

    # Now merge spo2 cleanly on the single date column
    merged_data = pd.merge(merged_data, sp02_data, on="date", how="left")
    
    # Drop the date helper column — it was only needed for the spo2 join
    merged_data = merged_data.drop(columns=["date"])

    return merged_data


def load_fitbit_data(folder_name = "k_fitbit_13.4"):
    #loads spo2 data from default fitbit folder. Merges daily files to one pd dataframe. 
    # Returns the merged dataframe.
    script_dir = os.path.dirname(os.path.abspath(__file__))
    base = os.path.join(script_dir, "data", folder_name, "Fitbit",)
#Aalto_projects\FitbitModel\data\takeout Fitbit Kari 13.4.  asti\Fitbit\Oxygen Saturation (SpO2)
    spo2 = os.path.join(script_dir, "data", folder_name, "Fitbit","Oxygen Saturation (SpO2)")
    # load and merge spo2 data from multiple daily files
    spo2_data = []
    for file in os.listdir(spo2):
        if file.endswith(".csv"):
            df = pd.read_csv(os.path.join(spo2, file))
            spo2_data.append(df)
    return pd.concat(spo2_data, ignore_index=True)

data = load_oura_data("K_Oura_14.4")
data.to_csv("oura_merged_data.csv", index=False)

print(data.head())

fit_bit_data = load_fitbit_data("k_fitbit_13.4")
print(fit_bit_data.head())