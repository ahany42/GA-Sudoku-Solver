from __future__ import annotations
from dataclasses import dataclass
from typing import List


Grid = List[List[int]]  


@dataclass(frozen=True)
class SudokuPuzzle:
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


    @staticmethod
    def _conflicts_in_9(values: List[int]) -> int:
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
    
        return self.column_conflicts(grid) + self.box_conflicts(grid)

    def fitness(self, grid: Grid) -> float:
        
        conflicts = self.total_conflicts(grid)
        return 1.0 / (1.0 + conflicts)

  

    def is_solved(self, grid: Grid) -> bool:
        return self.total_conflicts(grid) == 0

    def pretty(self, grid: Grid) -> str:
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
