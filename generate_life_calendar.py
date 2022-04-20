"""
Produce a poster-size pdf representing a human life-span
as 90 rows of 52 or 53 weeks, one box for each week
"""
import argparse
import functools
import itertools
from datetime import datetime, timedelta

import cairo

import colors
import hebcal

# A2 paper
PAGE_WIDTH = 1190  # 26 inches
PAGE_HEIGHT = 1684  # 40 inches
DOC_NAME = "life_calendar.pdf"

FONT = "Brocha"
BIGFONT_SIZE = 24
SMALLFONT_SIZE = 11

DEFAULT_TITLE = "LIFE CALENDAR"

NUM_ROWS = 90
NUM_COLUMNS = 53  # Some years have 53 weeks.

BOX_MARGIN_FRAC = 0.175

TOP_MARGIN = 72
BOTTOM_MARGIN = 42
CHART_HEIGHT = PAGE_HEIGHT - TOP_MARGIN - BOTTOM_MARGIN
BOX_SIZE = CHART_HEIGHT / NUM_ROWS / (1 + BOX_MARGIN_FRAC)
BOX_MARGIN = BOX_SIZE * BOX_MARGIN_FRAC
BOX_LINE_WIDTH = 1
X_MARGIN = (PAGE_WIDTH - ((BOX_SIZE + BOX_MARGIN) * NUM_COLUMNS)) / 2

MONTHS = [
    "Jan",
    "Feb",
    "Mar",
    "Apr",
    "May",
    "Jun",
    "Jul",
    "Aug",
    "Sep",
    "Oct",
    "Nov",
    "Dec",
]


def parse_date(date):
    "parse a string into a date"
    for fmt in ["%d/%m/%Y", "%d-%m-%Y"]:
        try:
            return datetime.strptime(date.strip(), fmt)
        except ValueError:
            continue
    raise ValueError("Incorrect date format: must be dd-mm-yyyy or dd/mm/yyyy")


def weeks(start_date):
    "generate sequence of week start dates, starting with specified date"
    for num in itertools.count():
        yield start_date + timedelta(num * 7)


def x_position(week, day):
    "get horizontal position on the page for given week and day"
    return X_MARGIN + week * (BOX_SIZE + BOX_MARGIN) + day * BOX_SIZE / 7 + BOX_SIZE / 2


def y_position(year_num):
    "get vertical position on the page for a given year number (starting from 0)"
    return TOP_MARGIN + year_num * (BOX_SIZE + BOX_MARGIN)


