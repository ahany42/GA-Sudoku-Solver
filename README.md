# 🧬 GA‑Sudoku‑Solver

A Sudoku solver implemented using a **Genetic Algorithm (GA)**, with both a **command-line interface** and a **Streamlit web app** for interactive puzzle input, GA configuration, and results visualization.

---

## 🚀 Features

- 🧩 **Interactive Sudoku input** — enter or edit givens in the browser  
- 🧬 **Genetic Algorithm solver** with configurable evolution parameters  
- 📈 **Fitness visualization** showing GA progress over generations  
- 🧠 Supports **elitism, tournament selection, adaptive mutation, and stagnation handling**  
- 🖼️ **Streamlit UI** for end-to-end solving and display  
- 📊 **Matplotlib charts** for fitness history  
- 🧪 **Prettified console output** for CLI use  

---

## 📁 Repository Structure

```bash
├── app.py # Streamlit web application
├── genetic_algo.py # GA and configuration logic
├── individual.py # GA Individual class
├── puzzle.py # SudokuPuzzle class
├── run_ga.py # CLI entry point (optional)
└── README.md
```


---

## ⚙️ Installation

Clone the repository and navigate to the folder:

```bash
git clone https://github.com/ahany42/GA-Sudoku-Solver.git
cd GA-Sudoku-Solver
```
Install Python dependencies:

```bash
Copy code
pip install streamlit matplotlib
Python 3.7+ is recommended.
```
🧠 Usage
```bash
Run Streamlit app.py
```

Enter Sudoku givens (0 = empty)

Configure GA parameters (population, crossover, mutation, etc.)

Click “🚀 Solve with GA”

View best solution & fitness charts


## 📌 Core Classes
🧩 SudokuPuzzle
Immutable puzzle definition using @dataclass(frozen=True)

Computes total conflicts, fitness score, and performs sanity checks


## 🧪 GeneticAlgorithm
Implements evolutionary loop with:

✔ Tournament selection

✔ Row-wise uniform crossover

✔ Elitism

✔ Adaptive mutation & stagnation

✔ Immigrants injection
