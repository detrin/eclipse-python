# -*- coding: utf-8 -*-
import sys

from eclipse import Eclipse
from tile import Tile

WHITE_OPTIONS = ["w", "white"]
BLACK_OPTIONS = ["b", "black"]

# Process and pass along command line parameters
if __name__ == "__main__":

    # Catch missing parameters
    if len(sys.argv) < 3:
        print("usage: main.py <t-limit> [<h-player>]")
        sys.exit(-1)

    # Unpack params into variables
    t_limit = sys.argv[1]
    h_player = sys.argv[2] if len(sys.argv) == 3 else None

    # Validate b_size and t_limit
    if not t_limit.isdigit():
        print("error: <t-limit> should be integer")
        sys.exit(-1)

    t_limit = int(t_limit)

    # Validate h_player
    if h_player is None:
        c_player = None

    else:
        h_player = h_player.lower()

        if h_player in WHITE_OPTIONS:
            c_player = Tile.P_WHITE
        elif h_player in BLACK_OPTIONS:
            c_player = Tile.P_BLACK
        else:
            print(
                "error: <h-player> should be ["
                + ", ".join(WHITE_OPTIONS + BLACK_OPTIONS)
                + "]"
            )
            sys.exit(-1)

    elcipse = Eclipse(t_limit, c_player)
