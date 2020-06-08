# -*- coding: utf-8 -*-
import sys
import time
import math

from board import Board
from tile import Tile
from stones import Stones


class Eclipse:
    def __init__(self, t_limit=60, c_player=Tile.P_WHITE):

        # Create initial board
        stones = Stones(down=c_player)
        self.stones = stones
        self.player_pos = [0, 1] if c_player == Tile.P_BLACK else [1, 0]
        board = stones.stones2board()

        # Save member variables
        self.b_size_x, self.b_size_y = len(board), len(board[0])
        self.t_limit = t_limit
        self.c_player = c_player
        self.board_view = Board(stones)
        self.board = board
        self.current_player = Tile.P_WHITE
        self.selected_tile = None
        self.valid_moves = []
        self.computing = False
        self.total_plies = 0
        self.constants = [1, 1, 0.1, 0.1]

        self.ply_depth = 3
        self.ab_enabled = True

        self.moves_map_short = [[-1, 1], [1, -1], [-1, -1], [1, 1], [0, 2], [0, -2]]
        self.moves_map_long = self.moves_map_short + [
            [-1, 3],
            [1, 3],
            [1, -3],
            [-1, -3],
            [2, 0],
            [-2, 0],
        ]

        self.w_goals = [t for row in board for t in row if t == Tile.T_WHITE]
        self.b_goals = [t for row in board for t in row if t == Tile.T_BLACK]

        if self.current_player == Tile.P_WHITE:
            self.board_view.set_status_color(bg="#000000", fg="#FFFFFF")
        else:
            self.board_view.set_status_color(bg="#FFFFFF", fg="#000000")
        self.board_view.draw_tiles()

        self.board_view.add_click_handler(self.tile_clicked)
        self.board_view.draw_tiles(board=self.board)  # Refresh the board

        if self.c_player != self.current_player:
            self.execute_computer_move()

        # Print initial program info
        print("Eclipse Solver Basic Information")
        print("==============================")
        print("Turn time limit:", self.t_limit)
        print("Max ply depth:", self.ply_depth)
        print()

        self.board_view.mainloop()  # Begin tkinter main loop

    def tile_clicked(self, row, col):

        if self.computing:  # Block clicks while computing
            return

        new_tile = self.board[col][row]

        # If we are selecting a friendly piece
        if new_tile.stone_colour == self.current_player:

            self.outline_tiles(None)  # Reset outlines

            # Outline the new and valid move tiles
            new_tile.outline = Tile.O_MOVED
            self.valid_moves = self.get_moves_at_tile(row, col)
            self.outline_tiles(self.valid_moves)

            # Update status and save the new tile
            self.board_view.set_status("Tile `" + str(new_tile) + "` selected")
            self.selected_tile = new_tile

            self.board_view.draw_tiles(board=self.board)  # Refresh the board

        # If we already had a piece selected and we are moving a piece
        elif self.selected_tile and new_tile in self.valid_moves:

            self.outline_tiles(None)  # Reset outlines
            self.move_piece(self.selected_tile, new_tile)  # Move the piece

            # Update status and reset tracking variables
            self.selected_tile = None
            self.valid_moves = []
            self.current_player = (
                Tile.P_WHITE if self.current_player == Tile.P_BLACK else Tile.P_BLACK
            )

            self.board_view.draw_tiles(board=self.board)  # Refresh the board

            # If there is a winner to the game
            winner = self.find_winner()
            if winner:
                self.board_view.set_status(
                    "The "
                    + ("black" if winner == Tile.P_BLACK else "white")
                    + " player has won!"
                )
                self.current_player = None

            elif self.current_player is not None:
                self.execute_computer_move()

        else:
            self.board_view.set_status("Invalid move 1 attempted")

    def minimax(
        self,
        depth,
        player_to_max,
        max_time,
        a=float("-inf"),
        b=float("inf"),
        maxing=True,
        prunes=0,
        boards=0,
    ):

        # Bottomed out base case
        if depth == 0 or self.find_winner() or time.time() > max_time:
            return self.utility_distance(player_to_max), None, prunes, boards

        # Setup initial variables and find moves
        best_move = None
        if maxing:
            best_val = float("-inf")
            moves = self.get_next_tiles(player_to_max)
        else:
            best_val = float("inf")
            moves = self.get_next_tiles(
                (Tile.P_WHITE if player_to_max == Tile.P_BLACK else Tile.P_BLACK)
            )

        # For each move
        for move in moves:
            # Bail out when we're out of time
            if time.time() > max_time:
                return best_val, best_move, prunes, boards

            # Move piece to the move outlined
            piece = move["from"].stone_colour
            move["from"].stone_colour = Tile.P_NONE
            move["to"].stone_colour = piece
            boards += 1

            # Recursively call self
            val, _, new_prunes, new_boards = self.minimax(
                depth - 1, player_to_max, max_time, a, b, not maxing, prunes, boards
            )
            prunes = new_prunes
            boards = new_boards

            # Move the piece back
            move["to"].stone_colour = Tile.P_NONE
            move["from"].stone_colour = piece

            if maxing and val > best_val:
                best_val = val
                best_move = (move["from"].loc, move["to"].loc)
                a = max(a, val)

            if not maxing and val < best_val:
                best_val = val
                best_move = (move["from"].loc, move["to"].loc)
                b = min(b, val)

            if self.ab_enabled and b <= a:
                return best_val, best_move, prunes + 1, boards

        return best_val, best_move, prunes, boards

    def execute_computer_move(self):

        # Print out search information
        current_turn = (self.total_plies // 2) + 1
        print("Turn", current_turn, "Computation")
        print("=================" + ("=" * len(str(current_turn))))
        print("Executing search ...", end=" ")
        sys.stdout.flush()

        # self.board_view.set_status("Computing next move...")
        self.computing = True
        self.board_view.update()
        max_time = time.time() + self.t_limit

        status = False
        repeat_minmax = 0
        while not status:
            # Execute minimax search
            start = time.time()
            val, move, prunes, boards = self.minimax(
                self.ply_depth+repeat_minmax, self.current_player, max_time
            )
            end = time.time()

            # Print search result stats
            print("complete")
            print("Time to compute:", round(end - start, 4))
            print("Total boards generated:", boards)
            print("Total prune events:", prunes)
            print("Value:", val)

            # Move the resulting piece
            self.outline_tiles(None)  # Reset outlines
            row, col = move[0]
            row_cent, col_cent = self.find_other_piece(row, col)
            move_from = self.board[col_cent][row_cent]
            row, col = move[1]
            move_to = self.board[col][row]
            print("Move:", move_from, move_to)
            status = self.move_piece(move_from, move_to)
            repeat_minmax += 1

        self.board_view.draw_tiles(board=self.board)  # Refresh the board

        winner = self.find_winner()
        if winner:
            self.board_view.set_status(
                "The "
                + ("black" if winner == Tile.P_BLACK else "white")
                + " player has won!"
            )
            self.board_view.set_status_color("#212121")
            self.current_player = None
            self.current_player = None

            print()
            print("Final Stats")
            print("===========")
            print("Final winner:", "black" if winner == Tile.P_BLACK else "white")
            print("Total # of plies:", self.total_plies)

        else:  # Toggle the current player
            self.current_player = (
                Tile.P_WHITE if self.current_player == Tile.P_BLACK else Tile.P_BLACK
            )

        self.computing = False
        print()

    def get_next_moves(self, player=1):

        moves = []  # All possible moves

        for stone_num in [0, 1]:
            for curr_tile, next_tile in self.find_moves_of_piece(
                player, Tile.ST_SHORT, stone_num
            ):
                move = {"from": curr_tile, "to": next_tile}
                moves.append(move)

        for stone_num in [0, 1, 2]:
            for curr_tile, next_tile in self.find_moves_of_piece(
                player, Tile.ST_LONG, stone_num
            ):
                move = {"from": curr_tile, "to": next_tile}
                moves.append(move)

        for curr_tile, next_tile in self.find_moves_of_piece(player, Tile.ST_BIG, 0):
            move = {"from": curr_tile, "to": next_tile}
            moves.append(move)

        return moves

    def get_next_tiles(self, player=1):
        moves = self.get_next_moves(player)
        tiles = []
        for move in moves:
            row, col = move["from"]
            tile_from = self.board[col][row]
            row, col = move["to"]
            tile_to = self.board[col][row]
            tile = {"from": tile_from, "to": tile_to}
            tiles.append(tile)
        return tiles

    def is_on_board(self, row, col):
        if (
            not (0 <= col <= 6)
            or not (0 <= row <= 14)
            or (col + row) % 2 != 0
            or (row == 0 and (col == 0 or col == 6))
            or (row == 14 and (col == 0 or col == 6))
        ):
            return False
        return True

    def tile_surrounding(self, row, col, stone_type=None):
        if stone_type is None:
            return
        moves = []
        if stone_type == Tile.ST_SHORT or stone_type == Tile.ST_BIG:
            for d_col, d_row in self.moves_map_short:
                if self.is_on_board(row + d_row, col + d_col):
                    moves.append([row + d_row, col + d_col])

        elif stone_type == Tile.ST_LONG:
            for d_col, d_row in self.moves_map_long:
                if self.is_on_board(row + d_row, col + d_col):
                    moves.append([row + d_row, col + d_col])
        return moves

    def line_intersect(self, line1, line2):
        pt1, pt2 = line1
        pt3, pt4 = line2
        Ax1, Ay1, Ax2, Ay2, Bx1, By1, Bx2, By2 = pt1 + pt2 + pt3 + pt4
        d = (By2 - By1) * (Ax2 - Ax1) - (Bx2 - Bx1) * (Ay2 - Ay1)
        if d:
            uA = ((Bx2 - Bx1) * (Ay1 - By1) - (By2 - By1) * (Ax1 - Bx1)) / d
            uB = ((Ax2 - Ax1) * (Ay1 - By1) - (Ay2 - Ay1) * (Ax1 - Bx1)) / d
        else:
            return False
        if not (0 <= uA <= 1 and 0 <= uB <= 1):
            return False

        return True

    def is_piece_blocked(self, player, stone_type, stone_num):
        p_place = self.player_pos[player - 1]
        other_player = 3 - player
        op_place = self.player_pos[other_player - 1]
        tile_fixed = False

        if stone_type == Tile.ST_SHORT:
            moved1 = self.stones.short_moved[p_place][stone_num]
            # col row
            line1 = self.stones.short[p_place][stone_num]
            for orther_stone_num in [0, 1]:
                line2 = self.stones.short[op_place][orther_stone_num]
                moved2 = self.stones.short_moved[op_place][orther_stone_num]
                tile_fixed |= self.line_intersect(line1, line2) and moved2 > moved1
            for orther_stone_num in [0, 1, 2]:
                line2 = self.stones.long[op_place][orther_stone_num]
                moved2 = self.stones.long_moved[op_place][orther_stone_num]
                tile_fixed |= self.line_intersect(line1, line2) and moved2 > moved1

        elif stone_type == Tile.ST_LONG:
            moved1 = self.stones.long_moved[p_place][stone_num]
            # col row
            line1 = self.stones.long[p_place][stone_num]
            for orther_stone_num in [0, 1]:
                line2 = self.stones.short[op_place][orther_stone_num]
                moved2 = self.stones.short_moved[op_place][orther_stone_num]
                tile_fixed |= self.line_intersect(line1, line2) and moved2 > moved1
            for orther_stone_num in [0, 1, 2]:
                line2 = self.stones.long[op_place][orther_stone_num]
                moved2 = self.stones.long_moved[op_place][orther_stone_num]
                tile_fixed |= self.line_intersect(line1, line2) and moved2 > moved1

        return tile_fixed

    def does_cross_chain(self, player, line1, own=True):
        p_place = self.player_pos[player - 1]
        other_player = 3 - player
        op_place = self.player_pos[other_player - 1]
        chain_crossed = False

        if own:
            places = [0, 1]
        else:
            places = [op_place]

        for p_i in places:
            for other_stone_num in [0, 1, 2]:
                line2 = self.stones.long[op_place][other_stone_num]
                chain_crossed |= self.line_intersect(line1, line2)

        return chain_crossed

    def find_moves_of_piece(self, player, stone_type, stone_num):
        p_place = self.player_pos[player - 1]
        if not self.is_piece_blocked(player, stone_type, stone_num):
            moves_possible = []
            if stone_type == Tile.ST_SHORT:
                for piece in [0, 1]:
                    col, row = self.stones.short[p_place][stone_num][piece]
                    moves_surrounding = self.tile_surrounding(row, col, stone_type)
                    for move_surrounding in moves_surrounding:
                        row2, col2 = move_surrounding
                        if self.board[col2][row2].stone_colour == Tile.P_NONE:
                            yield [row, col], [row2, col2]

            elif stone_type == Tile.ST_LONG:
                for piece in [0, 1]:
                    col, row = self.stones.long[p_place][stone_num][piece]
                    moves_surrounding = self.tile_surrounding(row, col, stone_type)
                    for move_surrounding in moves_surrounding:
                        row2, col2 = move_surrounding
                        if self.board[col2][row2].stone_colour == Tile.P_NONE:
                            yield [row, col], [row2, col2]

            elif stone_type == Tile.ST_BIG:
                col, row = self.stones.big[p_place]
                moves_surrounding = self.tile_surrounding(row, col, stone_type)
                for move_surrounding in moves_surrounding:
                    row2, col2 = move_surrounding
                    if self.board[col2][
                        row2
                    ].stone_colour == Tile.P_NONE and not self.does_cross_chain(
                        player, [[row, col], [row2, col2]], own=False
                    ):
                        yield [row, col], [row2, col2]

    def find_other_piece(self, row, col):
        p_place = self.player_pos[self.current_player - 1]
        player = self.board[col][row].stone_colour
        stone_type = self.board[col][row].stone_type

        row_cent, col_cent = None, None
        for piece in [0, 1]:
            for i in [0, 1]:
                col2, row2 = self.stones.short[p_place][i][piece]
                if row2 == row and col2 == col:
                    col_cent, row_cent = self.stones.short[p_place][i][1 - piece]

            for i in [0, 1, 2]:
                col2, row2 = self.stones.long[p_place][i][piece]
                if row2 == row and col2 == col:
                    col_cent, row_cent = self.stones.long[p_place][i][1 - piece]

        col2, row2 = self.stones.big[p_place]
        if row2 == row and col2 == col:
            col_cent, row_cent = row2, col2

        return row_cent, col_cent

    def get_moves_at_tile(self, row, col):
        p_place = self.player_pos[self.current_player - 1]
        moves_all = self.get_next_moves(self.current_player)
        moves = []

        row_cent, col_cent = self.find_other_piece(row, col)

        for move in moves_all:
            if move["from"][0] == row_cent and move["from"][1] == col_cent:
                row_sel, col_sel = move["to"]
                moves.append(self.board[col_sel][row_sel])
        return moves

    def get_tiles_at_tile(self, row, col):
        moves = self.get_moves_at_tile(row, col)
        tiles = []
        for move in moves:
            row, col = move
            tiles.append(self.board[col][row])
        return tiles

    def find_stone_by_move(self, row, col):
        for p_i in [0, 1]:
            for piece in [0, 1]:
                for i in [0, 1]:
                    col2, row2 = self.stones.short[p_i][i][piece]
                    if row == row2 and col == col2:
                        return p_i, Tile.ST_SHORT, i, piece

                for i in [0, 1, 2]:
                    col2, row2 = self.stones.long[p_i][i][piece]
                    if row == row2 and col == col2:
                        return p_i, Tile.ST_LONG, i, piece

            col2, row2 = self.stones.big[p_i]
            if row == row2 and col == col2:
                return p_i, Tile.ST_BIG, i, piece

    def move_piece(self, from_tile, to_tile):

        # Handle trying to move a non-existant piece and moving into a piece
        if from_tile.stone_colour == Tile.P_NONE or to_tile.stone_colour != Tile.P_NONE:
            self.board_view.set_status("Invalid move 2")
            return False
        """
        # Move piece
        to_tile.set_colour(from_tile.stone_colour)
        from_tile.set_colour(Tile.P_NONE)

        to_tile.stone_type, from_tile.stone_type = from_tile.stone_type, to_tile.stone_type

        to_tile.outline = Tile.O_NONE
        from_tile.outline = Tile.O_NONE
        """

        # Swap pieces
        row, col = from_tile.loc
        row2, col2 = to_tile.loc
        move = [col2, row2]
        player_pos, stone_type, stone_num, piece = self.find_stone_by_move(row, col)
        if stone_type == Tile.ST_SHORT:
            self.stones.short[player_pos][stone_num][piece] = move
            self.stones.short_moved[player_pos][stone_num] = time.time()
        elif stone_type == Tile.ST_LONG:
            self.stones.long[player_pos][stone_num][piece] = move
            self.stones.long_moved[player_pos][stone_num] = time.time()
        elif stone_type == Tile.ST_BIG:
            self.stones.big[player_pos][stone_num] = move
            self.stones.big_moved[player_pos][stone_num] = time.time()

        self.board = self.stones.stones2board()

        self.total_plies += 1

        if self.current_player == Tile.P_WHITE:
            self.board_view.set_status_color(bg="#000000", fg="#FFFFFF")
        else:
            self.board_view.set_status_color(bg="#FFFFFF", fg="#000000")
        self.board_view.set_status(
            "Piece moved from `"
            + str(from_tile)
            + "` to `"
            + str(to_tile)
            + "`, "
            + ("black's" if self.current_player == Tile.P_WHITE else "white's")
            + " turn..."
        )
        return True

    def find_winner(self):
        moves = []
        for move in self.find_moves_of_piece(Tile.P_WHITE, Tile.ST_BIG, 0):
            moves.append(move)
        if len(moves) == 0:
            return Tile.P_BLACK

        moves = []
        for move in self.find_moves_of_piece(Tile.P_BLACK, Tile.ST_BIG, 0):
            moves.append(move)
        if len(moves) == 0:
            return Tile.P_WHITE

        return False

    def outline_tiles(self, tiles=[], outline_type=Tile.O_SELECT):

        if tiles is None:
            tiles = [j for i in self.board for j in i]
            outline_type = Tile.O_NONE

        for tile in tiles:
            tile.outline = outline_type

    def utility_distance(self, player):
        def point_distance(p0, p1):
            return math.sqrt((p1[0] - p0[0]) ** 2 + (p1[1] - p0[1]) ** 2)

        values1, values2 = [], []
        p_place = self.player_pos[player - 1]
        other_player = 3 - player
        op_place = self.player_pos[other_player - 1]

        pt_target1 = self.stones.big[p_place]
        pt_target2 = self.stones.big[op_place]
        for col in range(self.b_size_x):
            for row in range(self.b_size_y):
                if (
                    (col + row) % 2 != 0
                    or (row == 0 and (col == 0 or col == 6))
                    or (row == 14 and (col == 0 or col == 6))
                ):
                    continue
                pt = [col, row]
                if self.board[col][row].stone_colour == other_player:
                    values1 += [point_distance(pt_target1, pt)]
                if self.board[col][row].stone_colour == player:
                    values2 += [point_distance(pt_target2, pt)]

        values1 = sorted(values1)
        values2 = sorted(values2)
        value1 = sum(values1[0:6])
        value2 = sum(values2[0:6])
        value3 = sum(values1)
        value4 = sum(values2)

        value = +self.constants[0] * value1
        value -= self.constants[1] * value2
        value += self.constants[2] * value3
        value -= self.constants[3] * value4

        if self.current_player == self.c_player:
            value *= -1

        return value


if __name__ == "__main__":

    eclipse = Eclipse()
