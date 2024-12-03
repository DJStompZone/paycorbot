import json
import argparse
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import pandas as pd
import sys

def standardize_time_str(time_str):
    """
    Standardizes a time string to a uniform format for parsing.

    Args:
        time_str (str): The raw time string extracted from the data.

    Returns:
        str: A standardized time string.
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
    Parses a standardized time string into a datetime.time object.

    Args:
        time_str (str): The standardized time string.

    Returns:
        datetime.time: The parsed time object.

    Raises:
        ValueError: If the time string cannot be parsed.
    """
    time_str = standardize_time_str(time_str)
    time_formats = ['%I:%M%p', '%I%p']
    for fmt in time_formats:
        try:
            return datetime.strptime(time_str, fmt)
        except ValueError:
            continue
    raise ValueError(f"Time data '{time_str}' does not match any known format.")

def parse_day(day_html, default_date):
    """
    Parses the schedule for a single day.

    Args:
        day_html (str): The HTML content for the day's schedule.
        default_date (datetime): The default date if not specified in the HTML.

    Returns:
        list: A list of shift dictionaries for the day, or None if no shifts.
    """
    soup = BeautifulSoup(day_html, 'html.parser')
    date_div = soup.find('div', class_='indv-sch-cell-date')
    if date_div:
        month_div = date_div.find('div', class_='indv-sch-cell-date-mon')
        day_div = date_div.find('div', class_='indv-sch-cell-date-dom')
        if month_div and day_div:
            month_name = month_div.text.strip()
            day_num = day_div.text.strip()
            month_num = datetime.strptime(month_name, '%B').month
            year = default_date.year
            date = datetime(year, month_num, int(day_num))
        else:
            date = default_date
    else:
        date = default_date
    sch_schs_div = soup.find('div', class_='indv-sch-schs')
    if sch_schs_div:
        if sch_schs_div.find('div', class_='indv-sch-sch-off'):
            return None
        else:
            sch_divs = sch_schs_div.find_all('div', class_='indv-sch-sch')
            shifts = []
            for sch_div in sch_divs:
                sten_div = sch_div.find('div', class_='indv-sch-sch-sten')
                if sten_div:
                    shift_times = sten_div.text.strip()
                    try:
                        start_time_str, end_time_str = shift_times.split('/')
                        start_time = parse_time_str(start_time_str)
                        end_time = parse_time_str(end_time_str)
                        shift_start = datetime.combine(date.date(), start_time.time())
                        shift_end = datetime.combine(date.date(), end_time.time())
                        if shift_end <= shift_start:
                            shift_end += timedelta(days=1)
                        shifts.append({
                            'Shift Date': date.date(),
                            'Start Time': shift_start,
                            'End Time': shift_end,
                            'Duration (Hours)': round((shift_end - shift_start).total_seconds() / 3600, 2)
                        })
                    except Exception as e:
                        print(f"Error parsing time '{shift_times}' on date {date.date()}: {e}")
                        if sys.stdin.isatty():
                            corrected = False
                            while not corrected:
                                user_input = input(f"Enter the start and end time for shift on {date.date()} (format HH:MMAM/PM - HH:MMAM/PM), or leave blank to skip: ")
                                if not user_input:
                                    print("Skipping this shift.")
                                    corrected = True
                                else:
                                    try:
                                        start_time_str, end_time_str = user_input.strip().split('-')
                                        start_time = datetime.strptime(start_time_str.strip(), '%I:%M%p')
                                        end_time = datetime.strptime(end_time_str.strip(), '%I:%M%p')
                                        shift_start = datetime.combine(date.date(), start_time.time())
                                        shift_end = datetime.combine(date.date(), end_time.time())
                                        if shift_end <= shift_start:
                                            shift_end += timedelta(days=1)
                                        shifts.append({
                                            'Shift Date': date.date(),
                                            'Start Time': shift_start,
                                            'End Time': shift_end,
                                            'Duration (Hours)': round((shift_end - shift_start).total_seconds() / 3600, 2)
                                        })
                                        corrected = True
                                    except Exception as e:
                                        print(f"Invalid input: {e}. Please try again.")
                        else:
                            print("Cannot prompt for input in non-interactive mode. Skipping this shift.")
                else:
                    continue
            return shifts if shifts else None
    else:
        return None

def parse_schedule(json_data):
    """
    Parses the entire schedule from the JSON data.

    Args:
        json_data (str): The JSON data as a string.

    Returns:
        list: A list of all shift dictionaries.
    """
    data = json.loads(json_data)
    result = []
    for record in data['records']:
        weekof = record['weekof']
        week_start_date = datetime.strptime(weekof, '%b-%d-%Y')
        for i in range(7):
            day_key = f'd{i}'
            if day_key in record:
                day_html = record[day_key]
                current_date = week_start_date + timedelta(days=i)
                day_shifts = parse_day(day_html, current_date)
                if day_shifts:
                    result.extend(day_shifts)
    return result

def output_to_excel(shifts, output_file):
    """
    Outputs the shifts to an Excel file.

    Args:
        shifts (list): The list of shift dictionaries.
        output_file (str): The path to the output Excel file.
    """
    df = pd.DataFrame(shifts)
    df['Start Time'] = df['Start Time'].dt.strftime('%Y-%m-%d %I:%M %p')
    df['End Time'] = df['End Time'].dt.strftime('%Y-%m-%d %I:%M %p')
    df.to_excel(output_file, index=False)
    print(f"Shifts have been successfully written to {output_file}")

def main():
    parser = argparse.ArgumentParser(description='Parse schedule JSON and output to Excel.')
    parser.add_argument('--in', dest='input_file', required=True, help='Input JSON file')
    parser.add_argument('--out', dest='output_file', required=True, help='Output Excel file')
    args = parser.parse_args()
    with open(args.input_file, 'r') as f:
        json_data = f.read()
    # Parser? I barely know her!
    shifts = parse_schedule(json_data)

    if shifts:
        output_to_excel(shifts, args.output_file)
    else:
        print("No shifts found in the schedule.")

if __name__ == '__main__':
    main()
