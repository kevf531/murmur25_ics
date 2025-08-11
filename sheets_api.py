# %% 
# Imports
import pandas as pd
import re
from datetime import datetime


# %%
# Constants
gsheetkey = "1TG5w2ETvf9H3eIB1KJG-yDtwizyyYC-lXnq10gt4kdc"
sheet_name = "Murmur - Practice Schedule"
url=f'https://docs.google.com/spreadsheet/ccc?key={gsheetkey}&output=xlsx'
# Parameters
name = 'Kevin Fan'
today = datetime.today()


# %%
# DF and formatting
df = pd.read_excel(url,sheet_name=sheet_name, header=None)
schedule_df = df.head(4)
players_df = df.iloc[9:50]
players_df = players_df[players_df.iloc[:, 0] == name]

schedule_df_clean = pd.DataFrame()

# formatting on schedule
for row in schedule_df.iloc[:, 0]:
    raw = schedule_df[schedule_df.iloc[:, 0] == row].iloc[:, 1:20]
    schedule_df_clean[row] = raw.T

schedule_df_clean["Attendance"] = players_df.iloc[:, 1:20].T


# %%
# Clean up the date formats 
def clean_and_parse_date(date_str, year=2025):
    # Remove suffixes and notes
    date_str = re.sub(r"(st|nd|rd|th)", "", date_str)
    date_str = re.sub(r"\(.*?\)", "", date_str).strip()
    date_str = date_str.replace("Sept.", "Sep").replace("Aug.", "Aug").replace("Oct.", "Oct")
    
    # Handle ranges
    if "-" in date_str:
        parts = date_str.split("-")
        # Extract month from the first part
        month = parts[0].split()[0]
        day1 = re.findall(r"\d+", parts[0])[-1]
        day2 = re.findall(r"\d+", parts[1])[0]
        start_date = pd.to_datetime(f"{month} {day1}, {year}")
        end_date = pd.to_datetime(f"{month} {day2}, {year}")
        return pd.Series([start_date, end_date])
    else:
        date_parsed = pd.to_datetime(date_str + f" {year}")
        return pd.Series([date_parsed, date_parsed])

# Apply transformation
schedule_df_clean[["Start Date", "End Date"]] = schedule_df_clean["Date"].apply(lambda x: clean_and_parse_date(x))

# %%
# All day
schedule_df_clean['all_day'] = schedule_df_clean['Start Date'] != schedule_df_clean['End Date']

# helper functions
def parse_flexible_time(time_str):
    """Parses time strings like '10am' or '10:30am'"""
    for fmt in ('%I:%M%p', '%I%p'):
        try:
            return datetime.strptime(time_str.strip(), fmt)
        except ValueError:
            continue
    raise ValueError(f"Time format not recognized: {time_str}")


# Add timestamps 
for index, row in schedule_df_clean.iterrows():
    # print(index)
    # print(row)
    if row["all_day"] == False and pd.notna(row["Time"]):
        # print("NOT ALL DAY")
        time = row["Time"]
        # print(time)
        time_parts = time.split("-")
        # print(time_parts[0])
        # print(time_parts[-1])
        start_datetimes = parse_flexible_time(time_parts[0]).replace(
            year=row["Start Date"].year, 
            month=row["Start Date"].month, 
            day=row["Start Date"].day
            )
        end_datetimes = parse_flexible_time(time_parts[-1]).replace(
            year=row["End Date"].year, 
            month=row["End Date"].month, 
            day=row["End Date"].day
            )
        # print(start_datetimes)
        # print(end_datetimes)
             
        schedule_df_clean.loc[index, "Start Date"] = start_datetimes
        schedule_df_clean.loc[index, "End Date"] = end_datetimes

        if row['Start Date'] == row['End Date']:
            schedule_df_clean.loc[index, "all_day"] = True

# %%
schedule_df_clean

# %%
