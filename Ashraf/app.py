# app.py
import streamlit as st
import matplotlib.pyplot as plt
import time

from puzzle import SudokuPuzzle
from genetic_algo import GeneticAlgorithm, GAConfig

st.set_page_config(page_title="Sudoku GA Solver", layout="wide")

# -----------------------
# Helpers
# -----------------------
DEFAULT_GIVENS = [
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


def init_state():
    if "givens" not in st.session_state:
        st.session_state.givens = [row[:] for row in DEFAULT_GIVENS]
    if "solved_grid" not in st.session_state:
        st.session_state.solved_grid = None
    if "result_info" not in st.session_state:
        st.session_state.result_info = None


def clamp_cell(v):
    if v is None:
        return 0
    v = int(v)
    return v if 0 <= v <= 9 else 0


def render_grid_editor(title, grid, editable=True, key_prefix="cell"):
    st.subheader(title)
    for r in range(9):
        row_cols = st.columns(
            [1, 1, 1, 0.15, 1, 1, 1, 0.15, 1, 1, 1], gap="small")
        for c in range(9):
            col_index = c + (1 if c >= 3 else 0) + (1 if c >= 6 else 0)
            with row_cols[col_index]:
                val = int(grid[r][c])
                new_val = st.number_input(
                    label=f"r{r+1}c{c+1}",
                    min_value=0,
                    max_value=9,
                    value=val,
                    step=1,
                    disabled=not editable,
                    label_visibility="collapsed",
                    key=f"{key_prefix}_{r}_{c}",
                )
                grid[r][c] = clamp_cell(new_val)

        if r in (2, 5):
            st.markdown("---")


def show_solution_grid(grid, givens):
    st.subheader("Best Solution Found")

    # Build HTML table
    html = """
    <style>
    .sudoku { border-collapse: collapse; margin-top: 10px; }
    .sudoku td {
        width: 46px; height: 46px;
        text-align: center; vertical-align: middle;
        font-size: 22px; font-weight: 600;
        border: 1px solid #666;
        border-radius: 6px;
    }
    .given { background: rgba(255,255,255,0.08); font-weight: 800; }
    .thick-top    { border-top: 3px solid #aaa !important; }
    .thick-left   { border-left: 3px solid #aaa !important; }
    .thick-right  { border-right: 3px solid #aaa !important; }
    .thick-bottom { border-bottom: 3px solid #aaa !important; }
    </style>
    <table class="sudoku">
    """

    for r in range(9):
        html += "<tr>"
        for c in range(9):
            classes = []
            if givens[r][c] != 0:
                classes.append("given")

            # 3x3 borders
            if r in (0, 3, 6):
                classes.append("thick-top")
            if c in (0, 3, 6):
                classes.append("thick-left")
            if r in (2, 5, 8):
                classes.append("thick-bottom")
            if c in (2, 5, 8):
                classes.append("thick-right")

            class_str = " ".join(classes)
            html += f'<td class="{class_str}">{grid[r][c]}</td>'
        html += "</tr>"
    html += "</table>"

    st.markdown(html, unsafe_allow_html=True)


# -----------------------
# UI
# -----------------------
init_state()

st.title("🧬 Sudoku Solver with Genetic Algorithm (Streamlit GUI)")

left, right = st.columns([1.15, 1], gap="large")

with left:
    st.markdown("### 1) Enter / Edit Sudoku Givens (0 = empty)")
    givens = st.session_state.givens

    render_grid_editor(
        title="Sudoku Input Grid",
        grid=givens,
        editable=True,
        key_prefix="given",
    )

    colA, colB, colC = st.columns(3)
    with colA:
        if st.button("Reset to Default", use_container_width=True):
            st.session_state.givens = [row[:] for row in DEFAULT_GIVENS]
            st.session_state.solved_grid = None
            st.session_state.result_info = None
            st.rerun()

    with colB:
        if st.button("Clear All", use_container_width=True):
            st.session_state.givens = [[0] * 9 for _ in range(9)]
            st.session_state.solved_grid = None
            st.session_state.result_info = None
            st.rerun()

    with colC:
        st.download_button(
            "Download Givens (CSV)",
            data="\n".join(",".join(map(str, row)) for row in givens),
            file_name="givens.csv",
            mime="text/csv",
            use_container_width=True,
        )

with right:
    st.markdown("### 2) GA Settings")

    pop = st.number_input("Population size", min_value=50,
                          max_value=5000, value=400, step=50)

    run_until_solved = st.checkbox(
        "Run until solved (0 conflicts)", value=False)
    if run_until_solved:
        st.caption("Note: This uses a time limit to avoid infinite running.")
        max_seconds = st.number_input(
            "Max runtime (seconds)", min_value=5, max_value=3600, value=60, step=5)
        gens = st.number_input("Max generations (fallback)", min_value=500,
                               max_value=50000, value=12000, step=500, disabled=True)
    else:
        max_seconds = st.number_input(
            "Max runtime (seconds)", min_value=5, max_value=3600, value=60, step=5)
        gens = st.number_input(
            "Max generations", min_value=500, max_value=50000, value=12000, step=500)

    tourn = st.number_input("Tournament k", min_value=2,
                            max_value=10, value=3, step=1)

    elit = st.slider("Elitism rate", 0.0, 0.10, 0.02, 0.01)
    cross = st.slider("Crossover rate", 0.0, 1.0, 0.90, 0.01)
    mut = st.slider("Mutation rate", 0.0, 1.0, 0.20, 0.01)

    st.markdown("#### Stagnation Handling")
    stag = st.number_input("Stagnation limit (gens)",
                           min_value=50, max_value=5000, value=250, step=50)
    imm = st.slider("Immigrants rate", 0.0, 0.50, 0.10, 0.01)
    boost = st.slider("Mutation boost", 1.0, 5.0, 1.5, 0.1)
    mut_cap = st.slider("Mutation rate cap", 0.0, 1.0, 0.80, 0.01)

    solve_btn = st.button("🚀 Solve with GA", type="primary",
                          use_container_width=True)

    st.markdown("---")

    if solve_btn:
        puzzle = SudokuPuzzle([row[:] for row in st.session_state.givens])

        # IMPORTANT:
        # This requires you to add these fields to GAConfig + evolve() logic:
        #   run_until_solved: bool
        #   max_seconds: float
        config = GAConfig(
            population_size=int(pop),
            generations=int(gens),
            tournament_k=int(tourn),
            elitism_rate=float(elit),
            crossover_rate=float(cross),
            mutation_rate=float(mut),
            stagnation_limit=int(stag),
            immigrants_rate=float(imm),
            mutation_boost=float(boost),
            mutation_rate_cap=float(mut_cap),
            run_until_solved=bool(run_until_solved),
            max_seconds=float(max_seconds),
        )

        ga = GeneticAlgorithm(puzzle=puzzle, config=config)

        status = st.empty()
        prog = st.progress(0)

        start = time.time()
        status.info("Running GA...")

        best, gen_found = ga.evolve()

        elapsed = time.time() - start
        conflicts = puzzle.total_conflicts(best.grid)
        fitness = best.fitness

        st.session_state.solved_grid = best.grid
        st.session_state.result_info = {
            "gen_found": gen_found,
            "elapsed": elapsed,
            "conflicts": conflicts,
            "fitness": fitness,
            "best_history": ga.best_history,
            "avg_history": ga.avg_history,
        }

        prog.progress(100)
        status.success(
            f"Done in {elapsed:.2f}s | Best gen: {gen_found} | Conflicts: {conflicts} | Fitness: {fitness:.6f}"
        )

    # Results
    if st.session_state.solved_grid is not None:
        info = st.session_state.result_info

        st.markdown("### 3) Results")
        st.write(f"**Best generation:** {info['gen_found']}")
        st.write(f"**Runtime:** {info['elapsed']:.2f}s")
        st.write(f"**Conflicts:** {info['conflicts']}")
        st.write(f"**Fitness:** {info['fitness']:.6f}")

        if info["conflicts"] == 0:
            st.success("✅ Perfect Sudoku solution found!")
        else:
            st.warning(
                "Not perfect yet. Increase runtime / population, or add local repair.")

        show_solution_grid(st.session_state.solved_grid,
                           st.session_state.givens)

        st.markdown("### Fitness Progress")
        fig = plt.figure()
        plt.plot(info["best_history"], label="Best fitness")
        plt.plot(info["avg_history"], label="Average fitness")
        plt.xlabel("Generation")
        plt.ylabel("Fitness")
        plt.legend()
        st.pyplot(fig)
