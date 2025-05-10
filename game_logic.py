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

def get_valid_indices(board, allowed_subboards, captured_subboards):
    valid_indices = []
    
    for sub_idx in allowed_subboards:
        if captured_subboards[sub_idx] != 0:
            continue
        
        for cell_idx in range(9):  
            if board[sub_idx][cell_idx] == 0:
                valid_indices.append(sub_idx * 9 + cell_idx)
    return valid_indices

def is_valid_move(board, index):
    board_idx = index // 9
    cell_idx = index % 9
    if board[board_idx][cell_idx] == 0:
        return True
    return False

def place_move(board, index, player):
    if(is_valid_move(board, index)):
        board_idx = index // 9
        cell_idx = index % 9
        board[board_idx][cell_idx] = player
        return True
    return False

def get_next_subboard(last_move_index, board, captured_subboards):
    next_subboard_index = last_move_index % 9
    last_subboard = last_move_index // 9
    
    if next_subboard_index not in captured_subboards and any(cell == 0 for cell in board[next_subboard_index]):
        return [next_subboard_index]
    
    if all(cell != 0 for cell in board[last_subboard]):
        return [
            i for i in range(9)
            if i not in captured_subboards and not all(cell != 0 for cell in board[i])
        ] or None

    if last_subboard in captured_subboards or all(cell != 0 for cell in board[last_subboard]):
        open_tiles_in_last_subboard = [
            i for i in range(9) if board[last_subboard][i % 3 + (i // 3) * 3] == 0
        ]
        if open_tiles_in_last_subboard:
            return [
                i for i in open_tiles_in_last_subboard
                if i not in captured_subboards
            ] or None

    return [last_subboard]

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
    winning_lines = [
        [0, 1, 2], [3, 4, 5], [6, 7, 8],
        [0, 3, 6], [1, 4, 7], [2, 5, 8],
        [0, 4, 8], [2, 4, 6]
    ]

    for line in winning_lines:
        values = [captured_subboards[i] for i in line]
        if values == [1, 1, 1]:
            return 1
        elif values == [2, 2, 2]:
            return 2

    if all(x != 0 for x in captured_subboards):
        return 0

    return -1


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