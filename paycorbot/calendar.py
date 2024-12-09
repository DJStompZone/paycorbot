import json
import re
import sys
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
import pandas as pd

def standardize_time_str(time_str):
    """
    Standardizes a time string to a uniform format for parsing.
    """
    time_str = time_str.strip().lower()
    time_str = time_str.replace('.', '').replace(' ', '')
    if time_str.endswith('a'):
        time_str = time_str[:-1] + 'am'
    elif time_str.endswith('p'):
        time_str = time_str[:-1] + 'pm'
    if not re.match(r'\d+:\d+', time_str):
        time_str = time_str[:-2] + ':00' + time_str[-2:]
    return time_str

def parse_time_str(time_str):
    """
    Parses a standardized time string into a datetime object.
    """
    time_str = standardize_time_str(time_str)
    time_formats = ['%I:%M%p', '%I%p']
    for fmt in time_formats:
        try:
            return datetime.strptime(time_str, fmt).time()
        except ValueError:
            continue
    raise ValueError(f"Time data '{time_str}' does not match any known format.")

def parse_shift_times(shift_times, date):
    """
    Parses the shift times and returns a dictionary with shift details.
    """
    try:
        start_time_str, end_time_str = shift_times.split('/')
        start_time = parse_time_str(start_time_str)
        end_time = parse_time_str(end_time_str)
        shift_start = datetime.combine(date.date(), start_time)
        shift_end = datetime.combine(date.date(), end_time)
        if shift_end <= shift_start:
            shift_end += timedelta(days=1)
        return {
            'Shift Date': date.date(),
            'Start Time': shift_start,
            'End Time': shift_end,
            'Duration (Hours)': round((shift_end - shift_start).total_seconds() / 3600, 2)
        }
    except ValueError as e:
        print(f"Error parsing times '{shift_times}': {e}")
        return None

def parse_raw_markup(page_source):
    """
    Parses raw markup and extracts schedule information.
    """
    soup = BeautifulSoup(page_source, "html.parser")
    schedule_rows = soup.select("div.x-grid-item-container table")
    shifts = []

    for table in schedule_rows:
        rows = table.select("tr")
        for row in rows:
            cells = row.select("td")
            for cell in cells:
                date = cell.select_one(".indv-sch-cell-date-dom")
                time = cell.select_one(".indv-sch-sch-sten")
                hours = cell.select_one(".indv-sch-sch-hrs")
                if date and time and hours:
                    day_date = int(date.text.strip())
                    day_time = time.text.strip()
                    day_hours = float(hours.text.strip().replace("h", ""))
                    current_date = datetime(datetime.now().year, datetime.now().month, day_date)
                    shift = parse_shift_times(day_time, current_date)
                    if shift:
                        shift['Duration (Hours)'] = day_hours
                        shifts.append(shift)
    return shifts

def output_to_excel(shifts, output_file):
    """
    Outputs the shifts to an Excel file.
    """
    df = pd.DataFrame(shifts)
    df['Start Time'] = pd.to_datetime(df['Start Time'], format='%Y-%m-%d %H:%M:%S', errors='coerce')
    df['End Time'] = pd.to_datetime(df['End Time'], format='%Y-%m-%d %H:%M:%S', errors='coerce')
    df.to_excel(output_file, index=False)
    print(f"Shifts have been successfully written to {output_file}")

def parse_calendar():
    """
    Main function to parse a schedule JSON file and output the data to an Excel file.
    This function uses argparse to handle command-line arguments for specifying the input JSON file
    and the output Excel file. It reads the JSON data from the input file, parses the schedule, and
    writes the parsed data to the output Excel file.
    Command-line arguments:
    --in : str : Path to the input JSON file (required).
    --out : str : Path to the output Excel file (required).
    Raises:
    FileNotFoundError: If the input JSON file does not exist.
    json.JSONDecodeError: If the input file is not a valid JSON.
    """
    parser = argparse.ArgumentParser(description='Parse schedule JSON and output to Excel.')
    parser.add_argument('--in', dest='input_file', required=True, help='Input JSON file')
    parser.add_argument('--out', dest='output_file', required=True, help='Output Excel file')
    args = parser.parse_args()
    with open(args.input_file, 'r', encoding='utf-8') as f:
        json_data = f.read()
    # Parser? I barely know her!
    shifts = parse_schedule(json_data)


    if shifts:
        output_to_excel(shifts, args.output_file)
    else:
        print('No shifts found in the schedule.')

if __name__ == '__main__':
    parse_calendar()
