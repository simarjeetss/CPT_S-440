import copy
import random
import time
import numpy as np
import pygame

from board import Board


class Game:

    def __init__(self, player_1_type='real', player_2_type='real', window=False, search_depth=4,
                 nnets=(None, None), time_delay=0, ai_decision_temperature=0.05, window_scale=0.84):
        self.board = Board()
        self.use_window = window
        if player_1_type == "real" or player_2_type == "real":
            self.print_rules()
            self.use_window = True
        self.search_depth = search_depth
        self.nnets = nnets
        self.ai_decision_temperature = ai_decision_temperature
        self.time_delay = time_delay
        self.player_1_type = player_1_type
        self.player_2_type = player_2_type
        self.white_player_type = self.player_1_type
        self.black_player_type = self.player_2_type
        self.WHITE_PLAYER = 1
        self.BLACK_PLAYER = 2
        self.player_1_color = self.WHITE_PLAYER
        self.player_2_color = self.BLACK_PLAYER
        self.current_player = self.WHITE_PLAYER
        self.current_player_type = self.white_player_type
        # game ends in a draw if both players don't capture pieces for 10 moves
        self.moves_without_captured_piece_and_without_pawn_moves = 0
        if self.use_window:
            from window import Window
            self.window = Window(self.board, scale=window_scale)
            self.window.update_window(current_player=self.current_player)
        else:
            self.time_delay = 0

    def game_loop(self, n_games=1):
        p1_wins = 0
        p2_wins = 0
        draws = 0
        board_states_of_a_game = [[copy.copy(self.board.field)], [copy.copy(self.board.field)]]
        n_moves = 0
        n_games_to_play = n_games
        while n_games_to_play != 0:
            winner = 0
            while winner == 0:
                move = self.get_move()
                winner = self.do_move(move)
                n_moves += 1
                if n_games_to_play == 1 or n_games_to_play == 2:
                    if self.player_1_color == self.WHITE_PLAYER:
                        board_states_of_a_game[0].append(copy.copy(self.board.field))
                    else:
                        board_states_of_a_game[1].append(copy.copy(self.board.field))
            if self.use_window and self.player_1_type != "ai_evaluation":
                self.window.check_if_new_game()
            if winner == self.player_1_color:
                p1_wins += 1
            elif winner == self.player_2_color:
                p2_wins += 1
            elif winner == 3:
                draws += 1
            n_games_to_play -= 1
            self.start_new_game()
        average_game_length = round(n_moves / n_games, 1)
        return p1_wins, p2_wins, draws, board_states_of_a_game, average_game_length

    def print_rules(self):
        print("----------------------------------")
        print("---------------Rules---------------")
        print("----------------------------------")
        print("same rules as in normal chess except:")
        print("5*5 board")
        print("you are not forced to save yourself from check ...")
        print("... but it is wise --> otherwise, your king can be captured")
        print("no double pawn move")
        print("no en passant")
        print("no castling")
        print("pawns can only promote to a queen")
        print("----------------------------------")

    def print_game_result_info_in_console(self, winner):
        print("----------------------------------")
        if winner == self.WHITE_PLAYER:
            print("Weiß hat gewonnen!")
        elif winner == self.BLACK_PLAYER:
            print("Schwarz hat gewonnen!")
        elif winner == 3:
            print("Unentschieden, da 20 Züge lang keine Einheit geschlagen wurde!")
        print("----------------------------------")

    def start_new_game(self):
        # reset countable variables
        self.current_player = self.WHITE_PLAYER
        # switch who starts
        old_white_player_type = self.white_player_type
        old_black_player_type = self.black_player_type
        self.white_player_type = old_black_player_type
        self.black_player_type = old_white_player_type
        self.player_1_color = 3 - self.player_1_color
        self.player_2_color = 3 - self.player_2_color

        self.current_player_type = self.white_player_type
        self.moves_without_captured_piece_and_without_pawn_moves = 0
        # reset board
        self.board.reset_board()
        if self.use_window:
            self.window.update_window(current_player=self.current_player)

    def get_piece_positions_of_player(self, field=None, player=None):
        """
        returns the positions of all the pieces of the player
        uses self.current_player when no player is provided and self.board.field array when no field array is provided
        """
        if field is None:
            field = self.board.field
        if player == None:
            player = self.current_player
        piece_positions = []
        for i in range(self.board.board_size):
            for j in range(self.board.board_size):
                piece = field[i][j]
                if (player == self.WHITE_PLAYER and piece in self.board.WHITE_PIECES) or (player == self.BLACK_PLAYER and piece in self.board.BLACK_PIECES):
                    piece_positions.append([j, i])
        return piece_positions

    def get_all_legal_moves(self, current_player_piece_positions, field=None):
        """
        refers to self.board.field array when no other field array is provided
        returns a list of all legal moves in the format [(from_j, from_i, to_j, to_i), (...), ...]
        """

        if len(current_player_piece_positions) == 0:
            print("Verloren, keine Einheiten mehr")
        else:
            legal_moves = []
            WHITE_PIECES = self.board.WHITE_PIECES
            BLACK_PIECES = self.board.BLACK_PIECES
            EMPTY_FIELD = self.board.EMPTY_FIELD

            if field is None:
                field = self.board.field
            for piece in range(len(current_player_piece_positions)):
                from_j, from_i = current_player_piece_positions[piece][0], current_player_piece_positions[piece][1]
                piece_type = field[from_i][from_j]

                if piece_type == self.board.WHITE_PAWN:
                    if from_i - 1 >= 0:
                        if from_j - 1 >= 0:
                            if field[from_i - 1][from_j - 1] in BLACK_PIECES:
                                legal_moves.append((from_j, from_i, from_j - 1, from_i - 1))
                        if from_j + 1 <= 4:
                            if field[from_i - 1][from_j + 1] in BLACK_PIECES:
                                legal_moves.append((from_j, from_i, from_j + 1, from_i - 1))
                        if field[from_i - 1][from_j] == EMPTY_FIELD:
                            legal_moves.append((from_j, from_i, from_j, from_i - 1))

                elif piece_type == self.board.BLACK_PAWN:
                    if from_i + 1 <= 4:
                        if from_j - 1 >= 0:
                            if field[from_i + 1][from_j - 1] in WHITE_PIECES:
                                legal_moves.append((from_j, from_i, from_j - 1, from_i + 1))
                        if from_j + 1 <= 4:
                            if field[from_i + 1][from_j + 1] in WHITE_PIECES:
                                legal_moves.append((from_j, from_i, from_j + 1, from_i + 1))
                        if field[from_i + 1][from_j] == EMPTY_FIELD:
                            legal_moves.append((from_j, from_i, from_j, from_i + 1))

                elif piece_type == self.board.WHITE_KNIGHT or piece_type == self.board.BLACK_KNIGHT:
                    for k in ((-1, -2), (-1, 2), (1, -2), (1, 2), (-2, -1), (-2, 1), (2, -1), (2, 1)):
                        if 0 <= from_j + k[0] <= 4 and 0 <= from_i + k[1] <= 4:  # if on board
                            if piece_type == self.board.WHITE_KNIGHT and field[from_i + k[1]][from_j + k[0]] not in WHITE_PIECES:
                                legal_moves.append((from_j, from_i, from_j + k[0], from_i + k[1]))
                            elif piece_type == self.board.BLACK_KNIGHT and field[from_i + k[1]][from_j + k[0]] not in BLACK_PIECES:
                                legal_moves.append((from_j, from_i, from_j + k[0], from_i + k[1]))

                elif (piece_type == self.board.WHITE_BISHOP or piece_type == self.board.BLACK_BISHOP or piece_type == self.board.WHITE_QUEEN
                      or piece_type == self.board.BLACK_QUEEN or piece_type == self.board.WHITE_ROOK or piece_type == self.board.BLACK_ROOK):
                    if (piece_type == self.board.WHITE_BISHOP or piece_type == self.board.BLACK_BISHOP or
                            piece_type == self.board.WHITE_QUEEN or piece_type == self.board.BLACK_QUEEN):
                        for direktion in ((-1, -1), (-1, 1), (1, -1), (1, 1)):
                            for distance in range(1, 5):
                                if 0 <= from_j + direktion[0] * distance <= 4 and 0 <= from_i + direktion[1] * distance <= 4:  # if on board
                                    if (piece_type in WHITE_PIECES and field[from_i + direktion[1] * distance][from_j + direktion[0] * distance]
                                            not in WHITE_PIECES):  # if own white pieces aren't in the way
                                        legal_moves.append((from_j, from_i, from_j + direktion[0] * distance, from_i + direktion[1] * distance))
                                        if field[from_i + direktion[1] * distance][from_j + direktion[0] * distance] != EMPTY_FIELD:  # if opponent piece is captured
                                            break
                                    elif (piece_type in BLACK_PIECES and field[from_i + direktion[1] * distance][from_j + direktion[0] * distance]
                                          not in BLACK_PIECES):  # if own black pieces aren't in the way
                                        legal_moves.append((from_j, from_i, from_j + direktion[0] * distance, from_i + direktion[1] * distance))
                                        if field[from_i + direktion[1] * distance][
                                            from_j + direktion[0] * distance] != EMPTY_FIELD:  # if opponent piece is captured
                                            break
                                    else:
                                        break
                                else:
                                    break
                    if (piece_type == self.board.WHITE_ROOK or piece_type == self.board.BLACK_ROOK or
                            piece_type == self.board.WHITE_QUEEN or piece_type == self.board.BLACK_QUEEN):
                        for direktion in ((0, -1), (0, 1), (-1, 0), (1, 0)):
                            for distance in range(1, 5):
                                if 0 <= from_j + direktion[0] * distance <= 4 and 0 <= from_i + direktion[1] * distance <= 4:  # if on board
                                    if (piece_type in WHITE_PIECES and field[from_i + direktion[1] * distance][from_j + direktion[0] * distance]
                                            not in WHITE_PIECES):  # if own white pieces aren't in the way
                                        legal_moves.append((from_j, from_i, from_j + direktion[0] * distance, from_i + direktion[1] * distance))
                                        if field[from_i + direktion[1] * distance][from_j + direktion[0] * distance] != EMPTY_FIELD:  # if opponent piece is captured
                                            break
                                    elif (piece_type in BLACK_PIECES and field[from_i + direktion[1] * distance][from_j + direktion[0] * distance]
                                          not in BLACK_PIECES):  # if own black pieces aren't in the way
                                        legal_moves.append((from_j, from_i, from_j + direktion[0] * distance, from_i + direktion[1] * distance))
                                        if field[from_i + direktion[1] * distance][from_j + direktion[0] * distance] != EMPTY_FIELD:  # if opponent piece is captured
                                            break
                                    else:
                                        break
                                else:
                                    break
                elif piece_type == self.board.WHITE_KING or piece_type == self.board.BLACK_KING:
                    for step in ((-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)):
                        if 0 <= from_j + step[0] <= 4 and 0 <= from_i + step[1] <= 4:  # if on board
                            if piece_type == self.board.WHITE_KING and field[from_i + step[1]][from_j + step[0]] not in WHITE_PIECES:  # if own white pieces aren't in the way
                                legal_moves.append((from_j, from_i, from_j + step[0], from_i + step[1]))
                            elif piece_type == self.board.BLACK_KING and field[from_i + step[1]][
                                from_j + step[0]] not in BLACK_PIECES:  # if own white pieces aren't in the way
                                legal_moves.append((from_j, from_i, from_j + step[0], from_i + step[1]))
            return legal_moves