import pandas as pd
import re
from datetime import datetime
from typing import Optional, Tuple


class SheetsCalendarReader:
    """Reads and processes calendar data from Google Sheets"""
    
    def __init__(self, gsheet_key: str, sheet_name: str, player_name: str, year: int = 2025):
        self.gsheet_key = gsheet_key
        self.sheet_name = sheet_name  
        self.player_name = player_name
        self.year = year
        self.url = f'https://docs.google.com/spreadsheet/ccc?key={gsheet_key}&output=xlsx'
        
    def read_sheet_data(self) -> pd.DataFrame:
        """Read raw data from Google Sheets"""
        return pd.read_excel(self.url, sheet_name=self.sheet_name, header=None)
    
    def extract_schedule_and_attendance(self, df: pd.DataFrame) -> pd.DataFrame:
        """Extract and combine schedule data with player attendance"""
        schedule_df = df.head(4)
        players_df = df.iloc[9:50]
        player_attendance = players_df[players_df.iloc[:, 0] == self.player_name]
        
        schedule_clean = pd.DataFrame()
        
        # Transform schedule data
        for row_label in schedule_df.iloc[:, 0]:
            raw_data = schedule_df[schedule_df.iloc[:, 0] == row_label].iloc[:, 1:20]
            schedule_clean[row_label] = raw_data.T
            
        # Add attendance data
        schedule_clean["Attendance"] = player_attendance.iloc[:, 1:20].T
        
        return schedule_clean
    
    def clean_and_parse_date(self, date_str: str) -> Tuple[datetime, datetime]:
        """Parse date strings, handling ranges and various formats"""
        # Clean up the date string
        date_str = re.sub(r"(st|nd|rd|th)", "", date_str)
        date_str = re.sub(r"\(.*?\)", "", date_str).strip()
        date_str = date_str.replace("Sept.", "Sep").replace("Aug.", "Aug").replace("Oct.", "Oct")
        
        # Handle date ranges (e.g., "Sep 14-15")
        if "-" in date_str:
            parts = date_str.split("-")
            month = parts[0].split()[0]
            day1 = re.findall(r"\d+", parts[0])[-1]
            day2 = re.findall(r"\d+", parts[1])[0]
            start_date = pd.to_datetime(f"{month} {day1}, {self.year}")
            end_date = pd.to_datetime(f"{month} {day2}, {self.year}")
            return start_date, end_date
        else:
            date_parsed = pd.to_datetime(f"{date_str} {self.year}")
            return date_parsed, date_parsed
    
    def parse_time(self, time_str: str) -> datetime:
        """Parse flexible time formats like '10am' or '10:30am'"""
        time_str = time_str.strip()
        for fmt in ('%I:%M%p', '%I%p'):
            try:
                return datetime.strptime(time_str, fmt)
            except ValueError:
                continue
        raise ValueError(f"Time format not recognized: {time_str}")
    
    def process_dates_and_times(self, df: pd.DataFrame) -> pd.DataFrame:
        """Process all date and time information"""
        # Parse dates
        date_results = df["Date"].apply(lambda x: self.clean_and_parse_date(x))
        df[["Start Date", "End Date"]] = pd.DataFrame(date_results.tolist(), index=df.index)
        
        # Determine all-day events (multi-day ranges OR missing times)
        df['all_day'] = (df['Start Date'] != df['End Date']) | df['Time'].isna()
        
        # Process specific times for non-all-day events
        for index, row in df.iterrows():
            if not row["all_day"] and pd.notna(row["Time"]):
                self._add_specific_times(df, index, row)
        
        return df
    
    def _add_specific_times(self, df: pd.DataFrame, index: int, row: pd.Series):
        """Add specific start/end times to events"""
        time_parts = row["Time"].split("-")
        
        start_time = self.parse_time(time_parts[0])
        end_time = self.parse_time(time_parts[-1])
        
        # Combine date with time
        start_datetime = start_time.replace(
            year=row["Start Date"].year,
            month=row["Start Date"].month, 
            day=row["Start Date"].day
        )
        end_datetime = end_time.replace(
            year=row["End Date"].year,
            month=row["End Date"].month,
            day=row["End Date"].day
        )
        
        df.loc[index, "Start Date"] = start_datetime
        df.loc[index, "End Date"] = end_datetime
    
    def finalize_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean up column names and select necessary columns"""
        df.rename(columns={
            'Location (subject to change)': 'loc', 
            'Start Date': 'start_dt', 
            'End Date': 'end_dt'
        }, inplace=True)
        
        necessary_cols = ['Event', 'loc', 'Attendance', 'start_dt', 'end_dt', 'all_day']
        return df[necessary_cols]
    
    def get_calendar_data(self) -> pd.DataFrame:
        """Main method to get processed calendar data"""
        # Read and process data
        raw_df = self.read_sheet_data()
        schedule_df = self.extract_schedule_and_attendance(raw_df)
        processed_df = self.process_dates_and_times(schedule_df)
        final_df = self.finalize_dataframe(processed_df)
        
        return final_df


# Usage example
if __name__ == "__main__":
    # Configuration
    GSHEET_KEY = "1TG5w2ETvf9H3eIB1KJG-yDtwizyyYC-lXnq10gt4kdc"
    SHEET_NAME = "Murmur - Practice Schedule"
    PLAYER_NAME = "Kevin Fan"
    
    # Create reader and get data
    reader = SheetsCalendarReader(GSHEET_KEY, SHEET_NAME, PLAYER_NAME)
    calendar_data = reader.get_calendar_data()
    
    print(calendar_data)