def parse_input(user_input):
    labels = {'A': 0, 'B': 9, 'C': 18, 'D': 27, 'E': 36, 'F': 45, 'G': 54, 'H': 63, 'I': 72}
    user_input = user_input.upper().strip()
    if len(user_input) != 2:
        return None
    board_label, cell_char = user_input[0], user_input[1]
    if board_label not in labels or not cell_char.isdigit():
        return None
    cell_num = int(cell_char)
    if not 0 <= cell_num <= 8:
        return None
    return labels[board_label] + cell_num

def place_move(board, index, player):
    board_idx = index // 9
    cell_idx = index % 9
    if board[board_idx][cell_idx] == 0:
        board[board_idx][cell_idx] = player
        return True
    return False

def get_next_subboard(last_move_index, board, captured_subboards):
    next_subboard_index = last_move_index % 9
    last_subboard = last_move_index // 9
    
    # Rule 1: If the player is sent to a playable subboard, they will play there.
    if next_subboard_index not in captured_subboards and any(cell == 0 for cell in board[next_subboard_index]):
        return [next_subboard_index]  # The next subboard is playable.
    
    # Rule 4: If the player is sent to an unplayable subboard AND the last played subboard is full,
    # the next player will be able to play in any uncaptured subboard that is not filled.
    if all(cell != 0 for cell in board[last_subboard]):
        return [
            i for i in range(9)
            if i not in captured_subboards and not all(cell != 0 for cell in board[i])
        ] or None  # Return any uncaptured subboard that is not fully filled.

    # Rule 3: If the player is sent to an unplayable subboard AND the last played subboard is also now unplayable,
    # the next player will be able to play in any uncaptured subboard that corresponds to an open tile in the last played subboard.
    if last_subboard in captured_subboards or all(cell != 0 for cell in board[last_subboard]):
        # Return subboards that correspond to open tiles in the last played subboard
        open_tiles_in_last_subboard = [
            i for i in range(9) if board[last_subboard][i % 3 + (i // 3) * 3] == 0
        ]
        return [
            i for i in open_tiles_in_last_subboard
            if i not in captured_subboards
        ] or None  # Return uncaptured subboards with open spots in the last played subboard.

    # Rule 2: If the player is sent to an unplayable subboard, they will play in the subboard that was just played in.
    return [last_subboard]  # The player will play in the subboard just played in.





def check_for_capture(subboard):
    lines = [
        [0,1,2],[3,4,5],[6,7,8], [0,3,6],[1,4,7],[2,5,8], [0,4,8],[2,4,6]
    ]
    for line in lines:
        if all(subboard[i] == 1 for i in line):
            return 1
        elif all(subboard[i] == 2 for i in line):
            return 2
    return 0

def check_for_end(captured_subboards):
    lines = [
        [0,1,2],[3,4,5],[6,7,8], [0,3,6],[1,4,7],[2,5,8], [0,4,8],[2,4,6]
    ]
    for line in lines:
        values = [captured_subboards[i] for i in line]
        if values[0] != 0 and all(v == values[0] for v in values):
            return values[0]
    return 0

def print_ultimate_board(board, allowed_subboards, captured_subboards):
    symbol_map = {0: ' ', 1: 'X', 2: 'O'}
    labels = ['A','B','C','D','E','F','G','H','I']
    for big_row in range(3):
        label_line = ""
        for big_col in range(3):
            idx = big_row * 3 + big_col
            label = labels[idx]
            if idx in allowed_subboards:
                label = f"*{label}*"
            elif captured_subboards[idx] != 0:
                label = f"[{symbol_map[captured_subboards[idx]]}]"
            else:
                label = f" {label} "
            label_line += f"    {label}    "
            if big_col < 2:
                label_line += "||"
        print(label_line)
        for small_row in range(3):
            row_line = ""
            for big_col in range(3):
                idx = big_row * 3 + big_col
                subboard = board[idx]
                start = small_row * 3
                row = subboard[start:start+3]
                row_line += " " + " | ".join(symbol_map[cell] for cell in row) + " "
                if big_col < 2:
                    row_line += "||"
            print(row_line)
        if big_row < 2:
            print("=" * 37)

def main():
    board = [[0] * 9 for _ in range(9)]
    captured_subboards = [0] * 9
    allowed_subboards = [4]
    player_turn = 1

    while True:
        print_ultimate_board(board, allowed_subboards, captured_subboards)
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

        captured = check_for_capture(board[subboard])
        if captured != 0:
            captured_subboards[subboard] = captured

        result = check_for_end(captured_subboards)
        if result != 0:
            print_ultimate_board(board, [], captured_subboards)
            print("X wins!" if result == 1 else "O wins!")
            break

        allowed_subboards = get_next_subboard(idx, board, set(i for i, v in enumerate(captured_subboards) if v != 0))
        if allowed_subboards is None:
            print_ultimate_board(board, [], captured_subboards)
            print("Game over: no valid moves.")
            break

        player_turn = 2 if player_turn == 1 else 1

if __name__ == "__main__":
    main()
