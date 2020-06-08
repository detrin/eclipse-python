# -*- coding: utf-8 -*-
import sys
import time
import math
import numpy as np

from tile import Tile


class Stones:
    def __init__(self, down=Tile.P_WHITE):
        # 0 - white
        # 1 - Black
        self.short = [
            [[[1, 1], [0, 2]], [[5, 1], [6, 2]]],
            [[[1, 13], [0, 12]], [[5, 13], [6, 12]]],
        ]
        self.long = [
            [[[2, 0], [4, 0]], [[2, 2], [4, 2]], [[2, 4], [4, 4]]],
            [[[2, 14], [4, 14]], [[2, 12], [4, 12]], [[2, 10], [4, 10]]],
        ]
        self.big = [[3, 1], [3, 13]]

        self.short_moved = [[0, 0], [0, 0]]
        self.long_moved = [[0, 0, 0], [0, 0, 0]]
        self.big_moved = [0, 0]

        self.down = down
        self.up = 3 - down

        self.player_pos = [[0, 1] if down == 2 else [1, 0]]

    def stones2board(self):
        # Stone stages
        # 0 - Default
        # 1 - White
        # 2 - Black
        # Stone colour
        # 0 - Short
        # 1 - Long
        # 2 - Big
        board = [[None for y in range(15)] for x in range(7)]
        color_setup = [[2, 1], [1, 2]]
        for p_i in [0, 1]:
            stone_c = color_setup[self.down - 1][p_i]
            for piece in [0, 1]:
                for i in [0, 1]:
                    col, row = self.short[p_i][i][piece]
                    board[col][row] = Tile(stone_c, 0, 0, row, col)

                for i in [0, 1, 2]:
                    col, row = self.long[p_i][i][piece]
                    board[col][row] = Tile(stone_c, 1, 0, row, col)

            col, row = self.big[p_i]
            board[col][row] = Tile(stone_c, 2, 0, row, col)

        for col in range(7):
            for row in range(15):
                if board[col][row] is None:
                    board[col][row] = Tile(0, 0, 0, row, col)

        return board
