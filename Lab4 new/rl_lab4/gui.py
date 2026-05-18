import os
import sys
import tkinter as tk
from tkinter import ttk
import numpy as np

# Ensure the project root is on sys.path so the GUI can be run directly.
_pkg_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _pkg_root not in sys.path:
    sys.path.insert(0, _pkg_root)

from rl_lab4.gridworld import GridWorld
from rl_lab4.value_iteration import value_iteration
from rl_lab4.policy_iteration import policy_iteration


def make_rewards(R1, R2):
    # Construct the 5x5 reward matrix used in the assignment.
    rewards = np.zeros((5, 5), dtype=float)
    rewards[0] = [R1, 1, 0, -1, R2]
    for r in range(1, 5):
        rewards[r] = [2, 1, 0, -1, -2]
    return rewards


def policy_to_grid(policy, rows=5, cols=5):
    arrow = {0: '^', 1: 'v', 2: '<', 3: '>'}
    grid = [['' for _ in range(cols)] for _ in range(rows)]
    for (r, c), a in policy.items():
        grid[r][c] = 'T' if a is None else arrow[a]
    return grid


def values_to_grid(V, rows=5, cols=5):
    grid = [['' for _ in range(cols)] for _ in range(rows)]
    for r in range(rows):
        for c in range(cols):
            grid[r][c] = f"{V[(r, c)]:.2f}"
    return grid


def format_grid(grid):
    lines = []
    for row in grid:
        lines.append(' '.join(f"{cell:>6}" for cell in row))
    return '\n'.join(lines)


class GridworldGUI:
    def __init__(self, root):
        self.root = root
        root.title("Gridworld - Value & Policy Iteration")

        self.r1_var = tk.StringVar(value="100")
        self.r2_var = tk.StringVar(value="110")
        self.gamma_var = tk.StringVar(value="0.95")

        self._build_layout()

    def _build_layout(self):
        controls = ttk.Frame(self.root, padding=10)
        controls.grid(row=0, column=0, sticky="ew")

        ttk.Label(controls, text="R1:").grid(row=0, column=0, sticky="w")
        ttk.Entry(controls, textvariable=self.r1_var, width=8).grid(row=0, column=1, sticky="w")
        ttk.Label(controls, text="R2:").grid(row=0, column=2, sticky="w", padx=(10, 0))
        ttk.Entry(controls, textvariable=self.r2_var, width=8).grid(row=0, column=3, sticky="w")
        ttk.Label(controls, text="Gamma:").grid(row=0, column=4, sticky="w", padx=(10, 0))
        ttk.Entry(controls, textvariable=self.gamma_var, width=8).grid(row=0, column=5, sticky="w")

        ttk.Button(controls, text="Run Value Iteration", command=self.run_value_iteration).grid(
            row=1, column=0, columnspan=2, pady=(8, 0), sticky="ew"
        )
        ttk.Button(controls, text="Run Policy Iteration", command=self.run_policy_iteration).grid(
            row=1, column=2, columnspan=2, pady=(8, 0), sticky="ew"
        )
        ttk.Button(controls, text="Run Both", command=self.run_both).grid(
            row=1, column=4, columnspan=2, pady=(8, 0), sticky="ew"
        )

        output = ttk.Frame(self.root, padding=10)
        output.grid(row=1, column=0, sticky="nsew")
        self.root.rowconfigure(1, weight=1)
        self.root.columnconfigure(0, weight=1)
        output.columnconfigure(0, weight=1)
        output.columnconfigure(1, weight=1)

        self.vi_text = tk.Text(output, height=14, width=40)
        self.pi_text = tk.Text(output, height=14, width=40)
        self.vi_text.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        self.pi_text.grid(row=0, column=1, sticky="nsew")

        self.status_var = tk.StringVar(value="Ready")
        ttk.Label(self.root, textvariable=self.status_var, padding=(10, 0)).grid(
            row=2, column=0, sticky="w"
        )

    def _parse_inputs(self):
        try:
            r1 = float(self.r1_var.get().strip())
            r2 = float(self.r2_var.get().strip())
            gamma = float(self.gamma_var.get().strip())
        except ValueError:
            raise ValueError("R1, R2, and Gamma must be numbers.")
        return r1, r2, gamma

    def _build_env(self, r1, r2):
        rewards = make_rewards(r1, r2)
        return GridWorld(rewards, terminal_states=[(0, 0), (0, 4)])

    def _render(self, text_widget, title, V, policy):
        text_widget.configure(state="normal")
        text_widget.delete("1.0", tk.END)
        text_widget.insert(tk.END, f"{title}\n\n")
        text_widget.insert(tk.END, "Values:\n")
        text_widget.insert(tk.END, format_grid(values_to_grid(V)) + "\n\n")
        text_widget.insert(tk.END, "Policy:\n")
        text_widget.insert(tk.END, format_grid(policy_to_grid(policy)) + "\n")
        text_widget.configure(state="disabled")

    def run_value_iteration(self):
        try:
            r1, r2, gamma = self._parse_inputs()
            env = self._build_env(r1, r2)
            V, policy = value_iteration(env, gamma=gamma)
            self._render(self.vi_text, "Value Iteration", V, policy)
            self.status_var.set("Value Iteration complete")
        except Exception as exc:
            self.status_var.set(f"Error: {exc}")

    def run_policy_iteration(self):
        try:
            r1, r2, gamma = self._parse_inputs()
            env = self._build_env(r1, r2)
            V, policy = policy_iteration(env, gamma=gamma)
            # Bonus: compare multiple random-start PI policies to the VI policy.
            V_vi, policy_vi = value_iteration(env, gamma=gamma)
            matches = []
            for seed in range(10):
                _, pb = policy_iteration(env, gamma=gamma, random_seed=seed)
                matches.append(all((pb[s] == policy_vi[s]) for s in env.all_states()))
            all_match = all(matches)

            self._render(self.pi_text, "Policy Iteration", V, policy)
            self.pi_text.configure(state="normal")
            self.pi_text.insert(tk.END, "\nBonus check (10 random starts vs VI):\n")
            self.pi_text.insert(tk.END, f"All match VI policy: {all_match}\n")
            self.pi_text.configure(state="disabled")
            self.status_var.set("Policy Iteration complete")
        except Exception as exc:
            self.status_var.set(f"Error: {exc}")

    def run_both(self):
        self.run_value_iteration()
        self.run_policy_iteration()


if __name__ == "__main__":
    root = tk.Tk()
    app = GridworldGUI(root)
    root.mainloop()
