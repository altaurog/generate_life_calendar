"""
Color Palettes

source: https://colorbrewer2.org/#type=diverging&scheme=BrBG&n=5
"""
# pylint: disable=too-few-public-methods

colors = [
    [
        (166, 97, 26),
        (223, 194, 125),
        (245, 245, 245),
        (128, 205, 193),
        (1, 133, 113),
    ],
    [
        (77, 172, 38),
        (184, 225, 134),
        (247, 247, 247),
        (241, 182, 218),
        (208, 28, 139),
    ],
    [
        (123, 50, 148),
        (194, 165, 207),
        (247, 247, 247),
        (166, 219, 160),
        (0, 136, 55),
    ],
    [
        (94, 60, 153),
        (178, 171, 210),
        (247, 247, 247),
        (253, 184, 99),
        (230, 97, 1),
    ],
    [
        (5, 113, 176),
        (146, 197, 222),
        (247, 247, 247),
        (244, 165, 130),
        (202, 0, 32),
    ],
    [
        (64, 64, 64),
        (186, 186, 186),
        (255, 255, 255),
        (244, 165, 130),
        (202, 0, 32),
    ],
    [
        (44, 123, 182),
        (171, 217, 233),
        (255, 255, 191),
        (253, 174, 97),
        (215, 25, 28),
    ],
    [
        (26, 150, 65),
        (166, 217, 106),
        (255, 255, 191),
        (253, 174, 97),
        (215, 25, 28),
    ],
    [
        (43, 131, 186),
        (171, 221, 164),
        (255, 255, 191),
        (253, 174, 97),
        (215, 25, 28),
    ],
]


def as_float(rgb_int):
    "convert integer rgb values in range [0, 255] to float [0, 1]"
    return [val / 255 for val in rgb_int]


class Palette:
    "easy palette selection"

    def __init__(self, palette_id, reverse=False):
        self.palette_id = palette_id % len(colors)
        order = reversed if reverse else list
        self.colors = [(0, 0, 0)] + list(
            order([as_float(rgb) for rgb in colors[self.palette_id]])
        )

    def rgb(self, color):
        "get color from the palette"
        return self.colors[color % len(self.colors)]
