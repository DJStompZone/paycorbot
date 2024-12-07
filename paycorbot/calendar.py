import json
import sys
import re
from datetime import datetime, timedelta
import argparse

from bs4 import BeautifulSoup
import pandas as pd

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
    date = extract_date(soup, default_date)
    sch_schs_div = soup.find('div', class_='indv-sch-schs')
    if not sch_schs_div or sch_schs_div.find('div', class_='indv-sch-sch-off'):
        return None
    return extract_shifts(sch_schs_div, date)

def extract_date(soup, default_date):
    """
    Extracts a date from a BeautifulSoup object.

    This function searches for a specific date format within the provided
    BeautifulSoup object and returns a datetime object representing that date.
    If the date cannot be found, it returns the provided default date.

    Args:
        soup (BeautifulSoup): A BeautifulSoup object containing the HTML to search.
        default_date (datetime): A datetime object to return if the date cannot be found.

    Returns:
        datetime: A datetime object representing the extracted date, or the default date if not found.
    """
    date_div = soup.find('div', class_='indv-sch-cell-date')
    if date_div:
        month_div = date_div.find('div', class_='indv-sch-cell-date-mon')
        day_div = date_div.find('div', class_='indv-sch-cell-date-dom')
        if month_div and day_div:
            month_name = month_div.text.strip()
            day_num = day_div.text.strip()
            month_num = datetime.strptime(month_name, '%B').month
            year = default_date.year
            return datetime(year, month_num, int(day_num))
    return default_date

def extract_shifts(sch_schs_div, date):
    """
    Extracts shift information from the provided HTML division.

    Args:
        sch_schs_div (BeautifulSoup object): The HTML division containing individual shift schedules.
        date (str): The date for which the shifts are being extracted.

    Returns:
        list: A list of shifts extracted from the HTML division, or None if no shifts are found.
    """
    sch_divs = sch_schs_div.find_all('div', class_='indv-sch-sch')
    shifts = []
    for sch_div in sch_divs:
        sten_div = sch_div.find('div', class_='indv-sch-sch-sten')
        if sten_div:
            shift_times = sten_div.text.strip()
            shift = parse_shift_times(shift_times, date)
            if shift:
                shifts.append(shift)
    return shifts if shifts else None

def parse_shift_times(shift_times, date):
    """
    Parses the shift times and returns a dictionary with shift details.

    Args:
        shift_times (str): A string containing the start and end times of the shift, separated by a '/'.
        date (datetime): A datetime object representing the date of the shift.

    Returns:
        dict: A dictionary containing the following keys:
            - 'Shift Date': The date of the shift.
            - 'Start Time': The start time of the shift as a datetime object.
            - 'End Time': The end time of the shift as a datetime object.
            - 'Duration (Hours)': The duration of the shift in hours, rounded to two decimal places.
        None: If an error occurs during parsing, returns None and handles the error.

    Raises:
        Exception: If an error occurs during parsing, it is handled by handle_shift_parsing_error function.
    """
    try:
        start_time_str, end_time_str = shift_times.split('/')
        start_time = parse_time_str(start_time_str)
        end_time = parse_time_str(end_time_str)
        shift_start = datetime.combine(date.date(), start_time.time())
        shift_end = datetime.combine(date.date(), end_time.time())
        if shift_end <= shift_start:
            shift_end += timedelta(days=1)
        return {
            'Shift Date': date.date(),
            'Start Time': shift_start,
            'End Time': shift_end,
            'Duration (Hours)': round((shift_end - shift_start).total_seconds() / 3600, 2)
        }
    except Exception as e:
        handle_shift_parsing_error(e, shift_times, date)
        return None

def handle_shift_parsing_error(e, shift_times, date):
    """
    Handles errors encountered while parsing shift times.

    This function prints an error message and, if running in an interactive terminal,
    prompts the user to manually enter the start and end times for the shift. If the
    user provides valid input, it returns a dictionary with the shift details.

    Args:
        e (Exception): The exception that was raised during parsing.
        shift_times (str): The original shift times string that caused the error.
        date (datetime): The date for which the shift times are being parsed.

    Returns:
        dict: A dictionary containing the shift details if the user provides valid input.
              The dictionary includes the following keys:
              - 'Shift Date': The date of the shift.
              - 'Start Time': The start time of the shift as a datetime object.
              - 'End Time': The end time of the shift as a datetime object.
              - 'Duration (Hours)': The duration of the shift in hours, rounded to two decimal places.
              
    Raises:
        None: This function handles all exceptions internally and does not raise any.
    """
    print(f'Error parsing time "{shift_times}" on date {date.date()}: {e}')
    if sys.stdin.isatty():
        corrected = False
        while not corrected:
            user_input = input(f'Enter the start and end time for shift on {date.date()} (format HH:MMAM/PM - HH:MMAM/PM), or leave blank to skip: ')
            if not user_input:
                print('Skipping this shift.')
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
                    return {
                        'Shift Date': date.date(),
                        'Start Time': shift_start,
                        'End Time': shift_end,
                        'Duration (Hours)': round((shift_end - shift_start).total_seconds() / 3600, 2)
                    }
                except Exception as ex:
                    print(f"Invalid input: {ex}. Please try again.")
    else:
        print('Cannot prompt for input in non-interactive mode. Skipping this shift.')

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


class ScheduleDay:
    def __init__(self, date, time, hours):
        self.date = date
        self.time = time
        self.hours = hours

    def __str__(self):
        return f"Date: {self.date.text}, Time: {self.time.text}, Hours: {self.hours.text}"

def parse_raw_markup(page_source):
    soup = BeautifulSoup(page_source, "html.parser")
    schedule_rows = soup.select("div.x-grid-item-container table")
    days = []

    for table in schedule_rows:
        rows = table.select("tr")
        for row in rows:
            cells = row.select("td")
            for cell in cells:
                date = cell.select_one(".indv-sch-cell-date-dom")
                time = cell.select_one(".indv-sch-sch-sten")
                hours = cell.select_one(".indv-sch-sch-hrs")
                if date and time and hours:
                    days.append(ScheduleDay(date, time, hours))
    for day in days:
        print(day)



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
