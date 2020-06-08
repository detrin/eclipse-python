# -*- coding: utf-8 -*-


class Tile:

    # Goal constants
    T_NONE = 0
    T_WHITE = 1
    T_BLACK = 2

    # Piece constants
    P_NONE = 0
    P_WHITE = 1
    P_BLACK = 2

    # Outline constants
    O_NONE = 0
    O_SELECT = 1
    O_MOVED = 2

    # Stone types
    ST_NONE = -1
    ST_SHORT = 0
    ST_LONG = 1
    ST_BIG = 2

    def __init__(self, stone_colour=0, stone_type=-1, outline=0, row=0, col=0):
        self.stone_type = stone_type
        self.stone_colour = stone_colour
        self.outline = outline

        # Find appropriate tile color
        self.stone_colours = [
            ("#DBBFA0", "#614b38"),  # Normal tiles
            ("#FFFFFF", "#333333"),  # ("#dcdcdc", "#b0b0b0"),  # White goal tiles
            ("#000000", "#AAAAAA"),  # ("#353535", "#626262")   # Black goal tiles
        ]
        self.stone_colour_hex = self.stone_colours[self.stone_colour][0]
        self.stone_shadow_hex = self.stone_colours[self.stone_colour][1]

        self.row = row
        self.col = col
        self.loc = (row, col)

    def get_tile_colors(self):
        # Find appropriate outline color
        outline_colours = [self.stone_colour_hex, "yellow", "#1100BB"]  # TODO: Change
        outline_colour = outline_colours[self.outline]

        return self.stone_colour_hex, outline_colour

    def set_colour(self, colour):
        self.stone_colour = colour
        self.stone_colour_hex = self.stone_colours[self.stone_colour][0]
        self.stone_shadow_hex = self.stone_colours[self.stone_colour][1]

    def __str__(self):
        return chr(self.loc[1] + 97) + str(self.loc[0] + 1)

    def __repr__(self):
        return chr(self.loc[1] + 97) + str(self.loc[0] + 1)
