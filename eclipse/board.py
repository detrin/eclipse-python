# Python Standard Library imports
import tkinter as tk
import sys

from tile import Tile


class Board(tk.Tk):
    def __init__(self, init_stones, *args, **kwargs):

        # Initialize parent tk class
        tk.Tk.__init__(self, *args, **kwargs)

        # Save metadata
        self.title("Eclipse")
        self.resizable(False, False)
        self.configure(bg="#fff")

        # Save tracking variables
        self.tiles = {}
        self.stones = init_stones
        self.board = init_stones.stones2board()
        self.b_size_x, self.b_size_y = len(self.board), len(self.board[0])

        # Create column/row labels
        label_font = "Helvetica 16"
        label_bg = "#fff"
        label_fg = "#333"
        for i in range(self.b_size_y):
            row_label1 = tk.Label(
                self, text=i + 1, font=label_font, bg=label_bg, fg=label_fg
            )
            row_label1.grid(row=i + 1, column=0)
            row_label2 = tk.Label(
                self, text=i + 1, font=label_font, bg=label_bg, fg=label_fg
            )
            row_label2.grid(row=i + 1, column=self.b_size_x + 2)

        for i in range(self.b_size_x):
            col_label1 = tk.Label(
                self, text=chr(i + 97), font=label_font, bg=label_bg, fg=label_fg
            )
            col_label1.grid(row=0, column=i + 1)

            col_label2 = tk.Label(
                self, text=chr(i + 97), font=label_font, bg=label_bg, fg=label_fg
            )
            col_label2.grid(row=self.b_size_y + 2, column=i + 1)

        # Create grid canvas
        self.canvas = tk.Canvas(
            self, width=550, height=600, bg="#fff", highlightthickness=0
        )
        self.canvas.grid(
            row=1, column=1, columnspan=self.b_size_x, rowspan=self.b_size_y
        )

        # Create status label
        self.status = tk.Label(
            self,
            anchor="c",
            font=(None, 16),
            bg="#212121",
            fg="#fff",
            text="White player's turn",
        )
        self.status.grid(
            row=self.b_size_y + 3, column=0, columnspan=self.b_size_x + 3, sticky="ewns"
        )

        # Bind the drawing function and configure grid sizes
        self.canvas.bind("<Configure>", self.draw_tiles)
        self.columnconfigure(0, minsize=48)
        self.rowconfigure(0, minsize=48)
        self.columnconfigure(self.b_size_x + 2, minsize=48)
        self.rowconfigure(self.b_size_y + 2, minsize=48)
        self.rowconfigure(self.b_size_y + 3, minsize=48)

    # Public Methods #

    def add_click_handler(self, func):
        self.click_handler = func

    def set_status(self, text):
        self.status.configure(text=text)

    def set_status_color(self, bg=None, fg=None):
        self.status.configure(bg=bg, fg=fg)

    def draw_tiles(self, event=None, board=None):

        if board is not None:
            self.board = board

        # Delete old rectangles and save properties
        self.canvas.delete("tile")
        cell_width = int(self.canvas.winfo_width() / self.b_size_x)
        cell_height = int(self.canvas.winfo_height() / self.b_size_y)
        border_size = 4

        # Calculate pixel positions
        x1 = border_size / 2
        y1 = border_size / 2
        x2 = (self.b_size_x + 1) * cell_width - border_size / 2
        y2 = (self.b_size_y + 1) * cell_height - border_size / 2 - 4

        # Render background tile
        tile = self.canvas.create_rectangle(
            x1,
            y1,
            x2,
            y2,
            tags="tile",
            width=border_size,
            fill="#614b38",
            outline="#FFFFFF",
        )

        # Draw the rest
        self.draw_pieces()

    def draw_pieces(self, board=None):
        if board is not None:
            self.board = board

        self.canvas.delete("piece")
        cell_width = int(self.canvas.winfo_width() / self.b_size_x)
        cell_height = int((self.canvas.winfo_height() - 14) / self.b_size_y)
        border_piece = 1
        chain_width = 4
        chain_border = 1
        scale_size = 4
        outline_border = 4
        radius = [
            int(cell_height / 2) - scale_size,
            int(cell_height / 2),
            int(cell_height / 2) + scale_size,
        ]
        border_size = 20

        # Draw connections between stones
        moves_ind = []
        for p_i in [0, 1]:  # player order
            for stone_num in [0, 1]:
                moves_ind.append(
                    [self.stones.short_moved[p_i][stone_num], p_i, stone_num,]
                )
        moves_ind = sorted(moves_ind)

        for val, p_i, i in moves_ind:  # player order
            col, row = self.stones.short[p_i][i][0]
            xc1 = col * cell_width + border_size / 2 + cell_width / 2
            yc1 = row * cell_height + border_size / 2 + cell_height / 2
            col, row = self.stones.short[p_i][i][1]
            xc2 = col * cell_width + border_size / 2 + cell_width / 2
            yc2 = row * cell_height + border_size / 2 + cell_height / 2

            self.canvas.create_line(
                xc1,
                yc1,
                xc2,
                yc2,
                tags="piece",
                width=chain_width + chain_border,
                fill="#333333",
            )
            self.canvas.create_line(
                xc1, yc1, xc2, yc2, tags="piece", width=chain_width, fill="#777777"
            )

        moves_ind = []
        for p_i in [0, 1]:  # player order
            for stone_num in [0, 1, 2]:
                moves_ind.append(
                    [self.stones.long_moved[p_i][stone_num], p_i, stone_num,]
                )
        moves_ind = sorted(moves_ind)

        for val, p_i, i in moves_ind:  # player order
            col, row = self.stones.long[p_i][i][0]
            xc1 = col * cell_width + border_size / 2 + cell_width / 2
            yc1 = row * cell_height + border_size / 2 + cell_height / 2
            col, row = self.stones.long[p_i][i][1]
            xc2 = col * cell_width + border_size / 2 + cell_width / 2
            yc2 = row * cell_height + border_size / 2 + cell_height / 2

            self.canvas.create_line(
                xc1,
                yc1,
                xc2,
                yc2,
                tags="piece",
                width=chain_width + chain_border,
                fill="#333333",
            )
            self.canvas.create_line(
                xc1, yc1, xc2, yc2, tags="piece", width=chain_width, fill="#777777"
            )

        # Draw stones
        for col in range(self.b_size_x):
            for row in range(self.b_size_y):
                if (
                    (col + row) % 2 != 0
                    or (row == 0 and (col == 0 or col == 6))
                    or (row == 14 and (col == 0 or col == 6))
                ):
                    continue
                # Calculate pixel positions
                xc = col * cell_width + border_size / 2 + cell_width / 2
                yc = row * cell_height + border_size / 2 + cell_height / 2
                r = radius[self.board[col][row].stone_type]
                stone_colour, outline_color = self.board[col][row].get_tile_colors()
                shadow_colour = self.board[col][row].stone_shadow_hex

                if self.board[col][row].outline == Tile.O_NONE:
                    piece = self.canvas.create_oval(
                        xc - r,
                        yc - r,
                        xc + r,
                        yc + r,
                        tags="piece",
                        fill=stone_colour,
                        outline=shadow_colour,
                        width=border_piece,
                    )
                else:
                    piece = self.canvas.create_oval(
                        xc - r,
                        yc - r,
                        xc + r,
                        yc + r,
                        tags="piece",
                        fill=stone_colour,
                        outline=outline_color,
                        width=outline_border,
                    )

                self.canvas.tag_bind(
                    piece,
                    "<1>",
                    lambda event, row=row, col=col: self.click_handler(row, col),
                )

        self.update()
