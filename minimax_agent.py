"""
minimax_agent.py
author: <YOUR NAME(s) HERE>
"""
import agent
import game
import time
import random


class MinimaxAgent(agent.Agent):
    def __init__(self, initial_state: game.GameState, piece: str):
        super().__init__(initial_state, piece)
        self.eval_calls = 0
        self.wrapup_time = 0.1
        self.silent = False

    def introduce(self):
        """
        returns a multi-line introduction string
        :return: intro string
        """
        return ("My name is Alpha Agent.\n" +
                "I was created by Alex Pullen and Ashley Fenton.\n" +
                "I'm ready to win K-in-a-Row.")

    def nickname(self):
        """
        returns a short nickname for the agent
        :return: nickname
        """
        return "alpha_agent"

    def choose_move(self, state: game.GameState, time_limit: float) -> (int, int):
        """
        Selects a move to make on the given game board. Returns a move
        :param state: current game state
        :param time_limit: time (in seconds) before you'll be cutoff and forfeit the game
        :return: move (x,y)
        """

        self.eval_calls = 0
        d = state.d
        k = state.k

        """Default best move is first available empty space"""
        best_move = None
        max_depth = 0
        for i in range(d[0]):
            for j in range(d[1]):
                for k in range(d[2]):
                    for x in range(d[3]):
                        if state.board[i][j][k][x] == game.EMPTY_PIECE:
                            max_depth += 1
                            if best_move is not None:
                                best_move = (i, j, k, x)

        """Limit the maximum search depth to 3"""
        max_depth = min(max_depth, 3)

        """Perform iterative deepening search until depth limit or time limit reached"""
        timeout = time.perf_counter() + time_limit if time_limit is not None else None
        depth = 1
        while depth <= max_depth:

            """Initialise Zobrist hash table"""
            z_table = [[random.getrandbits(32) for _ in range(2)] for _ in range(d[0] * d[1] * d[2] * d[3])]
            z_hashing = (z_table, dict(), 0)

            """Search for best value at current depth"""
            latest_time_limit = timeout - time.perf_counter() if timeout is not None else None
            move, value = self.minimax(state, depth, latest_time_limit, float("-inf"), float("inf"), z_hashing)

            if time_limit is None or time.perf_counter() < timeout - self.wrapup_time:

                """Full search complete, update best_move"""
                best_move = move
                best_value = value
                if not self.silent:
                    print(f"depth={depth}, best_move={best_move}, best_value={best_value}")

                """Search again, one layer deeper"""
                depth += 1

            else:
                """Time limit reached, exit search"""
                break

        if not self.silent:

            if timeout is not None:
                """Report remaining time"""
                print(f"Exited {round(timeout - time.perf_counter(), 4)} seconds remaining before timeout")

            """Report total number of static evaluations made"""
            print(f"Called static_eval() {self.eval_calls} times")

            self.print_board(state, best_move)

        return best_move

    def minimax(self, state: game.GameState, depth_remaining: int, time_limit: float = None,
                alpha: float = None, beta: float = None, z_hashing=None) -> ((int, int), float):
        """
        Uses minimax to evaluate the given state and choose the best action from this state. Uses the next_player of the
        given state to decide between min and max. Recursively calls itself to reach depth_remaining layers. Optionally
        uses alpha, beta for pruning, and/or z_hashing for zobrist hashing.
        :param state: State to evaluate
        :param depth_remaining: number of layers left to evaluate
        :param time_limit: argument for your use to make sure you return before the time limit. None means no time limit
        :param alpha: alpha value for pruning
        :param beta: beta value for pruning
        :param z_hashing: zobrist hashing data
        :return: move (x,y) or None, state evaluation
        """

        d = state.d
        a_piece = state.next_player

        """Generate Zobrist hash for the current board state"""
        (z_table, z_memory, z_key) = (None, None, None)
        if z_hashing is not None:
            (z_table, z_memory, z_key) = z_hashing

        if time_limit is not None and time_limit < self.wrapup_time:
            """Exit early if reached time limit"""
            return None, None
        elif depth_remaining == 0:
            """Return static evaluation if reached depth limit"""
            value = self.static_eval(state)
            if z_memory is not None:
                z_memory[z_key] = (None, value)
            return None, value
        else:
            """Otherwise do minimax"""

            timeout = None
            if time_limit is not None:
                timeout = time.perf_counter() + time_limit

            best_move = None
            best_value = float("-inf") if a_piece == game.X_PIECE else float("inf")

            # """Default best move is first available empty space"""
            # for i in range(w):
            #     for j in range(h):
            #         if state.board[i][j] == game.EMPTY_PIECE:
            #             best_move = (i, j)
            #             i = w - 1
            #             break

            for i in range(d[0]):
                for j in range(d[1]):
                    for k in range(d[2]):
                        for x in range(d[3]):
                            """Iterate until all spaces have been tried, exit early if time limit is reached"""
                            if timeout is None or time.perf_counter() < timeout - self.wrapup_time:

                                if state.board[i][j][k][x] == game.EMPTY_PIECE:

                                    """Play A in square (i,j,k,x,y), update Zobrist hash"""
                                    new_state = state.make_move((i, j, k, x))
                                    new_z_key = None
                                    if z_hashing is not None:
                                        z_index = 0 if a_piece == game.X_PIECE else 1
                                        board_index = (i * d[1] * d[2] * d[3] +
                                                       j * d[2] * d[3] +
                                                       k * d[3] +
                                                       x)
                                        new_z_key = z_key ^ z_table[board_index][z_index]

                                    if new_z_key is not None and new_z_key in z_memory:
                                        """If already calculated for this state, no need to search further"""
                                        (move, value) = z_memory[new_z_key]
                                    elif new_state.winner() == a_piece:
                                        """If A has won, no need to search further"""
                                        value = self.static_eval(new_state) / 10 ** (depth_remaining - 1)
                                    else:
                                        """Run minimax on new state"""
                                        new_time_limit = None
                                        if timeout is not None:
                                            new_time_limit = timeout - time.perf_counter()
                                        new_z_hashing = (z_table, z_memory, new_z_key)
                                        move, value = self.minimax(new_state, depth_remaining - 1, new_time_limit,
                                                                   alpha, beta, new_z_hashing)

                                    """Exit early if reached time limit"""
                                    if value is None:
                                        break

                                    """Update best move, alpha and beta"""
                                    if a_piece == game.X_PIECE:
                                        if value > best_value:
                                            best_move = (i, j, k, x)
                                            best_value = value
                                        if beta is not None and best_value > beta:
                                            return best_move, best_value
                                        elif alpha is not None:
                                            alpha = max(alpha, best_value)
                                    elif a_piece == game.O_PIECE:
                                        if value < best_value:
                                            best_move = (i, j, k, x)
                                            best_value = value
                                        if alpha is not None and best_value < alpha:
                                            return best_move, best_value
                                        elif beta is not None:
                                            beta = min(beta, best_value)

                            else:
                                """Exit early if reached time limit"""
                                break

            if z_hashing is not None:
                z_memory[z_key] = (best_move, best_value)

            return best_move, best_value

    def static_eval(self, state: game.GameState) -> float:
        """
        Evaluates the given state. States good for X should be larger that states good for O.
        :param state: state to evaluate
        :return: evaluation of the state
        """
        self.eval_calls += 1

        d = state.d

        value = 0
        win_value = 10.0 ** (state.k + 5)
        x_value = 0
        o_value = 0
        x_wins = 0
        o_wins = 0

        for direction in state.directions:
            for i in range(d[0]):
                for j in range(d[1]):
                    for k in range(d[2]):
                        for x in range(d[3]):
                            valid, steps = state.is_valid_starting_point((i, j, k, x), direction)
                            if valid:
                                # print((i, j, k, x, y), direction, steps)
                                for step in range(steps):
                                    x_pieces = 0
                                    o_pieces = 0
                                    x_blocked = False
                                    o_blocked = False
                                    for c in range(state.k):
                                        p = (i + direction[0] * (step + c),
                                             j + direction[1] * (step + c),
                                             k + direction[2] * (step + c),
                                             x + direction[3] * (step + c))
                                        value = state.board[p[0]][p[1]][p[2]][p[3]]
                                        if value == game.X_PIECE:
                                            x_pieces += 1
                                            o_blocked = True
                                        elif value == game.O_PIECE:
                                            o_pieces += 1
                                            x_blocked = True
                                        elif value == game.BLOCK_PIECE:
                                            x_blocked = True
                                            o_blocked = True

                                    if not x_blocked:
                                        if x_pieces == state.k:
                                            return win_value
                                        elif x_pieces != 0:
                                            x_value += 10 ** x_pieces
                                    if not o_blocked:
                                        if o_pieces == state.k:
                                            return -win_value
                                        elif o_pieces != 0:
                                            o_value += 10 ** o_pieces

        return x_value - o_value
