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

def get_box_pos(year, week):
    """
    convert year-week into x-y coordinates
    """
    offset = BOX_SIZE + BOX_MARGIN
    return X_MARGIN + week * offset, Y_MARGIN + year * offset

def get_week_number(date):
    return date.isocalendar()[1] - 1

def weeks_in_year(year):
    def p(year):
        return (year + math.floor(year/4.) - math.floor(year/100.) + math.floor(year/400.)) % 7
    return 53 if (p(year) == 4 or p(year - 1) == 3) else 52

class Calendar:

    def __init__(self, start_date, title):
        # Back up to the last monday
        self.start_date = start_date - datetime.timedelta(start_date.weekday())
        self.title = title

    def draw_square(self, year, week, fillcolour=(1, 1, 1)):
        """
        Draws a square for year, week
        """
        pos_x, pos_y = get_box_pos(year, week)
        self.ctx.set_line_width(BOX_LINE_WIDTH)
        self.ctx.set_source_rgb(0, 0, 0)
        self.ctx.move_to(pos_x, pos_y)

        self.ctx.rectangle(pos_x, pos_y, BOX_SIZE, BOX_SIZE)
        self.ctx.stroke_preserve()

        self.ctx.set_source_rgb(*fillcolour)
        self.ctx.fill()

    def text_size(self, text):
        _, _, width, height, _, _ = self.ctx.text_extents(text)
        return width, height

    def draw_row_label(self, date):
        """
        draw label for the row
        """
        year = date.year - self.start_date.year
        pos_x, pos_y = get_box_pos(year, 0)
        # Generate string for current date
        self.ctx.set_source_rgb(0, 0, 0)
        date_str = date.strftime('%Y')
        w, h = self.text_size(date_str)

        # Draw it in front of the current row
        self.ctx.move_to(pos_x - w - BOX_SIZE,
            pos_y + ((BOX_SIZE / 2) + (h / 2)))
        self.ctx.show_text(date_str)

    def get_row_boxes(self, date):
        """
        get boxes to draw for row
        """
        start = 0 if date.year != self.start_date.year else get_week_number(self.start_date)
        end = weeks_in_year(date.year)
        for week in range(start, end):
            d = datetime.date(date.year, 1, 1) + datetime.timedelta(weeks=week)
            yield week, d.month % 2

    def draw_row(self, date):
        """
        Draws a row of squares, one per week of the year
        If start_date and date are in the same year, then skip squares for weeks before start_date.
        Draw a 53rd square for years with 53 weeks.
        """
        for week, shade in self.get_row_boxes(date):
            color = (0.9, 0.9, 0.9) if shade else (1, 1, 1)
            self.draw_square(date.year - self.start_date.year, week, color)

    def draw_grid(self):
        """
        Draws the whole grid of 52x90 squares
        """
        date = self.start_date
        pos_x = X_MARGIN / 4
        pos_y = pos_x

        # Draw the key for box colours
        self.ctx.set_font_size(TINYFONT_SIZE)
        self.ctx.select_font_face(FONT, cairo.FONT_SLANT_NORMAL,
            cairo.FONT_WEIGHT_NORMAL)

        # draw week numbers above top row
        self.ctx.set_font_size(TINYFONT_SIZE)
        self.ctx.select_font_face(FONT, cairo.FONT_SLANT_NORMAL,
            cairo.FONT_WEIGHT_NORMAL)

        pos_x = X_MARGIN
        pos_y = Y_MARGIN
        for i in range(NUM_COLUMNS):
            text = str(i + 1)
            w, h = self.text_size(text)
            self.ctx.move_to(pos_x + (BOX_SIZE / 2) - (w / 2), pos_y - BOX_SIZE)
            self.ctx.show_text(text)
            pos_x += BOX_SIZE + BOX_MARGIN

        self.ctx.set_font_size(TINYFONT_SIZE)
        self.ctx.select_font_face(FONT, cairo.FONT_SLANT_ITALIC,
            cairo.FONT_WEIGHT_NORMAL)

        for i in range(NUM_ROWS):

            self.draw_row_label(date)
            self.draw_row(date)

            # Increment y position and current date by 1 row/year
            date += datetime.timedelta(weeks=weeks_in_year(date.year))

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

        # Draw 52x90 grid of squares
        self.draw_grid()
        self.ctx.show_page()


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
