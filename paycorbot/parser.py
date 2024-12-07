from bs4 import BeautifulSoup

class PaycorScheduleParser:
    """
    A parser class to extract schedule information from a Paycor page source.
    Attributes:
        driver: A web driver instance used to fetch the page source.
    Methods:
        parse_schedule():
            Parses the schedule from the page source provided by the driver.
        _parse_schedule(page_source):
            A static method that takes the HTML page source as input and returns
            a list of dictionaries containing schedule data with keys 'date', 'time', and 'hours'.
    """
    def __init__(self, driver):
        self.driver = driver

    @staticmethod
    def _parse_schedule(page_source):
        soup = BeautifulSoup(page_source, "html.parser")

        schedule_rows = soup.select("div.x-grid-item-container table")

        schedule_data = []
        for table in schedule_rows:
            rows = table.select("tr")
            for row in rows:
                cells = row.select("td")
                for cell in cells:
                    date = cell.select_one(".indv-sch-cell-date-dom")
                    time = cell.select_one(".indv-sch-sch-sten")
                    hours = cell.select_one(".indv-sch-sch-hrs")
                    if date and time and hours:
                        schedule_data.append({
                            "date": date.text,
                            "time": time.text,
                            "hours": hours.text
                        })

        return schedule_data

    def parse_schedule(self):
        """
        Parses the schedule from the current page source of the web driver.

        Returns:
            dict: A dictionary containing the parsed schedule information.
        """
        return self._parse_schedule(self.driver.page_source)
