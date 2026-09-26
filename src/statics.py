"""
Statically determinate 2D truss solver.

Given a fixed geometry (nodes + bars) and a single vertical load applied
at one node, this script builds the joint-equilibrium system for the
whole truss, solves it for the internal bar forces and support
reactions, and reports the results.

Supports: pin at node A (Ax, Ay) and roller at node B (By).
"""

import numpy as np


# --------------------------------------------------------------------
# Geometry
# --------------------------------------------------------------------

NODES: dict[str, np.ndarray] = {
    "A": np.array([0.0, 0.0]),
    "B": np.array([4.0, 0.0]),
    "C": np.array([0.0, 3.0]),
    "D": np.array([2.0, 1.5]),
    "E": np.array([2.0, 0.0]),
}

BARS: list[tuple[str, str]] = [
    ("A", "C"),
    ("A", "D"),
    ("C", "D"),
    ("D", "E"),
    ("D", "B"),
    ("E", "B"),
    ("A", "E"),
]

GRAVITY = 9.81

# Derived sizes, computed once so the numbers below always stay
# consistent with the geometry above instead of being hard-coded.
NODE_NAMES: list[str] = list(NODES.keys())
NODE_INDEX: dict[str, int] = {name: i for i, name in enumerate(NODE_NAMES)}

N_NODES = len(NODES)
N_BARS = len(BARS)
N_REACTIONS = 3
N_UNKNOWNS = N_BARS + N_REACTIONS

# Support reactions: (node, direction, column index in the unknowns vector).
# Pin at A (horizontal + vertical), roller at B (vertical only).
REACTIONS: list[tuple[str, str, int]] = [
    ("A", "x", N_BARS),
    ("A", "y", N_BARS + 1),
    ("B", "y", N_BARS + 2),
]


# --------------------------------------------------------------------
# Geometry helpers
# --------------------------------------------------------------------

def bar_length(node_1: str, node_2: str) -> float:
    """Return the length of a bar between two nodes."""
    position_1 = NODES[node_1]
    position_2 = NODES[node_2]

    return np.linalg.norm(position_2 - position_1)


def unit_vector(node_1: str, node_2: str) -> np.ndarray:
    """Return the unit vector pointing from node_1 to node_2."""
    vector = NODES[node_2] - NODES[node_1]
    length = np.linalg.norm(vector)

    return vector / length


# --------------------------------------------------------------------
# Topology helpers
# --------------------------------------------------------------------

def connected_bars(node: str) -> list[int]:
    """Return the indices (into BARS) of every bar touching a node."""
    return [
        index
        for index, (node_1, node_2) in enumerate(BARS)
        if node in (node_1, node_2)
    ]


def bar_direction(node: str, bar: tuple[str, str]) -> np.ndarray:
    """Return the unit vector of a bar, pointing away from the given node."""
    node_1, node_2 = bar

    if node == node_1:
        return unit_vector(node_1, node_2)

    return unit_vector(node_2, node_1)


# --------------------------------------------------------------------
# Equilibrium system
# --------------------------------------------------------------------

def build_equilibrium_matrix() -> np.ndarray:
    """
    Build the full equilibrium coefficient matrix for the truss.

    Each node contributes two rows (sum Fx = 0, sum Fy = 0). Each
    column is an unknown: the first N_BARS columns are bar forces
    (positive = tension), and the last N_REACTIONS columns are the
    support reactions listed in REACTIONS.
    """
    matrix = []

    for node in NODE_NAMES:
        row_x = np.zeros(N_UNKNOWNS)
        row_y = np.zeros(N_UNKNOWNS)

        for index in connected_bars(node):
            direction = bar_direction(node, BARS[index])
            row_x[index] = direction[0]
            row_y[index] = direction[1]

        for reaction_node, direction, column in REACTIONS:
            if reaction_node != node:
                continue
            if direction == "x":
                row_x[column] = 1.0
            else:
                row_y[column] = 1.0

        matrix.append(row_x)
        matrix.append(row_y)

    return np.array(matrix)


# The geometry is fixed, so the equilibrium matrix is too: build it
# once and reuse it instead of recomputing it on every solve/check.
EQUILIBRIUM_MATRIX = build_equilibrium_matrix()


# --------------------------------------------------------------------
# Loads
# --------------------------------------------------------------------

def calculate_weight(mass: float) -> float:
    """Return the weight (N) of a given mass (kg) under gravity."""
    return mass * GRAVITY


def build_load_vector(load_node: str, load: float) -> np.ndarray:
    """Build the external load vector for a single downward vertical load."""
    vector = np.zeros(2 * N_NODES)

    y_index = 2 * NODE_INDEX[load_node] + 1
    vector[y_index] = -load

    return vector


# --------------------------------------------------------------------
# Solver
# --------------------------------------------------------------------

def solve_truss(load_node: str, mass: float) -> np.ndarray:
    """
    Solve the truss for a vertical load (from `mass`) applied at `load_node`.

    Returns a vector of N_UNKNOWNS values: bar forces (in BARS order),
    followed by the support reactions (in REACTIONS order).
    """
    load = calculate_weight(mass)
    load_vector = build_load_vector(load_node, load)

    return np.linalg.solve(EQUILIBRIUM_MATRIX, -load_vector)


def check_equilibrium(solution: np.ndarray, load_node: str, mass: float) -> np.ndarray:
    """Return the equilibrium residual for a solution (should be ~0 everywhere)."""
    load = calculate_weight(mass)
    load_vector = build_load_vector(load_node, load)

    return EQUILIBRIUM_MATRIX @ solution + load_vector


# --------------------------------------------------------------------
# Reporting
# --------------------------------------------------------------------

def classify_force(force: float, tolerance: float = 1e-9) -> str:
    """Classify a bar force as tension, compression, or (numerically) zero."""
    if abs(force) < tolerance:
        return "zero"

    if force > 0:
        return "tension"

    return "compression"


def print_internal_forces(solution: np.ndarray) -> None:
    """Print each bar's internal force and its tension/compression state."""
    print("\nInternal forces:")

    for index, (start, end) in enumerate(BARS):
        force = solution[index]
        state = classify_force(force)
        print(f"{start}{end} = {force:.2f} N ({state})")


# --------------------------------------------------------------------
# Main
# --------------------------------------------------------------------

def main() -> None:
    mass = 100.0
    load_node = "D"

    solution = solve_truss(load_node, mass)

    print("\nTruss solution:")
    print_internal_forces(solution)

    residual = check_equilibrium(solution, load_node, mass)
    print("\nEquilibrium residuals:")
    print(residual)


if __name__ == "__main__":
    main()