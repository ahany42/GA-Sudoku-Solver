import random
import matplotlib.pyplot as plt

from puzzle import SudokuPuzzle
from genetic_algo import GeneticAlgorithm, GAConfig


def main():
    random.seed(42)

    givens = [
        [5, 3, 0, 0, 7, 0, 0, 0, 0],
        [6, 0, 0, 1, 9, 5, 0, 0, 0],
        [0, 9, 8, 0, 0, 0, 0, 6, 0],
        [8, 0, 0, 0, 6, 0, 0, 0, 3],
        [4, 0, 0, 8, 0, 3, 0, 0, 1],
        [7, 0, 0, 0, 2, 0, 0, 0, 6],
        [0, 6, 0, 0, 0, 0, 2, 8, 0],
        [0, 0, 0, 4, 1, 9, 0, 0, 5],
        [0, 0, 0, 0, 8, 0, 0, 7, 9],
    ]

    puzzle = SudokuPuzzle(givens)

    config = GAConfig(
        population_size=800,
        generations=14000,
        tournament_k=3,
        elitism_rate=0.02,
        crossover_rate=0.9,
        mutation_rate=0.2,
        stagnation_limit=250,
        immigrants_rate=0.10,
        mutation_boost=1.5,
        mutation_rate_cap=0.8,
    )

    ga = GeneticAlgorithm(puzzle=puzzle, config=config)
    best, gen = ga.evolve()

    print(f"\nBest found at generation: {gen}")
    print(f"Fitness: {best.fitness:.6f}")
    print(f"Conflicts: {puzzle.total_conflicts(best.grid)}\n")
    print(puzzle.pretty(best.grid))

    plt.figure()
    plt.plot(ga.best_history, label="Best fitness")
    plt.plot(ga.avg_history, label="Average fitness")
    plt.xlabel("Generation")
    plt.ylabel("Fitness (higher is better)")
    plt.title("Genetic Algorithm Fitness Progress")
    plt.legend()
    plt.show()


if __name__ == "__main__":
    main()
