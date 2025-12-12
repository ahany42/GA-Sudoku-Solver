import random

def generate_full_board(N):
    board = [['-' for _ in range(N)] for _ in range(N)]
    block_size = int(N**0.5)

    def is_valid(board, row, col, num):
        if str(num) in board[row]:
            return False
        for r in range(N):
            if board[r][col] == str(num):
                return False
        start_row = (row // block_size) * block_size
        start_col = (col // block_size) * block_size
        for r in range(start_row, start_row + block_size):
            for c in range(start_col, start_col + block_size):
                if board[r][c] == str(num):
                    return False
        return True

    def fill_board():
        for i in range(N):
            for j in range(N):
                if board[i][j] == '-':
                    nums = list(range(1, N+1))
                    random.shuffle(nums)
                    for num in nums:
                        if is_valid(board, i, j, num):
                            board[i][j] = str(num) 
                            if fill_board():
                                return True
                            board[i][j] = '-'  
                    return False
        return True

    fill_board()
    return board

def generate_puzzle(N, empty_cells_ratio=0.5):
    board = generate_full_board(N)
    total_cells = N * N
    empty_cells = int(total_cells * empty_cells_ratio)

    attempts = empty_cells * 2
    while attempts > 0 and empty_cells > 0:
        r = random.randint(0, N-1)
        c = random.randint(0, N-1)
        if board[r][c] != '-':
            board[r][c] = '-' 
            empty_cells -= 1
        attempts -= 1
    return board

puzzle = generate_puzzle(9, empty_cells_ratio=0.5)
trimmed_board = [[cell.strip() for cell in row] for row in puzzle]
for row in trimmed_board:
    print(row)
