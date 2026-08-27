import pandas as pd
import glob
import os

# 1. Load All 12-Month CSV Files
path = '/content/drive/MyDrive/cyclistic_data/*.csv'
all_files = glob.glob(path)

df_list = []
for filename in sorted(all_files):
    # Skip previously created cleaned files if re-running
    if 'cleaned_cyclistic_full' not in filename and 'tableau_summary_data' not in filename:
        data = pd.read_csv(filename, on_bad_lines='skip', engine='python')
        df_list.append(data)

# Combine all monthly dataframes into one raw dataframe
raw_df = pd.concat(df_list, axis=0, ignore_index=True)
print(f"Total Raw Rows Loaded: {len(raw_df):,}")

# 2. Date Conversion & Handling Mixed Formats
print("Converting Datetime Columns...")
raw_df['started_at'] = pd.to_datetime(raw_df['started_at'], format='mixed', errors='coerce')
raw_df['ended_at'] = pd.to_datetime(raw_df['ended_at'], format='mixed', errors='coerce')

# 3. Feature Engineering
print("Engineering Features (Ride Length, Day, Month, Hour)...")
# Calculate ride duration in minutes
raw_df['ride_length_min'] = (raw_df['ended_at'] - raw_df['started_at']).dt.total_seconds() / 60
raw_df['day_of_week'] = raw_df['started_at'].dt.day_name()
raw_df['month_name'] = raw_df['started_at'].dt.month_name()
raw_df['hour_of_day'] = raw_df['started_at'].dt.hour

# 4. Data Cleaning
print("Cleaning Data...")
# Drop missing critical values and duplicate ride IDs
cleaned_df = raw_df.dropna(subset=['started_at', 'ended_at', 'start_station_name', 'end_station_name'])
cleaned_df = cleaned_df.drop_duplicates(subset=['ride_id'])

# Remove erroneous trips (ride length <= 1 min or negative duration)
cleaned_df = cleaned_df[cleaned_df['ride_length_min'] > 1]
print(f"Total Cleaned Rows: {len(cleaned_df):,}")

# 5. Export Full Cleaned Dataset
export_path = '/content/drive/MyDrive/cyclistic_data/cleaned_cyclistic_full.csv'
cleaned_df.to_csv(export_path, index=False)
print("SUCCESS: Full Cleaned Dataset Exported!")

# 6. Aggregation for Tableau Dashboard
print("Generating Summary Data for Tableau...")
summary_df = cleaned_df.groupby(
    ['member_casual', 'rideable_type', 'day_of_week', 'month_name', 'hour_of_day']
).agg(
    total_rides=('ride_id', 'count'),
    avg_ride_length=('ride_length_min', 'mean')
).reset_index()

# 7. Export Summary Dataset for Tableau
summary_path = '/content/drive/MyDrive/cyclistic_data/tableau_summary_data.csv'
summary_df.to_csv(summary_path, index=False)
print(f"Summary Dataset Rows: {len(summary_df):,}")
print("SUCCESS: Tableau Summary Data Exported Successfully!")