class ChessGame:
    def __init__(self):
        self.board = self.create_board()
        self.turn = "white"
        self.en_passant = None
        self.castling = {
            "white_kingside": True,
            "white_queenside": True,
            "black_kingside": True,
            "black_queenside": True
        }

    def create_board(self):
        return [
            ["br", "bn", "bb", "bq", "bk", "bb", "bn", "br"],
            ["bp", "bp", "bp", "bp", "bp", "bp", "bp", "bp"],
            ["", "", "", "", "", "", "", ""],
            ["", "", "", "", "", "", "", ""],
            ["", "", "", "", "", "", "", ""],
            ["", "", "", "", "", "", "", ""],
            ["wp", "wp", "wp", "wp", "wp", "wp", "wp", "wp"],
            ["wr", "wn", "wb", "wq", "wk", "wb", "wn", "wr"]
        ]

    def display_board(self):
        symbols = {
            "wp": "♙",
            "wr": "♖",
            "wn": "♘",
            "wb": "♗",
            "wq": "♕",
            "wk": "♔",
            "bp": "♟",
            "br": "♜",
            "bn": "♞",
            "bb": "♝",
            "bq": "♛",
            "bk": "♚",
            "": "."
        }

        print("\n    a b c d e f g h")
        print("   -----------------")

        for row in range(8):
            print(
                f"{8 - row} | " +
                " ".join(symbols[piece] for piece in self.board[row]) +
                f" | {8 - row}"
            )

        print("   -----------------")
        print("    a b c d e f g h\n")

    def position_to_coordinates(self, position):
        if len(position) != 2:
            return None

        file = position[0].lower()
        rank = position[1]

        if file not in "abcdefgh" or rank not in "12345678":
            return None

        column = ord(file) - ord("a")
        row = 8 - int(rank)

        return row, column

    def coordinates_to_position(self, row, column):
        return chr(column + ord("a")) + str(8 - row)

    def is_white(self, piece):
        return piece.startswith("w")

    def is_black(self, piece):
        return piece.startswith("b")

    def same_color(self, piece1, piece2):
        if piece1 == "" or piece2 == "":
            return False

        return piece1[0] == piece2[0]

    def opponent(self, color):
        return "black" if color == "white" else "white"

    def piece_belongs_to_turn(self, piece):
        if piece == "":
            return False

        if self.turn == "white":
            return self.is_white(piece)

        return self.is_black(piece)

    def is_inside_board(self, row, column):
        return 0 <= row < 8 and 0 <= column < 8

    def get_piece_moves(self, row, column, attack_only=False):
        piece = self.board[row][column]

        if piece == "":
            return []

        color = "white" if piece[0] == "w" else "black"
        piece_type = piece[1]

        moves = []

        if piece_type == "p":
            direction = -1 if color == "white" else 1
            start_row = 6 if color == "white" else 1

            next_row = row + direction

            if self.is_inside_board(next_row, column):
                if attack_only:
                    for dc in [-1, 1]:
                        target_col = column + dc

                        if self.is_inside_board(next_row, target_col):
                            moves.append((next_row, target_col))
                else:
                    if self.board[next_row][column] == "":
                        moves.append((next_row, column))

                        if row == start_row:
                            double_row = row + (2 * direction)

                            if self.board[double_row][column] == "":
                                moves.append((double_row, column))

                    for dc in [-1, 1]:
                        target_col = column + dc

                        if self.is_inside_board(next_row, target_col):
                            target = self.board[next_row][target_col]

                            if target != "" and not self.same_color(piece, target):
                                moves.append((next_row, target_col))

                            if self.en_passant == (next_row, target_col):
                                moves.append((next_row, target_col))

        elif piece_type == "n":
            knight_moves = [
                (-2, -1),
                (-2, 1),
                (-1, -2),
                (-1, 2),
                (1, -2),
                (1, 2),
                (2, -1),
                (2, 1)
            ]

            for dr, dc in knight_moves:
                nr = row + dr
                nc = column + dc

                if self.is_inside_board(nr, nc):
                    target = self.board[nr][nc]

                    if target == "" or not self.same_color(piece, target):
                        moves.append((nr, nc))

        elif piece_type in ["b", "r", "q"]:
            directions = []

            if piece_type in ["b", "q"]:
                directions += [
                    (-1, -1),
                    (-1, 1),
                    (1, -1),
                    (1, 1)
                ]

            if piece_type in ["r", "q"]:
                directions += [
                    (-1, 0),
                    (1, 0),
                    (0, -1),
                    (0, 1)
                ]

            for dr, dc in directions:
                nr = row + dr
                nc = column + dc

                while self.is_inside_board(nr, nc):
                    target = self.board[nr][nc]

                    if target == "":
                        moves.append((nr, nc))
                    else:
                        if not self.same_color(piece, target):
                            moves.append((nr, nc))

                        break

                    nr += dr
                    nc += dc

        elif piece_type == "k":
            king_moves = [
                (-1, -1),
                (-1, 0),
                (-1, 1),
                (0, -1),
                (0, 1),
                (1, -1),
                (1, 0),
                (1, 1)
            ]

            for dr, dc in king_moves:
                nr = row + dr
                nc = column + dc

                if self.is_inside_board(nr, nc):
                    target = self.board[nr][nc]

                    if target == "" or not self.same_color(piece, target):
                        moves.append((nr, nc))

            if not attack_only:
                if color == "white" and row == 7 and column == 4:
                    if self.can_castle("white", "kingside"):
                        moves.append((7, 6))

                    if self.can_castle("white", "queenside"):
                        moves.append((7, 2))

                elif color == "black" and row == 0 and column == 4:
                    if self.can_castle("black", "kingside"):
                        moves.append((0, 6))

                    if self.can_castle("black", "queenside"):
                        moves.append((0, 2))

        return moves

    def find_king(self, color):
        king = "wk" if color == "white" else "bk"

        for row in range(8):
            for column in range(8):
                if self.board[row][column] == king:
                    return row, column

        return None

    def square_attacked(self, row, column, by_color):
        for r in range(8):
            for c in range(8):
                piece = self.board[r][c]

                if piece == "":
                    continue

                if by_color == "white" and not self.is_white(piece):
                    continue

                if by_color == "black" and not self.is_black(piece):
                    continue

                moves = self.get_piece_moves(r, c, attack_only=True)

                if (row, column) in moves:
                    return True

        return False

    def is_in_check(self, color):
        king_position = self.find_king(color)

        if king_position is None:
            return True

        row, column = king_position

        return self.square_attacked(
            row,
            column,
            self.opponent(color)
        )

    def copy_board(self):
        return [row[:] for row in self.board]

    def restore_board(self, board):
        self.board = [row[:] for row in board]

    def make_temporary_move(self, start, end):
        sr, sc = start
        er, ec = end

        moving_piece = self.board[sr][sc]
        captured_piece = self.board[er][ec]

        self.board[er][ec] = moving_piece
        self.board[sr][sc] = ""

        return moving_piece, captured_piece

    def undo_temporary_move(self, start, end, moving_piece, captured_piece):
        sr, sc = start
        er, ec = end

        self.board[sr][sc] = moving_piece
        self.board[er][ec] = captured_piece

    def legal_moves(self, row, column):
        piece = self.board[row][column]

        if piece == "":
            return []

        color = "white" if piece[0] == "w" else "black"

        possible_moves = self.get_piece_moves(row, column)

        legal = []

        for move in possible_moves:
            old_board = self.copy_board()

            old_en_passant = self.en_passant

            self.perform_move(row, column, move[0], move[1], test=True)

            if not self.is_in_check(color):
                legal.append(move)

            self.restore_board(old_board)
            self.en_passant = old_en_passant

        return legal

    def can_castle(self, color, side):
        if color == "white":
            row = 7

            if side == "kingside":
                if not self.castling["white_kingside"]:
                    return False

                if self.board[row][7] != "wr":
                    return False

                if self.board[row][5] != "" or self.board[row][6] != "":
                    return False

                if self.is_in_check("white"):
                    return False

                if self.square_attacked(7, 5, "black"):
                    return False

                if self.square_attacked(7, 6, "black"):
                    return False

                return True

            if side == "queenside":
                if not self.castling["white_queenside"]:
                    return False

                if self.board[row][0] != "wr":
                    return False

                if (
                    self.board[row][1] != "" or
                    self.board[row][2] != "" or
                    self.board[row][3] != ""
                ):
                    return False

                if self.is_in_check("white"):
                    return False

                if self.square_attacked(7, 3, "black"):
                    return False

                if self.square_attacked(7, 2, "black"):
                    return False

                return True

        else:
            row = 0

            if side == "kingside":
                if not self.castling["black_kingside"]:
                    return False

                if self.board[row][7] != "br":
                    return False

                if self.board[row][5] != "" or self.board[row][6] != "":
                    return False

                if self.is_in_check("black"):
                    return False

                if self.square_attacked(0, 5, "white"):
                    return False

                if self.square_attacked(0, 6, "white"):
                    return False

                return True

            if side == "queenside":
                if not self.castling["black_queenside"]:
                    return False

                if self.board[row][0] != "br":
                    return False

                if (
                    self.board[row][1] != "" or
                    self.board[row][2] != "" or
                    self.board[row][3] != ""
                ):
                    return False

                if self.is_in_check("black"):
                    return False

                if self.square_attacked(0, 3, "white"):
                    return False

                if self.square_attacked(0, 2, "white"):
                    return False

                return True

        return False

    def perform_move(self, sr, sc, er, ec, test=False):
        piece = self.board[sr][sc]

        if piece == "":
            return

        captured = self.board[er][ec]

        self.board[er][ec] = piece
        self.board[sr][sc] = ""

        # En passant capture
        if piece[1] == "p":
            if self.en_passant == (er, ec) and captured == "":
                capture_row = er + (1 if piece[0] == "w" else -1)
                self.board[capture_row][ec] = ""

        # Castling
        if piece[1] == "k" and abs(ec - sc) == 2:
            if ec == 6:
                self.board[sr][5] = self.board[sr][7]
                self.board[sr][7] = ""
            else:
                self.board[sr][3] = self.board[sr][0]
                self.board[sr][0] = ""

        if not test:
            self.update_castling_rights(
                piece,
                sr,
                sc,
                er,
                ec,
                captured
            )

            self.en_passant = None

            if piece[1] == "p" and abs(er - sr) == 2:
                middle_row = (sr + er) // 2
                self.en_passant = (middle_row, sc)

            # Promotion
            if piece[1] == "p":
                if er == 0 or er == 7:
                    self.promote_pawn(er, ec, piece[0])

    def update_castling_rights(
        self,
        piece,
        sr,
        sc,
        er,
        ec,
        captured
    ):
        if piece == "wk":
            self.castling["white_kingside"] = False
            self.castling["white_queenside"] = False

        elif piece == "bk":
            self.castling["black_kingside"] = False
            self.castling["black_queenside"] = False

        elif piece == "wr":
            if sr == 7 and sc == 0:
                self.castling["white_queenside"] = False

            elif sr == 7 and sc == 7:
                self.castling["white_kingside"] = False

        elif piece == "br":
            if sr == 0 and sc == 0:
                self.castling["black_queenside"] = False

            elif sr == 0 and sc == 7:
                self.castling["black_kingside"] = False

        if captured == "wr":
            if er == 7 and ec == 0:
                self.castling["white_queenside"] = False

            elif er == 7 and ec == 7:
                self.castling["white_kingside"] = False

        elif captured == "br":
            if er == 0 and ec == 0:
                self.castling["black_queenside"] = False

            elif er == 0 and ec == 7:
                self.castling["black_kingside"] = False

    def promote_pawn(self, row, column, color):
        print("\nPawn promotion!")
        print("Choose: Q = Queen, R = Rook, B = Bishop, N = Knight")

        while True:
            choice = input("Promotion piece: ").strip().lower()

            if choice in ["q", "r", "b", "n"]:
                self.board[row][column] = color + choice
                break

            print("Invalid choice.")

    def make_move(self, start, end):
        start_coords = self.position_to_coordinates(start)
        end_coords = self.position_to_coordinates(end)

        if start_coords is None or end_coords is None:
            print("Invalid position.")
            return False

        sr, sc = start_coords
        er, ec = end_coords

        piece = self.board[sr][sc]

        if piece == "":
            print("There is no piece on that square.")
            return False

        if not self.piece_belongs_to_turn(piece):
            print("That is not your piece.")
            return False

        legal = self.legal_moves(sr, sc)

        if (er, ec) not in legal:
            print("Illegal move.")
            return False

        self.perform_move(sr, sc, er, ec)

        self.turn = self.opponent(self.turn)

        return True

    def has_legal_moves(self, color):
        for row in range(8):
            for column in range(8):
                piece = self.board[row][column]

                if piece == "":
                    continue

                if color == "white" and not self.is_white(piece):
                    continue

                if color == "black" and not self.is_black(piece):
                    continue

                if self.legal_moves(row, column):
                    return True

        return False

    def game_status(self):
        color = self.turn

        if self.is_in_check(color):
            if not self.has_legal_moves(color):
                return "checkmate"

            return "check"

        if not self.has_legal_moves(color):
            return "stalemate"

        return "normal"

    def play(self):
        print("\n==============================")
        print("       PYTHON CHESS")
        print("==============================")
        print("Enter moves like: e2 e4")
        print("Enter 'quit' to exit.")
        print("Enter 'restart' to restart.\n")

        while True:
            self.display_board()

            status = self.game_status()

            if status == "checkmate":
                winner = self.opponent(self.turn)
                print(f"CHECKMATE! {winner.capitalize()} wins!")
                break

            if status == "stalemate":
                print("STALEMATE! The game is a draw.")
                break

            if status == "check":
                print(f"{self.turn.capitalize()} is in CHECK!")

            print(f"{self.turn.capitalize()}'s turn.")

            command = input("Move: ").strip().lower()

            if command == "quit":
                print("Game ended.")
                break

            if command == "restart":
                self.__init__()
                continue

            parts = command.split()

            if len(parts) != 2:
                print("Enter moves in this format: e2 e4")
                continue

            start, end = parts

            self.make_move(start, end)


def main():
    while True:
        game = ChessGame()
        game.play()

        choice = input("\nPlay again? (y/n): ").strip().lower()

        if choice != "y":
            print("Thanks for playing!")
            break


if __name__ == "__main__":
    main()