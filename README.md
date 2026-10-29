# Artificial Intelligence Coursework (Python)

![Python](https://img.shields.io/badge/Python-3776AB?style=flat&logo=python&logoColor=white)
![Jupyter](https://img.shields.io/badge/Jupyter-F37626?style=flat&logo=jupyter&logoColor=white)

## For readers

This repo holds my work from CPS 367 Artificial Intelligence at Franklin & Marshall College
(Fall 2025), taught from *Artificial Intelligence: A Modern Approach* (Russell & Norvig).

If you have five minutes, look at the **final project**: a search problem I designed, coded
and tested myself (`connect4_puzzzle.py`, slides in `slide.pdf`). Below it is an
**independent analysis** that re-checks the project's claims by brute force. It confirms the
main result and finds one claim in my presentation that does not hold.

## Contents

| File | Topics |
|---|---|
| `Homework 1.ipynb` | Intelligent agents, uninformed search |
| `Homework 2.ipynb` | Informed search, search under uncertainty, constraint satisfaction |
| `Homework 3.ipynb` | Propositional and first-order logic, forward chaining, resolution |
| `Homework4.ipynb` | Planning, probability, Bayesian networks |
| `connect4_puzzzle.py` | Final project: BFS and A* search on a Connect-4 puzzle |
| `slide.pdf` | Final project presentation (11 slides) |
| `analysis/check_heuristic.py` | Independent check of the final project (see below) |

## Final project: Search and CSP approaches for a simplified Connect-4 puzzle

**The question.** Starting from an empty board and dropping pieces with normal gravity, what is
the smallest number of pieces needed to make four in a row?

**Why this version.** Full two-player Connect-4 on a 6 × 7 board has about 4.5 trillion
positions, too many for basic search. I made it a single-player puzzle on a 4 × 6 board. A
state is the tuple of six column heights (0–4 each), which gives 5⁶ = 15,625 states. Tuples
are hashable, so they work directly in a visited set.

**What I built.**
- `build_board`, `has_connect` (horizontal, vertical and both diagonals) and `get_successors`.
- **Breadth-first search**, which is optimal here because every drop costs 1.
- **A\*** with two heuristics: `h = 0`, and `h_max_connect = 4 − (longest line on the board)`.
- A **CSP formulation** on the slides: variables are the six final heights, domains are
  {0,…,4}, and one global constraint requires at least one line of four. It is described,
  not implemented.

**What I reported.** From the empty board, all three searches find the optimal answer of 4
pieces. BFS expands 85 nodes, A* with `h = 0` expands 170, and A* with `h_max_connect`
expands 38.

## Independent analysis

This is a review of the final project, written after the course. It treats the code and the
slides as claims and tests each one. `analysis/check_heuristic.py` imports the original file
without changing it. It then computes the true minimum number of drops from **all 15,625
states**, working backward from full boards, and compares every claim against that ground
truth. The homework notebooks were not re-run for this review.

### What holds up

- **The answer is correct.** The true minimum from the empty board is 4, and every search in
  the project finds it.
- **The problem is set up well.** The column-height state removes symmetric duplicates (any
  order of the same drops gives the same state), and gravity is built into the encoding, so
  illegal boards cannot be generated.
- **The heuristic does guide the search.** A* with `h_max_connect` reaches the goal after 29
  unique expansions, compared with 85 for BFS.

### What does not hold up

**1. `h_max_connect` is not admissible.** The slides argue that each new piece can extend a
line by at most one, so the heuristic never overestimates. That misses one case: a single
piece can **join two separate pieces** into one longer line. The check script finds **139
states** where the heuristic overestimates. The smallest:

```
. . . . . .
. . . . . .
. . . . . .
. . . X . X      longest line = 1, so h = 3
```

Dropping into columns 2 and 4 makes four in a row, so the true cost is 2.

An inadmissible heuristic can make A* return a non-optimal answer. It does not happen here:
A* with `h_max_connect` returns the optimal cost from **all 15,625 starting states**. The
board is small and the goal is shallow, so the bad estimates never decide the result.

**A fix that is admissible:** take the fewest empty cells in any of the 24 possible winning
lines. Each drop fills one cell, so this can never overestimate, and the script confirms
zero overestimates. The price is a little more work: 42 unique expansions instead of 29.

**2. The "170 vs 85" gap is a counting artifact.** The slides suggest A* with `h = 0`
expanded more nodes than BFS "possibly due to heap ties". The code actually increments the
counter *before* skipping states it has already visited, so it counts every heap pop,
duplicates included. Counting unique expansions, A* with `h = 0` expands **85, exactly the
same as BFS**, which is what theory predicts for unit costs. The same fix changes the
heuristic's count from 38 to 29.

| From the empty board | Cost | Heap pops (what the code reports) | Unique expansions |
|---|---|---|---|
| BFS | 4 | — | 85 |
| A*, `h = 0` | 4 | 170 | 85 |
| A*, `h_max_connect` | 4 | 38 | 29 |
| A*, fewest empty cells in a line (admissible) | 4 | 74 | 42 |

**3. Smaller points.**
- 13,473 of the 15,625 states already contain four in a row. Only about 2,150 states need any
  search, which is why every algorithm runs in about a millisecond. The runtimes on the
  slides cannot separate the algorithms.
- The CSP was formulated but not solved, so the slides compare search and CSP in words only.
- `show()` prints the total number of pieces on the board, not the number of pieces added.
  For the second test case it says "9 pieces" for a 1-move solution.

### What this project shows

- A large problem cut down to one that can be searched exhaustively, with the reasons stated.
- BFS and A* implemented from scratch with a sensible state encoding.
- A hypothesis-driven experiment. The flaws above are in the reasoning about the results, not
  in the search code, and they are the kind a brute-force check catches quickly.

### Next steps

1. Use the admissible heuristic, or keep `h_max_connect` and describe it as inadmissible but
   effective in practice.
2. Count unique expansions, and test on harder starts or bigger boards (5 × 7, five in a row)
   where the algorithms actually differ.
3. Implement the CSP with backtracking search so the search-vs-CSP comparison has numbers.

## Reproduce

```bash
python connect4_puzzzle.py            # original results
python analysis/check_heuristic.py    # independent check (a few seconds)
```

Only the Python standard library is needed.

## Skills

Search algorithms (BFS, A*, heuristic design) · constraint satisfaction · logical inference ·
Bayesian reasoning · Python
