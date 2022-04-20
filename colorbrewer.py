"""
Color Palettes
"""
# pylint: disable=too-few-public-methods

colors = [
    [
        (0, 0, 0),
        (166, 97, 26),
        (223, 194, 125),
        (245, 245, 245),
        (128, 205, 193),
        (1, 133, 113),
    ],
]


def as_float(rgb_int):
    "convert integer rgb values in range [0, 255] to float [0, 1]"
    return [val / 255 for val in rgb_int]


class Palette:
    "easy palette selection"

    def __init__(self, palette_id):
        self.palette_id = palette_id % len(colors)
        self.colors = [as_float(rgb) for rgb in colors[self.palette_id]]

    def rgb(self, color):
        "get color from the palette"
        return self.colors[color % len(self.colors)]
