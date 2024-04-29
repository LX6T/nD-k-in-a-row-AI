"""
game.py
author: CSE 415 course staff

This file provides a data type for the game state.
You should not modify this file.
"""
import copy
from dataclasses import dataclass
from functools import cached_property

"""
Use these globals below for good programming practices instead of hard coding 'X' or 'O' into your code.
"""
X_PIECE = 'X'
O_PIECE = 'O'
BLOCK_PIECE = '-'
EMPTY_PIECE = ' '


@dataclass
class GameState:
    """
    Data type for the game state. Contains the board, the next player to move, and k (pieces in a row to win).
    Because this is a dataclass, functions such as the constructor are automatically created despite not being shown.
    """
    board: list[list[list[list[str]]]]  # n-dimensional array of board pieces
    next_player: str
    k: int

    @cached_property
    def n(self):
        """
        The number of dimensions of the board.
        """
        return len(self.d)

    @cached_property
    def d(self):
        """
        The height of the board. The @cached_property decorator on this method means that you reference this as if it
        were a property, such as through state.h instead of state.h()
        """
        return [len(self.board),
                len(self.board[0]),
                len(self.board[0][0]),
                len(self.board[0][0][0])]

    @cached_property
    def directions(self):
        units = []
        for i in range(self.n):
            if self.d[i] >= self.k:
                units.append(i)

        directions = []
        n = len(units)

        direction = [0, 0, 0, 0]
        for i in range(n):
            u1 = units[i]
            direction[u1] = 1
            directions.append(direction.copy())
            for j in range(i + 1, n):
                u2 = units[j]
                for pm2 in range(-1, 2, 2):
                    direction[u2] = pm2
                    directions.append(direction.copy())
                    for k in range(j + 1, n):
                        u3 = units[k]
                        for pm3 in range(-1, 2, 2):
                            direction[u3] = pm3
                            directions.append(direction.copy())
                            for x in range(k + 1, n):
                                u4 = units[x]
                                for pm4 in range(-1, 2, 2):
                                    direction[u3] = pm4
                                    directions.append(direction.copy())
                                direction[u4] = 0
                        direction[u3] = 0
                direction[u2] = 0
            direction[u1] = 0
        return directions

    def is_valid_move(self, move: (int, int, int, int)) -> bool:
        """
        Test for if a move is allowed or not.
        :param move: Tuple of (x,y) coords of the desired move
        :return: True if valid, False if not
        """
        return (move[0] < self.d[0] and
                move[1] < self.d[1] and
                move[2] < self.d[2] and
                move[3] < self.d[3] and
                self.board[move[0]][move[1]][move[2]][move[3]] is EMPTY_PIECE)

    def make_move(self, move: (int, int, int, int)) -> "GameState":
        """
        Applies a move to the game board and returns the new state
        :param move: Tuple of (x,y) coords of the desired move
        :return: new state with the move applied
        """
        assert self.is_valid_move(move)
        new_board = copy.deepcopy(self.board)
        new_board[move[0]][move[1]][move[2]][move[3]] = self.next_player
        new_player = X_PIECE if self.next_player is O_PIECE else O_PIECE
        new_state = GameState(new_board, new_player, self.k)
        return new_state

    def is_valid_starting_point(self, point, direction):
        is_on_boundary = False
        max_steps = max(self.d[0], self.d[1], self.d[2], self.d[3])
        for i in range(self.n):
            if direction[i] == 1:
                max_steps = min(max_steps, (self.d[i] - point[i] - self.k) + 1)
            elif direction[i] == -1:
                max_steps = min(max_steps, (point[i] - self.k + 1) + 1)
            if (((point[i] == 0 and direction[i] == 1) or
                 (point[i] == self.d[i] - 1 and direction[i] == -1)) and
                    direction[i] != 0):
                is_on_boundary = True

        return (is_on_boundary and max_steps > 0), max_steps

    def winner(self) -> [str, None]:
        """
        Determines if any agent has won the game.
        :return: token of the winning player, 'draw', or None
        """

        # print(self.directions)
        # print(len(self.directions))

        empty_spaces = 0

        for direction in self.directions:
            # print()
            # print(direction)
            for i in range(self.d[0]):
                for j in range(self.d[1]):
                    for k in range(self.d[2]):
                        for x in range(self.d[3]):
                            if self.board[i][j][k][x] is EMPTY_PIECE:
                                empty_spaces += 1
                            valid, steps = self.is_valid_starting_point((i, j, k, x), direction)
                            if valid:
                                # print((i, j, k, x), steps)
                                for step in range(steps):
                                    x_pieces = 0
                                    o_pieces = 0
                                    for c in range(self.k):
                                        p = (i + direction[0] * (step + c),
                                             j + direction[1] * (step + c),
                                             k + direction[2] * (step + c),
                                             x + direction[3] * (step + c))
                                        value = self.board[p[0]][p[1]][p[2]][p[3]]
                                        if value == X_PIECE:
                                            x_pieces += 1
                                        elif value == O_PIECE:
                                            o_pieces += 1
                                        if x_pieces < c and o_pieces < c:
                                            break

                                    if x_pieces == self.k:
                                        return X_PIECE
                                    elif o_pieces == self.k:
                                        return O_PIECE

        if empty_spaces == 0:
            return 'draw'
        else:
            return None

    @classmethod
    def empty(cls, size: (int, int, int, int), k: int, first: str = X_PIECE):
        """
        Creates a new empty board. Because this is a class method, call this function by referring to the class instead
        of an instance of the class, such as GameState.empty() instead of state.empty()
        :param size: tuple of dimensions of the board
        :param k: pieces in a row needed to win
        :param first: whose turn it is to start. defaults to X
        :return: new board
        """
        assert k <= max(size)
        new_board = [[[[EMPTY_PIECE
                        for a in range(size[3])]
                       for b in range(size[2])]
                      for c in range(size[1])]
                     for d in range(size[0])]
        return GameState(new_board, first, k)

    @classmethod
    def tic_tac_toe(cls):
        return cls.empty((1, 1, 3, 3), 3)

    @classmethod
    def no_corners(cls):
        new_board = [[[['-', ' ', ' ', ' ', ' ', ' ', '-'],
                       [' ', ' ', ' ', ' ', ' ', ' ', ' '],
                       [' ', ' ', ' ', ' ', ' ', ' ', ' '],
                       [' ', ' ', ' ', ' ', ' ', ' ', ' '],
                       [' ', ' ', ' ', ' ', ' ', ' ', ' '],
                       [' ', ' ', ' ', ' ', ' ', ' ', ' '],
                       ['-', ' ', ' ', ' ', ' ', ' ', '-']]]]
        return GameState(new_board, X_PIECE, 5)

    @classmethod
    def no_corners_small(cls):
        new_board = [[[['-', ' ', ' ', ' ', '-'],
                       [' ', ' ', ' ', ' ', ' '],
                       [' ', ' ', ' ', ' ', ' '],
                       [' ', ' ', ' ', ' ', ' '],
                       ['-', ' ', ' ', ' ', '-']]]]
        return GameState(new_board, X_PIECE, 4)

    def __str__(self):
        s = '+--' + 4 * (self.d[0] - 1) * '-' + '-+\n'
        for row in self.board[0][0][0]:
            s = s + '| ' + ' | '.join(row) + ' |\n'
        s = s + '+--' + 4 * (self.d[0] - 1) * '-' + '-+\n'
        s = s + self.next_player + " to play next"
        return s

    def __repr__(self):
        return str(self)

    def copy(self):
        return GameState(copy.deepcopy(self.board), self.next_player, self.k)
