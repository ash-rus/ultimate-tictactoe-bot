def update_cell_visibility(board, allowed_subboards):
    for i, subboard in enumerate(board):
        new_subboard = []
        for cell in subboard:
            if i in allowed_subboards:
                if cell == 3:
                    new_subboard.append(0)
                elif cell == 4:
                    new_subboard.append(1)
                elif cell == 5:
                    new_subboard.append(2)
                else:
                    new_subboard.append(cell)
            else:
                if cell == 0:
                    new_subboard.append(3)
                elif cell == 1:
                    new_subboard.append(4)
                elif cell == 2:
                    new_subboard.append(5)
                else:
                    new_subboard.append(cell)
        board[i] = new_subboard

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
    else:
        return False

def get_next_subboard(last_move_index, board):
    next_subboard_index = last_move_index % 9
    if all(cell in (6, 7) for cell in board[next_subboard_index]):
        playable = [
            i for i, sub in enumerate(board)
            if any(cell in (0, 1, 2, 3, 4, 5) for cell in sub)
        ]
        return playable if playable else None
    else:
        if any(cell in (0, 1, 2, 3, 4, 5) for cell in board[next_subboard_index]):
            return [next_subboard_index]
        else:
            playable = [
                i for i, sub in enumerate(board)
                if any(cell in (0, 1, 2, 3, 4, 5) for cell in sub)
            ]
            return playable if playable else None

def check_for_end(board):
    capture_patterns = [
        [0, 1, 2], [3, 4, 5], [6, 7, 8],
        [0, 3, 6], [1, 4, 7], [2, 5, 8],
        [0, 4, 8], [2, 4, 6]
    ]
    def is_captured(subboard, player_value):
        return all(cell == player_value for cell in subboard)
    captured = []
    for subboard in board:
        if is_captured(subboard, 6):
            captured.append(1)
        elif is_captured(subboard, 7):
            captured.append(2)
        else:
            captured.append(0)
    for pattern in capture_patterns:
        first = captured[pattern[0]]
        if first != 0 and all(captured[i] == first for i in pattern):
            return first
    return 0

def check_for_capture(subboard):
    capture_patterns = [
        [0, 1, 2], [3, 4, 5], [6, 7, 8],
        [0, 3, 6], [1, 4, 7], [2, 5, 8],
        [0, 4, 8], [2, 4, 6]
    ]
    for pattern in capture_patterns:
        cells = [subboard[i] for i in pattern]
        if all(c == 1 for c in cells):
            return 1
        if all(c == 2 for c in cells):
            return 2
    return 0

def print_ultimate_board(board, available_subboards):
    symbol_map = {
        0: ' ',
        1: 'X',
        2: 'O',
        3: ' ',
        4: 'X',
        5: 'O',
        6: 'X',
        7: 'O'
    }
    labels = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I']
    def is_playable(subboard):
        for cell in subboard:
            if cell in (0, 1, 2):
                return True
        return False
    for big_row in range(3):
        label_line = ""
        for big_col in range(3):
            idx = big_row * 3 + big_col
            label = labels[idx]
            if idx in available_subboards:
                label = f"*{label}*"
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
    board = [
        [3, 3, 3, 3, 3, 3, 3, 3, 3],
        [3, 3, 3, 3, 3, 3, 3, 3, 3],
        [3, 3, 3, 3, 3, 3, 3, 3, 3],
        [3, 3, 3, 3, 3, 3, 3, 3, 3],
        [0, 0, 0, 0, 0, 0, 0, 0, 0],
        [3, 3, 3, 3, 3, 3, 3, 3, 3],
        [3, 3, 3, 3, 3, 3, 3, 3, 3],
        [3, 3, 3, 3, 3, 3, 3, 3, 3],
        [3, 3, 3, 3, 3, 3, 3, 3, 3]
    ]
    player_turn = 1
    current_allowed_subboards = [4]
    while True:
        print_ultimate_board(board, current_allowed_subboards)
        move_input = input(f"Player {'X' if player_turn == 1 else 'O'}, enter your move: ")
        idx = parse_input(move_input)
        if idx is None:
            print("Invalid format. Try again.")
            continue
        subboard = idx // 9
        if subboard not in current_allowed_subboards:
            print(f"Invalid move. You must play in {[chr(i + 65) for i in current_allowed_subboards]}")
            continue
        if not place_move(board, idx, player_turn):
            print("Cell already taken.")
            continue
        captured = check_for_capture(board[subboard])
        if captured == 1:
            board[subboard] = [6] * 9
        elif captured == 2:
            board[subboard] = [7] * 9
        result = check_for_end(board)
        if result == 1:
            print_ultimate_board(board, [])
            print("X wins the game!")
            break
        elif result == 2:
            print_ultimate_board(board, [])
            print("O wins the game!")
            break
        current_allowed_subboards = get_next_subboard(idx, board)
        update_cell_visibility(board, current_allowed_subboards)
        if current_allowed_subboards is None:
            print("Game over — no more moves possible.")
            break
        player_turn = 2 if player_turn == 1 else 1

if __name__ == "__main__":
    main()
