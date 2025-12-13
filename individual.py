# individual.py
from __future__ import annotations
from dataclasses import dataclass
from typing import List, Optional
import random


Grid = List[List[int]] 


@dataclass
class Individual:
    """
    One candidate Sudoku solution (chromosome).
    Representation: each ROW is always valid (1..9) by construction.
    Fixed cells (givens) are never changed.
    """
    grid: Grid
    fitness: Optional[float] = None

    @classmethod
    def random_from_puzzle(cls, puzzle) -> "Individual":
        """
        Create a random individual that respects givens and makes each row a permutation of 1..9.
        'puzzle' is expected to provide:
          - puzzle.givens_grid (9x9, 0 for empty)
          - puzzle.is_fixed(r, c) -> bool
        """
        grid: Grid = [[0] * 9 for _ in range(9)]

        for r in range(9):
            given_digits = []
            empty_positions = []

            for c in range(9):
                val = puzzle.givens_grid[r][c]
                if val != 0:
                    grid[r][c] = val
                    given_digits.append(val)
                else:
                    empty_positions.append(c)

            missing = [d for d in range(1, 10) if d not in given_digits]
            random.shuffle(missing)

            for idx, c in enumerate(empty_positions):
                grid[r][c] = missing[idx]

        return cls(grid=grid, fitness=None)

    def copy(self) -> "Individual":
        return Individual(grid=[row[:] for row in self.grid], fitness=self.fitness)

    def evaluate(self, puzzle) -> float:
        """
        Fitness computed by puzzle. Expected:
          - puzzle.fitness(grid) -> float (higher is better)
        """
        self.fitness = puzzle.fitness(self.grid)
        return self.fitness

  

    def mutate_swap_in_row(self, puzzle, row: Optional[int] = None) -> None:
       
        r = random.randrange(9) if row is None else row

        mutable_cols = [c for c in range(9) if not puzzle.is_fixed(r, c)]
        if len(mutable_cols) < 2:
            return

        c1, c2 = random.sample(mutable_cols, 2)
        self.grid[r][c1], self.grid[r][c2] = self.grid[r][c2], self.grid[r][c1]
        self.fitness = None

    def mutate_scramble_in_row(self, puzzle, row: Optional[int] = None, k: int = 4) -> None:
     
        r = random.randrange(9) if row is None else row

        mutable_cols = [c for c in range(9) if not puzzle.is_fixed(r, c)]
        if len(mutable_cols) < 2:
            return

        k = min(k, len(mutable_cols))
        cols = random.sample(mutable_cols, k)
        vals = [self.grid[r][c] for c in cols]
        random.shuffle(vals)

        for c, v in zip(cols, vals):
            self.grid[r][c] = v

        self.fitness = None

    def mutate(self, puzzle, p_swap: float = 0.8) -> None:
      
        if random.random() < p_swap:
            self.mutate_swap_in_row(puzzle)
        else:
            self.mutate_scramble_in_row(puzzle)

   

    def respects_givens(self, puzzle) -> bool:
        for r in range(9):
            for c in range(9):
                if puzzle.is_fixed(r, c) and self.grid[r][c] != puzzle.givens_grid[r][c]:
                    return False
        return True