class Calendar:
    """
    Calendar generator class

    Instantiated with a config (Namespace) object,
    which should have the following properties:

    title - calendar title
    num_years - number of years to display
    start_date - date on which calendar should start
    """

    def __init__(self, config):
        # Start on Monday (Monday is 0, Sunday is 6)
        self.start_date = config.start_date - timedelta(config.start_date.weekday())
        self.start_year = self.start_date.isocalendar().year
        self.end_date = self.start_date.replace(
            year=self.start_date.year + config.num_years
        ) - timedelta(1)
        self.num_years = self.end_date.isocalendar().year - self.start_year
        self.title = config.title
        surface = cairo.PDFSurface(config.filename, PAGE_WIDTH, PAGE_HEIGHT)
        self.ctx = cairo.Context(surface)
        self.palette = colors.Palette(config.color_palette, config.invert_palatte)
        self.jewish_calendar = config.jewish_calendar or config.israeli
        if self.jewish_calendar:
            try:
                self.hebcal = hebcal.HebrewCalendar(
                    self.start_date,
                    self.num_years,
                    config.israeli,
                )
            except FileNotFoundError:
                print("hebcal not found, Jewish calendar not available")
                self.jewish_calendar = False

    def bounded_weeks(self, week_iter):
        "take dates from iterator below the upper bound"
        predicate = lambda date: date < self.end_date
        return itertools.takewhile(predicate, week_iter)

    def positioned_weeks(self, week_iter):
        "convert dates to dicts with positioning data"
        return map(self.position, week_iter)

    def position(self, date):
        "determine positioning of a date"
        isodate = date.isocalendar()
        year = isodate.year - self.start_year
        week = isodate.week - 1
        offset = datetime(isodate.year, 1, 1).weekday()
        if offset > 3:
            # isocalendar counts first days towards previous year
            week += 1
        return {
            "date": date,
            "isodate": isodate,
            "year": year,
            "week": week,
            "offset": offset,
            "pos_x": x_position(week, -offset),
            "pos_y": y_position(year),
        }

    def annotated_weeks(self, week_iter):
        "add hebrew calendar annotations to week data"
        for week in week_iter:
            yield {"hebcal": self.hebcal.events(week["date"]), **week}

    def draw_holidays(self, week):
        "draw color boxes for holidays"
        day_width = BOX_SIZE / 7
        pos_x = week["pos_x"]
        pos_y = week["pos_y"]
        for event, day, num_days in week.get("hebcal", []):
            self.set_color(4 + event, 0.75)
            self.ctx.rectangle(
                pos_x + day * day_width,
                pos_y,
                num_days * day_width,
                BOX_SIZE,
            )
            self.ctx.fill()

    def draw_week(self, week):
        "draw a prepositioned box representing given year, week"
        pos_x = week["pos_x"]
        pos_y = week["pos_y"]
        self.ctx.set_line_width(BOX_LINE_WIDTH)
        self.ctx.rectangle(pos_x, pos_y, BOX_SIZE, BOX_SIZE)
        self.set_color(3, 0.75)
        self.ctx.fill()
        if self.jewish_calendar:
            self.draw_holidays(week)
        self.ctx.rectangle(pos_x, pos_y, BOX_SIZE, BOX_SIZE)
        self.set_color(0, 1)
        self.ctx.stroke()

    def draw_grid(self):
        "render the week squares"
        self.ctx.set_font_size(SMALLFONT_SIZE)
        self.ctx.select_font_face(
            FONT,
            cairo.FONT_SLANT_ITALIC,
            cairo.FONT_WEIGHT_NORMAL,
        )
        proc = [
            weeks,
            self.bounded_weeks,
            self.positioned_weeks,
        ]
        if self.jewish_calendar:
            proc.append(self.annotated_weeks)
        reducer = lambda agg, func: func(agg)
        for week in functools.reduce(reducer, proc, self.start_date):
            self.draw_week(week)

    def draw_months(self):
        "render labeled columns for months"
        ref = datetime(2000, 1, 1)
        pos_y = y_position(0) - BOX_MARGIN
        height = y_position(self.num_years + 1) - pos_y + 2 * BOX_MARGIN
        for i, label in enumerate(MONTHS):
            start = (datetime(2000, i + 1, 1) - ref).days
            end = (datetime(2000 + (i + 1) // 12, (i + 1) % 12 + 1, 1) - ref).days - 1
            pos_x = x_position(*divmod(start, 7))
            width = x_position(*divmod(end, 7)) - pos_x
            self.set_color(0, 1)
            self.ctx.set_font_size(SMALLFONT_SIZE)
            self.ctx.select_font_face(
                FONT,
                cairo.FONT_SLANT_NORMAL,
                cairo.FONT_WEIGHT_NORMAL,
            )
            self.center_text(
                pos_x, pos_y - BOX_SIZE - BOX_MARGIN, width, BOX_SIZE, label
            )
            if not i % 2:
                self.ctx.set_line_width(1)
                self.set_color(2, 1)
                self.ctx.rectangle(pos_x, pos_y, width, height)
                self.ctx.fill()

    def draw_year_labels(self):
        "render secular year labels in margin"
        self.set_color(0, 1)
        self.ctx.set_font_size(SMALLFONT_SIZE)
        self.ctx.select_font_face(
            FONT,
            cairo.FONT_SLANT_NORMAL,
            cairo.FONT_WEIGHT_NORMAL,
        )
        for year_num in range(self.num_years + 1):
            self.center_text(
                X_MARGIN / 2,
                y_position(year_num),
                X_MARGIN / 2,
                BOX_SIZE,
                str(year_num + self.start_year),
            )

    def draw_heb_year_labels(self):
        "render secular year labels in margin"
        self.set_color(0, 1)
        self.ctx.set_font_size(SMALLFONT_SIZE)
        self.ctx.select_font_face(
            FONT,
            cairo.FONT_SLANT_NORMAL,
            cairo.FONT_WEIGHT_NORMAL,
        )
        for year_num in range(-1, self.num_years + 1):
            self.center_text(
                PAGE_WIDTH - X_MARGIN,
                y_position(year_num) + BOX_SIZE / 2,
                X_MARGIN / 2,
                BOX_SIZE,
                hebcal.heb_year(year_num + self.start_date.year),
            )

    def draw_title(self):
        "render calendar title"
        self.ctx.select_font_face(
            FONT,
            cairo.FONT_SLANT_NORMAL,
            cairo.FONT_WEIGHT_BOLD,
        )
        self.set_color(1, 1)
        self.ctx.set_font_size(BIGFONT_SIZE)
        self.center_text(0, 0, PAGE_WIDTH, TOP_MARGIN * 2 / 3, self.title)

    def render(self):
        "render the calendar"
        self.draw_title()
        self.draw_months()
        self.draw_year_labels()
        if self.jewish_calendar:
            self.draw_heb_year_labels()
        self.draw_grid()
        self.ctx.show_page()

    def center_text(self, pos_x, pos_y, box_width, box_height, label):
        "render text on the page, centered within giving bounds"
        text_width, text_height = self.text_size(label)
        self.ctx.move_to(
            pos_x + (box_width - text_width) / 2,
            pos_y + (box_height + text_height) / 2,
        )
        self.ctx.show_text(label)

    def set_color(self, color_id, alpha=1):
        "set rgb and alpha using preselected palette"
        rgb = self.palette.rgb(color_id)
        self.ctx.set_source_rgba(*rgb, alpha)

    def text_size(self, text):
        "get size of text rendered with current font selection"
        return self.ctx.text_extents(text)[2:4]


def parse_args():
    "parse command line arguments"
    parser = argparse.ArgumentParser(
        description='\nGenerate a personalized "Life '
        ' Calendar", inspired by the calendar with the same name from the '
        "waitbutwhy.com store"
    )

    parser.add_argument(
        type=parse_date,
        dest="start_date",
        help="starting date; your birthday,"
        "in either dd/mm/yyyy or dd-mm-yyyy format",
    )

    parser.add_argument(
        "-f",
        "--filename",
        type=str,
        dest="filename",
        help="output filename",
        default=DOC_NAME,
    )

    parser.add_argument(
        "-y",
        "--num-years",
        type=int,
        dest="num_years",
        help=f'number of years (default is "{NUM_ROWS}")',
        default=NUM_ROWS,
    )

    parser.add_argument(
        "-t",
        "--title",
        type=str,
        dest="title",
        help=f'Calendar title text (default is "{DEFAULT_TITLE}")',
        default=DEFAULT_TITLE,
    )

    parser.add_argument(
        "-j",
        "--jewish-calendar",
        action="store_true",
        help="Include Hebrew calendar years and Jewish holidays",
    )

    parser.add_argument(
        "-i",
        "--israeli",
        action="store_true",
        help="Use Israeli Jewish holidays (implies -j)",
    )

    parser.add_argument(
        "-c",
        "--color-palette",
        type=int,
        help="Color palette (0 -- 8)",
        default=0,
    )

    parser.add_argument(
        "--invert-palatte",
        action="store_true",
        help="Invert palatte",
    )

    return parser.parse_args()


def main():
    "entry point: parse cli args and render calendar"
    args = parse_args()
    calendar = Calendar(args)
    calendar.render()
    print(f"Created {args.filename}")


if __name__ == "__main__":
    main()
