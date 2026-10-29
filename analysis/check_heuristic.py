"""
Independent check of connect4_puzzzle.py (CPS 367 final project).

The script imports the original file without changing it, then:
  1. computes the true minimum number of drops to a Connect-4 from all 15,625 states,
  2. tests whether h_max_connect ever overestimates that number (admissibility),
  3. checks whether A* still returns the optimal cost from every starting state,
  4. separates "heap pops" (what the original code counts) from unique expansions,
  5. compares an admissible alternative: fewest empty cells in any winning line.

Run from the repo root:  python analysis/check_heuristic.py
"""
import contextlib
import heapq
import importlib.util
import io
import itertools
import sys
from pathlib import Path

sys.dont_write_bytecode = True
SRC = Path(__file__).resolve().parents[1] / "connect4_puzzzle.py"
spec = importlib.util.spec_from_file_location("connect4", SRC)
c4 = importlib.util.module_from_spec(spec)
with contextlib.redirect_stdout(io.StringIO()):  # the original file runs its demo on import
    spec.loader.exec_module(c4)

ROWS, COLS, K = c4.ROWS, c4.COLS, c4.CONNECT
EMPTY = (0,) * COLS


def is_goal(state):
    return c4.has_connect(c4.build_board(state))


# 1. True cost-to-goal. Every move adds one piece, so process states from full to empty.
states = sorted(itertools.product(range(ROWS + 1), repeat=COLS), key=sum, reverse=True)
true_cost = {}
for s in states:
    true_cost[s] = 0 if is_goal(s) else 1 + min(true_cost[t] for t in c4.get_successors(s))

# All 24 winning lines on a 4 x 6 board.
LINES = []
for r in range(ROWS):
    for c in range(COLS):
        for dr, dc in [(0, 1), (1, 0), (1, 1), (1, -1)]:
            cells = [(r + i * dr, c + i * dc) for i in range(K)]
            if all(0 <= a < ROWS and 0 <= b < COLS for a, b in cells):
                LINES.append(cells)


def h_min_empty_line(state):
    """Admissible: each drop fills one cell, so a win needs at least this many drops."""
    board = c4.build_board(state)
    return min(sum(board[a][b] == 0 for a, b in line) for line in LINES)


def a_star(start, h):
    """Same algorithm as the original, but counts pops and unique expansions separately."""
    frontier = [(h(start), 0, start)]
    closed, pops = set(), 0
    while frontier:
        _, g, s = heapq.heappop(frontier)
        pops += 1
        if s in closed:
            continue
        closed.add(s)
        if is_goal(s):
            return g, pops, len(closed)
        for t in c4.get_successors(s):
            if t not in closed:
                heapq.heappush(frontier, (g + 1 + h(t), g + 1, t))
    return None, pops, len(closed)


def show(state):
    for row in c4.build_board(state):
        print("    " + " ".join("X" if x else "." for x in row))


print(f"States: {len(states):,}   already-winning states: {sum(v == 0 for v in true_cost.values()):,}")
print(f"True minimum drops from the empty board: {true_cost[EMPTY]}\n")

over = [s for s in states if c4.h_max_connect(s) > true_cost[s]]
print(f"h_max_connect overestimates the true cost in {len(over)} states, so it is not admissible.")
example = min(over, key=sum)
print(f"Example {example}: h = {c4.h_max_connect(example)}, true cost = {true_cost[example]}")
show(example)
print("  Two drops fill the gaps and join the separate pieces into one line of four.\n")

bad = sum(a_star(s, c4.h_max_connect)[0] != true_cost[s] for s in states)
print(f"Starts where A* with h_max_connect returns a non-optimal cost: {bad} of {len(states):,}\n")

print(f"Alternative h_min_empty_line overestimates in "
      f"{sum(h_min_empty_line(s) > true_cost[s] for s in states)} states.\n")

print("From the empty board         cost  heap pops  unique expansions")
for name, h in [("A*, h = 0", c4.h_zero),
                ("A*, h_max_connect", c4.h_max_connect),
                ("A*, h_min_empty_line", h_min_empty_line)]:
    g, pops, uniq = a_star(EMPTY, h)
    print(f"  {name:26s} {g:4d} {pops:10d} {uniq:18d}")
