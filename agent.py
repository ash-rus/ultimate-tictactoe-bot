import math
import numpy as np
import time
from collections import defaultdict
import random
from game_logic import check_for_capture, check_for_end, get_valid_indices, get_next_subboard, print_ultimate_board

class UltimateTicTacToeState():
    def __init__(self, board, allowed_subboards, captured_subboards, player_turn):
        self.board = board
        self.allowed_subboards = allowed_subboards
        self.captured_subboards = captured_subboards
        self.player_turn = player_turn

    def get_legal_actions(self):
        return get_valid_indices(self.board, self.allowed_subboards, self.captured_subboards)


    def is_game_over(self):
        if check_for_end(self.captured_subboards) != -1:
            return True
        return False

    def game_result(self, root_player):
        winner = check_for_end(self.captured_subboards)
        if winner == root_player:
            return 1
        elif winner == 0 or winner == -1:
            return 0
        else:
            return -1


    def move(self, action):
        if isinstance(action, int):
            subboard_index = action // 9
            cell_index = action % 9
        else:
            subboard_index, cell_index = action

        new_board = [sub[:] for sub in self.board]
        row, col = divmod(cell_index, 3)
        new_board[subboard_index][cell_index] = self.player_turn

        new_captured_subboards = self.captured_subboards[:]
        captured = check_for_capture(new_board[subboard_index])
        if captured != 0:
            new_captured_subboards[subboard_index] = captured

        new_allowed_subboards = get_next_subboard(
            subboard_index * 9 + cell_index,
            new_board,
            set(i for i, v in enumerate(new_captured_subboards) if v != 0)
        )
        if new_allowed_subboards is None:
            new_allowed_subboards = []

        return UltimateTicTacToeState(
            new_board,
            new_allowed_subboards,
            new_captured_subboards,
            3 - self.player_turn
        )



class MonteCarloTreeSearchNode():
    def __init__(self, state, parent=None, parent_action=None):
        self.state = state
        self.parent = parent
        self.root_player = state.player_turn if parent is None else parent.root_player
        self.parent_action = parent_action
        self.children = []
        self._number_of_visits = 0
        self._results = defaultdict(int)
        self._results[1] = 0
        self._results[-1] = 0
        self._untried_actions = None
        self._untried_actions = self.untried_actions()

    def untried_actions(self):
        self._untried_actions = self.state.get_legal_actions()
        return self._untried_actions

    def q(self):
        wins = self._results[1]
        loses = self._results[-1]
        return wins - loses

    def n(self):
        return self._number_of_visits

    def expand(self):
        action = self._untried_actions.pop()
        next_state = self.state.move(action)
        child_node = MonteCarloTreeSearchNode(next_state, parent=self, parent_action=action)
        self.children.append(child_node)
        return child_node

    def is_terminal_node(self):
        return self.state.is_game_over()

    def rollout(self):
        current_rollout_state = self.state
        while not current_rollout_state.is_game_over():
            legal_actions = current_rollout_state.get_legal_actions()
            if not legal_actions:
                break
            move = self.heuristic_move(current_rollout_state, legal_actions)
            current_rollout_state = current_rollout_state.move(move)
        return current_rollout_state.game_result(self.root_player)


    def heuristic_move(self, state, legal_actions):
        player = state.player_turn
        opponent = 3 - player
        captured = state.captured_subboards

        def causes_subboard_capture(move, acting_player):
            board_idx = move // 9
            cell_idx = move % 9
            test_board = [sub[:] for sub in state.board]
            test_board[board_idx][cell_idx] = acting_player
            return check_for_capture(test_board[board_idx]) == acting_player

        # 1. Win a local board if possible
        for move in legal_actions:
            if causes_subboard_capture(move, player):
                return move

        # 2. Block opponent from winning a local board
        for move in legal_actions:
            board_idx = move // 9
            cell_idx = move % 9

            test_board = [sub[:] for sub in state.board]
            test_board[board_idx][cell_idx] = opponent

            if check_for_capture(test_board[board_idx]) == opponent:
                if move in legal_actions:
                    return move

        # 3. Play to a subboard that isn’t yet captured
        uncaptured_targets = [m for m in legal_actions if captured[m % 9] == 0]
        if uncaptured_targets:
            return random.choice(uncaptured_targets)

        # 4. Fallback: play center anywhere or random legal move
        center_moves = [m for m in legal_actions if m % 9 == 4]
        if center_moves:
            return random.choice(center_moves)

        return random.choice(legal_actions)

    def backpropagate(self, result):
        self._number_of_visits += 1
        self._results[result] += 1
        if self.parent:
            self.parent.backpropagate(result)



    def is_fully_expanded(self):
        return len(self._untried_actions) == 0

    def best_child(self, c_param=1.4):
        if not self.children:
            return None

        choices_weights = [
            (child.q() / child.n()) + c_param * math.sqrt((2 * math.log(self.n()) / child.n()))
            for child in self.children
        ]
        return self.children[np.argmax(choices_weights)]



    def rollout_policy(self, possible_moves):
        if len(possible_moves) == 0:
            return None
        return possible_moves[np.random.randint(len(possible_moves))]

    def tree_policy(self):
        current_node = self
        while not current_node.state.is_game_over():
            if not current_node.is_fully_expanded():
                return current_node.expand()
            current_node = current_node.best_child()
            if current_node is None:
                return None
        return current_node

    def best_action(self, time_limit=10):
        start_time = time.time()
        num_simulations = 0

        while time.time() - start_time < time_limit:
            v = self.tree_policy()
            if v is None:
                break
            reward = v.rollout()
            v.backpropagate(reward)
            num_simulations += 1

        # print(f"[MCTS] Completed {num_simulations} simulations in {time_limit:.2f} seconds.")

        min_simulations = max(50, num_simulations * 0.05)
        if not self.children:
            legal_actions = self.state.get_legal_actions()
            if legal_actions:
                return random.choice(legal_actions)
            raise ValueError("MCTS failed to find any valid moves.")

        most_visited = max(self.children, key=lambda c: c.n())
        best_value = self.best_child(c_param=0)

        return most_visited.parent_action