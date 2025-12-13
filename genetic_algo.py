# genetic_algo.py
from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Tuple
import random
import time

from individual import Individual
from puzzle import SudokuPuzzle


@dataclass
class GAConfig:
    population_size: int = 300
    generations: int = 5000 

    tournament_k: int = 3
    elitism_rate: float = 0.02  

    crossover_rate: float = 0.9
    mutation_rate: float = 0.2  

    
    stagnation_limit: int = 250
    immigrants_rate: float = 0.10  
    mutation_boost: float = 1.5    
    mutation_rate_cap: float = 0.8

    run_until_solved: bool = False
    max_seconds: float = 60.0 


@dataclass
class GeneticAlgorithm:
    puzzle: SudokuPuzzle
    config: GAConfig = field(default_factory=GAConfig)

    population: List[Individual] = field(default_factory=list)
    best_history: List[float] = field(default_factory=list)
    avg_history: List[float] = field(default_factory=list)

    def initialize(self) -> None:
        self.population = [
            Individual.random_from_puzzle(self.puzzle)
            for _ in range(self.config.population_size)
        ]
        for ind in self.population:
            ind.evaluate(self.puzzle)


    def tournament_select(self) -> Individual:
        k = self.config.tournament_k
        contenders = random.sample(self.population, k)
        return max(contenders, key=lambda x: x.fitness if x.fitness is not None else -1)


    def crossover_row_uniform(self, p1: Individual, p2: Individual) -> Individual:
        child_grid = []
        for r in range(9):
            src = p1 if random.random() < 0.5 else p2
            child_grid.append(src.grid[r][:])  
        return Individual(grid=child_grid)

   
    def _elitism_count(self) -> int:
        return max(1, int(self.config.elitism_rate * self.config.population_size))

    def _replace_with_immigrants(self, n: int) -> None:
        self.population.sort(key=lambda x: x.fitness, reverse=True)
        immigrants = [Individual.random_from_puzzle(self.puzzle) for _ in range(n)]
        for ind in immigrants:
            ind.evaluate(self.puzzle)
        self.population[-n:] = immigrants

    def evolve(self) -> Tuple[Individual, int]:
        if not self.population:
            self.initialize()

        best_fit = max(self.population, key=lambda x: x.fitness).fitness
        no_improve = 0
        mutation_rate = self.config.mutation_rate

        start = time.time()
        gen = 0

        while True:
            gen += 1

            
            if not self.config.run_until_solved and gen > self.config.generations:
                break
            if self.config.max_seconds is not None and (time.time() - start) > self.config.max_seconds:
                break

            self.population.sort(key=lambda x: x.fitness, reverse=True)

            best = self.population[0]
            avg = sum(ind.fitness for ind in self.population) / len(self.population)
            self.best_history.append(best.fitness)
            self.avg_history.append(avg)

            if self.puzzle.is_solved(best.grid):
                return best, gen

            if best.fitness > best_fit:
                best_fit = best.fitness
                no_improve = 0
                mutation_rate = self.config.mutation_rate  # reset
            else:
                no_improve += 1

            if no_improve >= self.config.stagnation_limit:
                mutation_rate = min(
                    self.config.mutation_rate_cap,
                    mutation_rate * self.config.mutation_boost
                )
                immigrants_n = max(1, int(self.config.immigrants_rate * self.config.population_size))
                self._replace_with_immigrants(immigrants_n)
                no_improve = 0

            elites_n = self._elitism_count()
            new_pop = [self.population[i].copy() for i in range(elites_n)]

            while len(new_pop) < self.config.population_size:
                parent1 = self.tournament_select()
                parent2 = self.tournament_select()

                if random.random() < self.config.crossover_rate:
                    child = self.crossover_row_uniform(parent1, parent2)
                else:
                    child = parent1.copy()

                if random.random() < mutation_rate:
                    child.mutate(self.puzzle)

                child.evaluate(self.puzzle)
                new_pop.append(child)

            self.population = new_pop

        
        self.population.sort(key=lambda x: x.fitness, reverse=True)
        return self.population[0], gen
