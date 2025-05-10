from game_logic import parse_input, check_for_capture, check_for_end, get_next_subboard, place_move, print_ultimate_board, get_valid_indices
from agent import MonteCarloTreeSearchNode, UltimateTicTacToeState
import random
import matplotlib.pyplot as plt

def simulate_games(n=1000):
    ai_wins = 0
    random_wins = 0
    draws = 0
    completed_games = 0

    results_over_time = []

    for game_num in range(1, n + 1):
        board = [[0] * 9 for _ in range(9)]
        captured_subboards = [0] * 9
        allowed_subboards = [4]
        player_turn = 1

        player_type = {1: "ai", 2: "random"}
        state = UltimateTicTacToeState(board, allowed_subboards, captured_subboards, player_turn)

        while True:
            if player_type[player_turn] == "ai":
                try:
                    mcts_node = MonteCarloTreeSearchNode(state)
                    idx = mcts_node.best_action(time_limit=0.01)
                except ValueError:
                    break
            else:
                valid_moves = get_valid_indices(board, allowed_subboards, captured_subboards)
                if not valid_moves:
                    break
                idx = random.choice(valid_moves)

            if not place_move(board, idx, player_turn):
                break

            subboard = idx // 9
            captured = check_for_capture(board[subboard])
            if captured != 0:
                captured_subboards[subboard] = captured

            result = check_for_end(captured_subboards)
            if result != -1:
                completed_games += 1
                if result == 1:
                    ai_wins += 1
                elif result == 2:
                    random_wins += 1
                else:
                    draws += 1
                break

            allowed_subboards = get_next_subboard(
                idx, board, set(i for i, v in enumerate(captured_subboards) if v != 0)
            )
            if allowed_subboards is None or not allowed_subboards:
                draws += 1
                completed_games += 1
                break

            player_turn = 3 - player_turn
            state = UltimateTicTacToeState(board, allowed_subboards, captured_subboards, player_turn)

        results_over_time.append((ai_wins, random_wins, draws))

        if game_num % 100 == 0 or game_num == 1:
            print(f"Game {game_num}: AI Wins: {ai_wins}, Random Wins: {random_wins}, Draws: {draws}, Completed: {completed_games}/{game_num}")

    print("\nFinal Results:")
    print(f"Total Games Attempted: {n}")
    print(f"Completed Games: {completed_games}")
    print(f"AI Wins: {ai_wins}")
    print(f"Random Wins: {random_wins}")
    print(f"Draws: {draws}")

    labels = ['AI Wins', 'Random Wins', 'Draws']
    values = [ai_wins, random_wins, draws]

    plt.figure(figsize=(8, 6))
    plt.bar(labels, values, color=['green', 'red', 'gray'])
    plt.title(f"Results after {n} Simulated Games")
    plt.ylabel("Number of Games")
    plt.xlabel("Outcome")
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.show()


def main(mode="AvR"):
    board = [[0] * 9 for _ in range(9)]
    captured_subboards = [0] * 9
    allowed_subboards = [4]
    player_turn = 1

    mode_map = {
        "PvP": {1: "human", 2: "human"},
        "PvA": {1: "human", 2: "ai"},
        "AvP": {1: "ai", 2: "human"},
        "AvA": {1: "ai", 2: "ai"},
        "AvR": {1: "ai", 2: "random"},
        "RvA": {1: "random", 2: "ai"},
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

        else:
            if player_type[player_turn] == "ai":
                print(f"AI Player {'X' if player_turn == 1 else 'O'} is thinking...")
                mcts_node = MonteCarloTreeSearchNode(state)
                best_action = mcts_node.best_action(time_limit=0.1)
                idx = best_action
            elif player_type[player_turn] == "random":
                print(f"Random Player {'X' if player_turn == 1 else 'O'} is choosing...")
                import random
                valid_moves = get_valid_indices(board, allowed_subboards, captured_subboards)
                idx = random.choice(valid_moves)

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
    # simulate_games(1000)
    main()