import datetime
import itertools
import argparse
import sys
import os
import cairo
import math

DOC_WIDTH = 1872   # 26 inches
DOC_HEIGHT = 2880  # 40 inches
DOC_NAME = "life_calendar.pdf"

KEY_NEWYEAR_DESC = "First week of the new year"
KEY_BIRTHDAY_DESC = "Week of your birthday"

XAXIS_DESC = "Weeks of the year"
YAXIS_DESC = "Years of your life"

FONT = "Brocha"
BIGFONT_SIZE = 40
SMALLFONT_SIZE = 16
TINYFONT_SIZE = 14

DEFAULT_TITLE = "LIFE CALENDAR"

NUM_ROWS = 90
NUM_COLUMNS = 53  # Some years have 53 weeks.

Y_MARGIN = 144
BOX_MARGIN = 6

BOX_LINE_WIDTH = 3
BOX_SIZE = ((DOC_HEIGHT - (Y_MARGIN + 36)) / NUM_ROWS) - BOX_MARGIN
X_MARGIN = (DOC_WIDTH - ((BOX_SIZE + BOX_MARGIN) * NUM_COLUMNS)) / 2

BIRTHDAY_COLOUR = (0.5, 0.5, 0.5)
NEWYEAR_COLOUR = (0.8, 0.8, 0.8)

ARROW_HEAD_LENGTH = 36
ARROW_HEAD_WIDTH = 8

def parse_date(date):
    formats = ['%d/%m/%Y', '%d-%m-%Y']
    stripped = date.strip()

    for f in formats:
        try:
            ret = datetime.datetime.strptime(date, f)
        except:
            continue
        else:
            return ret

    raise ValueError("Incorrect date format: must be dd-mm-yyyy or dd/mm/yyyy")

def weeks(start_date):
    for c in itertools.count():
        try:
            yield start_date + datetime.timedelta(c * 7)
        except Exception as exc:
            raise RuntimeError(f'{exc} at {c}')


class Calendar:

    def __init__(self, start_date, title):
        # Start on Sunday
        self.start_date = start_date - datetime.timedelta(start_date.weekday() - 1)
        self.end_date = self.start_date.replace(year=self.start_date.year + 90)
        self.title = title

    def weeks(self):
        yield from itertools.takewhile(
            lambda date: date < self.end_date,
            weeks(self.start_date),
        )

    def get_box_pos(self, date):
        """
        convert year-week into x-y coordinates
        """
        isodate = date.isocalendar()
        year = isodate.year - self.start_date.year
        week = isodate.week - 1
        offset = (date - datetime.datetime(isodate.year, 1, 1)).days % 7
        pos_x = X_MARGIN + week * (BOX_SIZE + BOX_MARGIN) + offset * BOX_SIZE / 7
        pos_y = Y_MARGIN + year * (BOX_SIZE + BOX_MARGIN)
        return pos_x, pos_y

    def draw_square(self, date, fillcolour=(1, 1, 1)):
        """
        Draws a square for year, week
        """
        pos_x, pos_y = self.get_box_pos(date)
        self.ctx.set_line_width(BOX_LINE_WIDTH)
        self.ctx.set_source_rgb(0, 0, 0)
        self.ctx.move_to(pos_x, pos_y)

        self.ctx.rectangle(pos_x, pos_y, BOX_SIZE, BOX_SIZE)
        self.ctx.stroke_preserve()

        self.ctx.set_source_rgb(*fillcolour)
        self.ctx.fill()

    def draw_grid(self):
        """
        Draws the whole grid of 52x90 squares
        """
        self.ctx.set_font_size(TINYFONT_SIZE)
        self.ctx.select_font_face(FONT, cairo.FONT_SLANT_ITALIC, cairo.FONT_WEIGHT_NORMAL)
        for d in self.weeks():
            self.draw_square(d)


    def render(self, filename):
        # Fill background with white
        surface = cairo.PDFSurface (filename, DOC_WIDTH, DOC_HEIGHT)
        self.ctx = cairo.Context(surface)

        self.ctx.set_source_rgb(1, 1, 1)
        self.ctx.rectangle(0, 0, DOC_WIDTH, DOC_HEIGHT)
        self.ctx.fill()

        self.ctx.select_font_face(FONT, cairo.FONT_SLANT_NORMAL,
            cairo.FONT_WEIGHT_BOLD)
        self.ctx.set_source_rgb(0, 0, 0)
        self.ctx.set_font_size(BIGFONT_SIZE)
        w, h = self.text_size(self.title)
        self.ctx.move_to((DOC_WIDTH / 2) - (w / 2), (Y_MARGIN / 2) - (h / 2))
        self.ctx.show_text(self.title)

        self.draw_grid()
        self.ctx.show_page()


    def text_size(self, text):
        return self.ctx.text_extents(text)[2:4]


def parse_args():
    parser = argparse.ArgumentParser(description='\nGenerate a personalized "Life '
        ' Calendar", inspired by the calendar with the same name from the '
        'waitbutwhy.com store')

    parser.add_argument(type=parse_date, dest='date', help='starting date; your birthday,'
        'in either dd/mm/yyyy or dd-mm-yyyy format')

    parser.add_argument('-f', '--filename', type=str, dest='filename',
        help='output filename', default=DOC_NAME)

    parser.add_argument('-t', '--title', type=str, dest='title',
        help='Calendar title text (default is "%s")' % DEFAULT_TITLE,
        default=DEFAULT_TITLE)

    return parser.parse_args()


def main():
    args = parse_args()
    calendar = Calendar(args.date, args.title)
    calendar.render(args.filename)
    print('Created %s' % args.filename)


if __name__ == "__main__":
    main()
