"""
Annotate weeks with Hebrew calendar events
"""
# pylint: disable=too-few-public-methods

import itertools
import subprocess
from datetime import datetime, timedelta

holiday = (
    "Chanukah",
    "Shushan Purim",
    "Pesach",
    "Shavuot",
    "Rosh Hashana",
    "Yom Kippur",
    "Sukkot",
)

major = holiday[2:]


def heb_year(secular_year):
    "get hebrew year at end of secular year"
    cmd = ["hebcal", "-dh", "12", "31", str(secular_year)]
    proc = subprocess.run(cmd, check=True, encoding="utf-8", capture_output=True)
    return proc.stdout.split()[-1]


class HebrewCalendar:
    "Hebrew Calendar"

    def __init__(self, start_date, num_years):
        cmd = [
            "hebcal",
            "-g",
            "-i",
            "--no-modern",
            "--years",
            str(num_years + 2),
            str(start_date.year),
        ]
        proc = subprocess.run(cmd, check=True, encoding="utf-8", capture_output=True)
        self.dates = dict(read_hebcal_output(proc.stdout.splitlines()))

    def events(self, date):
        "get events for days of week beginning on date"
        events = [classify(self.dates.get(date + timedelta(d))) for d in range(7)]
        return list(coalesce(events))


def read_hebcal_output(lines):
    "split and filter lines from hebcal output"
    for line in lines:
        datestr, description = line.split(" ", 1)
        date = datetime.strptime(datestr, "%Y-%m-%d")
        if description.startswith(holiday):
            yield (date, description)


def classify(description):
    "classify a calendar description as minor (0) or major (1)"
    return int(description.startswith(major)) if description else None


def coalesce(events):
    "combine holidays, returns iter of (classification, start day, num days)"
    for grouper, group in itertools.groupby(enumerate(events), lambda v: v[1]):
        if grouper is not None:
            days = list(group)
            yield grouper, days[0][0], len(days)
