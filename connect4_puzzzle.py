import time
from collections import deque
import heapq

# Game constants
ROWS = 4
COLS = 6  
CONNECT = 4

def build_board(heights):
    # Create empty board first
    board = [[0] * COLS for _ in range(ROWS)]
    
    # Fill columns from bottom up based on heights
    for c in range(COLS):
        for r in range(heights[c]):
            # row 3 is the bottom, so we fill upwards
            board[ROWS - 1 - r][c] = 1
    return board

def has_connect(board, k=CONNECT):
    # check all possible ways to get a connection
    
    # Horizontal check - left to right
    for r in range(ROWS):
        for c in range(COLS - k + 1):
            if all(board[r][c + j] == 1 for j in range(k)):
                return True
    
    # Vertical check - top to bottom  
    for c in range(COLS):
        for r in range(ROWS - k + 1):
            if all(board[r + j][c] == 1 for j in range(k)):
                return True
    
    # Diagonal check - top-left to bottom-right (\)
    for r in range(ROWS - k + 1):
        for c in range(COLS - k + 1):
            if all(board[r + j][c + j] == 1 for j in range(k)):
                return True
                
    # Diagonal check - bottom-left to top-right (/)
    for r in range(ROWS - k + 1):
        for c in range(k - 1, COLS):
            if all(board[r + j][c - j] == 1 for j in range(k)):
                return True
                
    return False

def max_connect(board):
    max_length = 0  # Keep track of longest sequence found
    
    # All directions we need to check horizontal, vertical, diag\, diag/
    directions = [(0,1), (1,0), (1,1), (1,-1)] 
    
    # Check each position on the board
    for r in range(ROWS):
        for c in range(COLS):
            if board[r][c] == 1:  # Only check from filled positions
                # Try each direction
                for dr, dc in directions:
                    current_length = 1 
                    next_r, next_c = r + dr, c + dc
                    
                    # Keep going in this direction while we find connected pieces
                    while (0 <= next_r < ROWS and 0 <= next_c < COLS and 
                           board[next_r][next_c] == 1):
                        current_length += 1
                        next_r += dr
                        next_c += dc
                    
                    max_length = max(max_length, current_length)
    
    return max_length

def get_successors(heights):
    # Generate all possible next states by dropping a piece
    possible_moves = []
    
    for col in range(COLS):
        # drop if column isn't full
        if heights[col] < ROWS:  
            new_state = list(heights) 
            new_state[col] += 1 
            possible_moves.append(tuple(new_state))
    
    return possible_moves

def bfs(start):
    search_queue = deque([(start, 0)]) 
    visited_states = set([start])
    nodes_expanded = 0
    
    while search_queue:
        current_state, moves_so_far = search_queue.popleft()
        nodes_expanded += 1
        
        # Check if won
        if has_connect(build_board(current_state)):
            return moves_so_far, nodes_expanded, current_state
            
        # Try all possible next moves
        for next_state in get_successors(current_state):
            if next_state not in visited_states:
                visited_states.add(next_state)
                search_queue.append((next_state, moves_so_far + 1))
    
    return None, nodes_expanded, None 

def a_star(start, h_func):
    priority_queue = [(h_func(start), 0, start)]  # (f_score, g_score, state)
    visited_states = set()
    nodes_expanded = 0
    
    while priority_queue:
        f_score, g_score, current_state = heapq.heappop(priority_queue)
        nodes_expanded += 1
        
        if current_state in visited_states: 
            continue
            
        visited_states.add(current_state)
        
        # Check if we've reached the goal
        if has_connect(build_board(current_state)):
            return g_score, nodes_expanded, current_state
            
        # Explore neighbors
        for next_state in get_successors(current_state):
            if next_state not in visited_states:
                new_g = g_score + 1
                new_f = new_g + h_func(next_state)
                heapq.heappush(priority_queue, (new_f, new_g, next_state))
    
    return None, nodes_expanded, None

def h_zero(state):
    # Admissible heuristic that always returns 0
    # This makes A* behave like uniform cost search
    return 0

def h_max_connect(state):
    # Heuristic based on current max connection length
    # Estimates how many more moves needed to reach CONNECT
    current_max = max_connect(build_board(state))
    remaining = max(0, CONNECT - current_max)
    return remaining

def show(state, name):
    print(f"\n--- {name} solution ({sum(state)} pieces) ---")
    b = build_board(state)
    print("  0 1 2 3 4 5")
    for row in b:
        print(" " + " ".join("1" if x==1 else "0" for x in row))
    print()


start = (0,0,0,0,0,0)

t = time.time()
moves1, nodes1, win1 = bfs(start)
print(f"BFS: {moves1} moves, {nodes1} nodes, {time.time()-t:.3f}s")
show(win1, "BFS")

t = time.time()
moves2, nodes2, win2 = a_star(start, h_zero)
print(f"A* (h=0): {moves2} moves, {nodes2} nodes, {time.time()-t:.3f}s")
show(win2, "A* h=0")

t = time.time()
moves3, nodes3, win3 = a_star(start, h_max_connect)
print(f"A* (max-connect heuristic): {moves3} moves, {nodes3} nodes, {time.time()-t:.3f}s")
show(win3, "A* heuristic")

start = (2,2,1,0,3,0)

t = time.time()
moves1, nodes1, win1 = bfs(start)
print(f"BFS: {moves1} moves, {nodes1} nodes, {time.time()-t:.3f}s")
show(win1, "BFS")

t = time.time()
moves2, nodes2, win2 = a_star(start, h_zero)
print(f"A* (h=0): {moves2} moves, {nodes2} nodes, {time.time()-t:.3f}s")
show(win2, "A* h=0")

t = time.time()
moves3, nodes3, win3 = a_star(start, h_max_connect)
print(f"A* (max-connect heuristic): {moves3} moves, {nodes3} nodes, {time.time()-t:.3f}s")
show(win3, "A* heuristic")

