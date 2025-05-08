# game.py
from game_logic import parse_input, check_for_capture, check_for_end, get_next_subboard, place_move, print_ultimate_board
from agent import MonteCarloTreeSearchNode, UltimateTicTacToeState
# Other imports

def main(mode="AvA"):
    board = [[0] * 9 for _ in range(9)]
    captured_subboards = [0] * 9
    allowed_subboards = [4]
    player_turn = 1

    # Define player types
    mode_map = {
        "PvP": {1: "human", 2: "human"},
        "PvA": {1: "human", 2: "ai"},
        "AvP": {1: "ai", 2: "human"},
        "AvA": {1: "ai", 2: "ai"},
    }

    player_type = mode_map.get(mode)
    if player_type is None:
        print("Invalid mode. Choose from: PvP, PvA, AvP, AvA")
        return

    state = UltimateTicTacToeState(board, allowed_subboards, captured_subboards, player_turn)

    while True:
        print_ultimate_board(board, allowed_subboards, captured_subboards)

        if player_type[player_turn] == "human":
            move_input = input(f"Player {'X' if player_turn == 1 else 'O'}, enter your move: ")
            idx = parse_input(move_input)
            if idx is None:
                print("Invalid input format.")
                continue

            subboard = idx // 9
            if subboard not in allowed_subboards:
                print(f"Invalid subboard. Must play in {[chr(i + 65) for i in allowed_subboards]}")
                continue

            if not place_move(board, idx, player_turn):
                print("Cell is already taken.")
                continue

        else:  # AI Move
            print(f"AI Player {'X' if player_turn == 1 else 'O'} is thinking...")
            mcts_node = MonteCarloTreeSearchNode(state)
            best_action = mcts_node.best_action(time_limit=10)
            idx = best_action
            place_move(board, idx, player_turn)

        subboard = idx // 9
        captured = check_for_capture(board[subboard])
        if captured != 0:
            captured_subboards[subboard] = captured

        result = check_for_end(captured_subboards)
        if result != -1:
            print_ultimate_board(board, [], captured_subboards)
            print("X wins!" if result == 1 else "O wins!" if result == 2 else "Game is a draw!")
            break

        allowed_subboards = get_next_subboard(idx, board, set(i for i, v in enumerate(captured_subboards) if v != 0))
        if allowed_subboards is None or not allowed_subboards:
            print_ultimate_board(board, [], captured_subboards)
            print("Game over: no valid moves.")
            break

        player_turn = 3 - player_turn
        state = UltimateTicTacToeState(board, allowed_subboards, captured_subboards, player_turn)


if __name__ == "__main__":
    main()