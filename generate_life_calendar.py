import argparse
import itertools
from datetime import datetime, timedelta

import cairo

DOC_WIDTH = 1872  # 26 inches
DOC_HEIGHT = 2880  # 40 inches
DOC_NAME = "life_calendar.pdf"

FONT = "Brocha"
BIGFONT_SIZE = 40
SMALLFONT_SIZE = 16
TINYFONT_SIZE = 14

DEFAULT_TITLE = "LIFE CALENDAR"

NUM_ROWS = 90
NUM_COLUMNS = 53  # Some years have 53 weeks.

Y_MARGIN = 144
BOX_MARGIN = 6

BOX_LINE_WIDTH = 1.5
BOX_SIZE = ((DOC_HEIGHT - (Y_MARGIN + 36)) / NUM_ROWS) - BOX_MARGIN
X_MARGIN = (DOC_WIDTH - ((BOX_SIZE + BOX_MARGIN) * NUM_COLUMNS)) / 2


def parse_date(date):
    formats = ["%d/%m/%Y", "%d-%m-%Y"]
    stripped = date.strip()

    for f in formats:
        try:
            ret = datetime.strptime(date, f)
        except:
            continue
        else:
            return ret

    raise ValueError("Incorrect date format: must be dd-mm-yyyy or dd/mm/yyyy")


def weeks(start_date):
    for c in itertools.count():
        yield start_date + timedelta(c * 7)


def x_position(week, day):
    return X_MARGIN + week * (BOX_SIZE + BOX_MARGIN) + day * BOX_SIZE / 7


def y_position(year):
    return Y_MARGIN + year * (BOX_SIZE + BOX_MARGIN)


class Calendar:
    def __init__(self, config):
        # Start on Monday (Monday is 0, Sunday is 6)
        self.num_years = config.num_years
        self.start_date = config.start_date - timedelta(config.start_date.weekday())
        self.end_date = self.start_date.replace(
            year=self.start_date.year + config.num_years
        )
        self.title = config.title

    def bounded_weeks(self, week_iter):
        predicate = lambda date: date < self.end_date
        return itertools.takewhile(predicate, week_iter)

    def positioned_weeks(self, week_iter):
        return map(self.position, week_iter)

    def position(self, date):
        isodate = date.isocalendar()
        year = isodate.year - self.start_date.year
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

    def draw_square(self, d, fillcolour=(1, 1, 1)):
        """
        Draws a square for year, week
        """
        pos_x = d["pos_x"]
        pos_y = d["pos_y"]
        self.ctx.set_line_width(BOX_LINE_WIDTH)
        self.ctx.rectangle(pos_x, pos_y, BOX_SIZE, BOX_SIZE)
        self.ctx.set_source_rgba(*fillcolour, 0.75)
        self.ctx.fill_preserve()
        self.ctx.set_source_rgba(0, 0, 0, 1)
        self.ctx.stroke()

    def center_text(self, pos_x, pos_y, box_width, box_height, label):
        text_width, text_height = self.text_size(label)
        self.ctx.move_to(
            pos_x + (box_width - text_width) / 2,
            pos_y + (box_height + text_height) / 2,
        )
        self.ctx.show_text(label)

    def draw_grid(self):
        """
        Draws the whole grid of 52x90 squares
        """
        self.ctx.set_font_size(TINYFONT_SIZE)
        self.ctx.select_font_face(
            FONT,
            cairo.FONT_SLANT_ITALIC,
            cairo.FONT_WEIGHT_NORMAL,
        )
        for d in self.positioned_weeks(self.bounded_weeks(weeks(self.start_date))):
            self.draw_square(d)

    def draw_months(self):
        months = [
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
        ref = datetime(2000, 1, 1)
        for i, label in enumerate(months):
            start = (datetime(2000, i + 1, 1) - ref).days
            end = (datetime(2000 + (i + 1) // 12, (i + 1) % 12 + 1, 1) - ref).days - 1
            x = x_position(*divmod(start, 7))
            y = y_position(0) - 2 * BOX_MARGIN
            width = x_position(*divmod(end, 7)) - x
            self.ctx.set_source_rgb(0, 0, 0)
            self.ctx.set_font_size(TINYFONT_SIZE)
            self.ctx.select_font_face(
                FONT,
                cairo.FONT_SLANT_NORMAL,
                cairo.FONT_WEIGHT_NORMAL,
            )
            self.center_text(x, y - BOX_SIZE - BOX_MARGIN, width, BOX_SIZE, label)
            if not i % 2:
                height = y_position(91) - y + 3 * BOX_MARGIN
                self.ctx.set_line_width(1)
                self.ctx.set_source_rgb(0.85, 0.85, 0.85)
                self.ctx.rectangle(x, y, width, height)
                self.ctx.fill()

    def label_years(self):
        self.ctx.set_source_rgb(0, 0, 0)
        self.ctx.set_font_size(TINYFONT_SIZE)
        self.ctx.select_font_face(
            FONT,
            cairo.FONT_SLANT_NORMAL,
            cairo.FONT_WEIGHT_NORMAL,
        )
        for n in range(self.num_years + 1):
            self.center_text(
                X_MARGIN / 3,
                y_position(n),
                X_MARGIN / 2,
                BOX_SIZE,
                str(n + self.start_date.year),
            )

    def render(self, filename):
        # Fill background with white
        surface = cairo.PDFSurface(filename, DOC_WIDTH, DOC_HEIGHT)
        self.ctx = cairo.Context(surface)

        self.ctx.set_source_rgb(1, 1, 1)
        self.ctx.rectangle(0, 0, DOC_WIDTH, DOC_HEIGHT)
        self.ctx.fill()

        self.ctx.select_font_face(
            FONT,
            cairo.FONT_SLANT_NORMAL,
            cairo.FONT_WEIGHT_BOLD,
        )
        self.ctx.set_source_rgb(0, 0, 0)
        self.ctx.set_font_size(BIGFONT_SIZE)
        self.center_text(0, 0, DOC_WIDTH, Y_MARGIN, self.title)

        self.draw_months()
        self.label_years()
        self.draw_grid()
        self.ctx.show_page()

    def text_size(self, text):
        return self.ctx.text_extents(text)[2:4]


def parse_args():
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
        help='number of years (default is "%d")' % NUM_ROWS,
        default=NUM_ROWS,
    )

    parser.add_argument(
        "-t",
        "--title",
        type=str,
        dest="title",
        help='Calendar title text (default is "%s")' % DEFAULT_TITLE,
        default=DEFAULT_TITLE,
    )

    return parser.parse_args()


def main():
    args = parse_args()
    calendar = Calendar(args)
    calendar.render(args.filename)
    print("Created %s" % args.filename)


if __name__ == "__main__":
    main()
