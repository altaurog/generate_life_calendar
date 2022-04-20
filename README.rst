Personalised Life Calendar Generator
====================================

This is a fork of `Erik Nyquist’s Life Calendar repo`_.  It contains a
python script for generating a pdf `Life Calendar`_, such as can be found
on Tim Urban's website www.waitbutwhy.com.  Each box on the calendar
represents a week, and each row of boxes represents a year.

The script takes your birthday as an argument, and generates a .pdf file.
The weeks always start on Monday (mainly because the isocalendar weeks
implemented by the Python standard library start on Monday).

What’s Different About This Fork
--------------------------------

This fork is a significant refactor of the upstream code, bordering on a
rewrite, with several added features:

* Building on Morten Fyhn Amundsen’s fork, which accounts for the fact that
  some years have 53 weeks, the boxes are shifted to correctly align week
  days and dates.

* The months of the year are displayed as columns behind the weeks,
  so it is much easier to identify dates.

* Output pdf format is A2 paper

* The output now has some color, several color palettes are provided.

* There is an option to show the Hebrew calendar year in addition to the
  Gregorian calendar, with Jewish holidays marked on the calendar.

.. _Erik Nyquist’s Life Calendar repo:
   https://github.com/eriknyquist/generate_life_calendar

.. _Life Calendar: https://store.waitbutwhy.com/collections/life-calendars

.. _Morten Fyhn Amundsen’s fork:
  https://github.com/mortenfyhn/generate_life_calendar


Dependencies
------------

* `PyCairo <https://pypi.python.org/pypi/pycairo>`_

* `hebcal <https://github.com/hebcal/hebcal>`_ is required for Hebrew calendar years
  and Jewish holidays.

Usage
------
::

  usage: generate_life_calendar.py [-h] [-f FILENAME] [-y NUM_YEARS] [-t TITLE] [-j] [-i]
                                   [-c COLOR_PALETTE] [--invert-palatte]
                                   start_date

  Generate a personalized "Life Calendar", inspired by the calendar with the same name from the
  waitbutwhy.com store

  positional arguments:
    start_date            starting date; your birthday,in either dd/mm/yyyy or dd-mm-yyyy format

  optional arguments:
    -h, --help            show this help message and exit
    -f FILENAME, --filename FILENAME
                          output filename
    -y NUM_YEARS, --num-years NUM_YEARS
                          number of years (default is "90")
    -t TITLE, --title TITLE
                          Calendar title text (default is "LIFE CALENDAR")
    -j, --jewish-calendar
                          Include Hebrew calendar years and Jewish holidays
    -i, --israeli         Use Israeli Jewish holidays (implies -j)
    -c COLOR_PALETTE, --color-palette COLOR_PALETTE
                          Color palette (0 -- 8)
    --invert-palatte      Invert palatte

License
--------
Upstream carries an Apache 2.0 license.  This is arguably a derivative,
albeit a now distant one, so I guess this carries the upstream license.
To the extent that an open source license can apply to a set of rgb colors,
the color palettes are available under `this Apache-like license`_.

.. _this Apache-like license: https://colorbrewer2.org/export/LICENSE.txt
