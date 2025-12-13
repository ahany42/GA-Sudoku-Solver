# puzzle.py
from __future__ import annotations
from dataclasses import dataclass
from typing import List


Grid = List[List[int]]  # 9x9


@dataclass(frozen=True)
class SudokuPuzzle:
    """
    Holds the original Sudoku (givens) + provides fast fitness evaluation.

    givens_grid:
      - 9x9
      - 0 means empty cell
      - 1..9 are fixed givens
    """
    givens_grid: Grid

    def __post_init__(self):
        if len(self.givens_grid) != 9 or any(len(row) != 9 for row in self.givens_grid):
            raise ValueError("givens_grid must be 9x9.")
        for r in range(9):
            for c in range(9):
                v = self.givens_grid[r][c]
                if v not in range(0, 10):
                    raise ValueError("givens_grid values must be in {0..9}.")

    def is_fixed(self, r: int, c: int) -> bool:
        return self.givens_grid[r][c] != 0

    # -------------------------
    # Fitness (higher is better)
    # -------------------------

    @staticmethod
    def _conflicts_in_9(values: List[int]) -> int:
        """
        values length is 9. For Sudoku we expect 1..9.
        Conflicts = 9 - number_of_unique_values.
        """
        return 9 - len(set(values))

    def column_conflicts(self, grid: Grid) -> int:
        total = 0
        for c in range(9):
            col = [grid[r][c] for r in range(9)]
            total += self._conflicts_in_9(col)
        return total

    def box_conflicts(self, grid: Grid) -> int:
        total = 0
        for br in (0, 3, 6):
            for bc in (0, 3, 6):
                box = []
                for r in range(br, br + 3):
                    for c in range(bc, bc + 3):
                        box.append(grid[r][c])
                total += self._conflicts_in_9(box)
        return total

    def total_conflicts(self, grid: Grid) -> int:
        # Rows are always valid by construction (in our representation),
        # so we only count column + box conflicts.
        return self.column_conflicts(grid) + self.box_conflicts(grid)

    def fitness(self, grid: Grid) -> float:
        """
        Convert conflicts to a 'higher is better' score.
        Perfect solution => conflicts = 0 => fitness = 1.0
        """
        conflicts = self.total_conflicts(grid)
        return 1.0 / (1.0 + conflicts)

    # -------------------------
    # Optional helpers
    # -------------------------

    def is_solved(self, grid: Grid) -> bool:
        return self.total_conflicts(grid) == 0

    def pretty(self, grid: Grid) -> str:
        """Nice printing for console debugging."""
        lines = []
        for r in range(9):
            if r in (3, 6):
                lines.append("-" * 21)
            row = []
            for c in range(9):
                if c in (3, 6):
                    row.append("|")
                row.append(str(grid[r][c]))
            lines.append(" ".join(row))
        return "\n".join(lines)
