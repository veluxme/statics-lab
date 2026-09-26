"""
Static visualization of the 2D truss defined in `statics.py`.

This module does no structural calculation of its own: it draws the
geometry, supports and load, and (optionally) labels the internal
forces and reactions returned by `statics.solve_truss`. `statics.py`
remains the single source of truth for geometry and physics.

Run directly with:

    python src/visualization.py
"""

from __future__ import annotations

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Polygon, Rectangle

from statics import (
    NODES,
    BARS,
    REACTIONS,
    calculate_weight,
    solve_truss,
    check_equilibrium,
    classify_force,
)


# --------------------------------------------------------------------
# Configurações visuais
# --------------------------------------------------------------------

FIGURE_SIZE = (8.0, 6.0)

BAR_COLOR = "#333333"
BAR_LINEWIDTH = 2.2

NODE_COLOR = "#1a1a1a"
NODE_MARKER_SIZE = 7
NODE_LABEL_OFFSET_POINTS = 10
NODE_LABEL_FONTSIZE = 11

SUPPORT_COLOR = "#4d4d4d"
SUPPORT_SIZE = 0.35            # visual size (m), not a physical quantity
ROLLER_RADIUS = SUPPORT_SIZE * 0.14
GROUND_HATCH_COUNT = 5
GROUND_HATCH_LENGTH = SUPPORT_SIZE * 0.18

LOAD_COLOR = "#c0392b"
LOAD_ROPE_LENGTH = 0.45        # visual only — not a physical length
LOAD_BLOCK_SIZE = 0.3
LOAD_ARROW_LENGTH = 0.35
LOAD_FONTSIZE = 9

TENSION_COLOR = "#2166ac"
COMPRESSION_COLOR = "#b2182b"
ZERO_FORCE_COLOR = "#808080"
FORCE_LABEL_FONTSIZE = 7.5
FORCE_LABEL_OFFSET = 0.38      # perpendicular offset from bar midpoint (m)

REACTIONS_BOX_FONTSIZE = 8.5

PLOT_MARGIN = 0.8
EQUILIBRIUM_TOLERANCE = 1e-8


# --------------------------------------------------------------------
# Funções auxiliares de desenho: geometria da treliça
# --------------------------------------------------------------------

def plot_bars(ax: plt.Axes) -> None:
    """Draw every bar as a straight line between its two nodes."""
    for start, end in BARS:
        x_values = [NODES[start][0], NODES[end][0]]
        y_values = [NODES[start][1], NODES[end][1]]
        ax.plot(x_values, y_values, color=BAR_COLOR, linewidth=BAR_LINEWIDTH, zorder=1)


def plot_nodes(ax: plt.Axes) -> None:
    """Draw a marker and a label for every node."""
    for name, position in NODES.items():
        x, y = position
        ax.plot(x, y, "o", color=NODE_COLOR, markersize=NODE_MARKER_SIZE, zorder=3)
        ax.annotate(
            name,
            xy=(x, y),
            xytext=(0, NODE_LABEL_OFFSET_POINTS),
            textcoords="offset points",
            ha="center",
            va="bottom",
            fontsize=NODE_LABEL_FONTSIZE,
            fontweight="bold",
            zorder=4,
        )


# --------------------------------------------------------------------
# Funções auxiliares de desenho: apoios
# --------------------------------------------------------------------

def _support_types() -> dict[str, str]:
    """
    Infer each support's type directly from REACTIONS instead of
    hard-coding which node is a pin and which is a roller.

    A node with both an "x" and a "y" reaction is a pin (fully fixed);
    a node with only a "y" reaction is a roller.
    """
    directions_by_node: dict[str, set[str]] = {}
    for node, direction, _ in REACTIONS:
        directions_by_node.setdefault(node, set()).add(direction)

    return {
        node: ("pin" if directions == {"x", "y"} else "roller")
        for node, directions in directions_by_node.items()
    }


def _draw_ground_hatching(ax: plt.Axes, x: float, y: float, half_width: float) -> None:
    """Draw a ground line with small hatch marks under a support."""
    ax.plot(
        [x - half_width * 1.3, x + half_width * 1.3],
        [y, y],
        color=SUPPORT_COLOR,
        linewidth=1.2,
        zorder=2,
    )

    step = (half_width * 2.2) / (GROUND_HATCH_COUNT - 1)
    for i in range(GROUND_HATCH_COUNT):
        hatch_x = x - half_width * 1.1 + i * step
        ax.plot(
            [hatch_x, hatch_x - GROUND_HATCH_LENGTH],
            [y, y - GROUND_HATCH_LENGTH],
            color=SUPPORT_COLOR,
            linewidth=1.0,
            zorder=2,
        )


def _draw_support_triangle(ax: plt.Axes, x: float, y: float) -> float:
    """Draw the triangle common to both support symbols; return its base y."""
    half_width = SUPPORT_SIZE / 2
    base_y = y - SUPPORT_SIZE

    triangle = Polygon(
        [(x, y), (x - half_width, base_y), (x + half_width, base_y)],
        closed=True,
        facecolor=SUPPORT_COLOR,
        edgecolor=SUPPORT_COLOR,
        zorder=2,
    )
    ax.add_patch(triangle)
    return base_y


def _draw_pin_support(ax: plt.Axes, position: np.ndarray) -> None:
    """Draw a pinned (fixed) support: a triangle resting directly on hatched ground."""
    x, y = position
    base_y = _draw_support_triangle(ax, x, y)
    _draw_ground_hatching(ax, x, base_y, SUPPORT_SIZE / 2)


def _draw_roller_support(ax: plt.Axes, position: np.ndarray) -> None:
    """Draw a roller support: a triangle resting on small circles (free to roll)."""
    x, y = position
    base_y = _draw_support_triangle(ax, x, y)

    roller_y = base_y - ROLLER_RADIUS
    for roller_x in (x - SUPPORT_SIZE * 0.25, x + SUPPORT_SIZE * 0.25):
        ax.add_patch(
            Circle(
                (roller_x, roller_y),
                ROLLER_RADIUS,
                facecolor=SUPPORT_COLOR,
                edgecolor=SUPPORT_COLOR,
                zorder=2,
            )
        )

    _draw_ground_hatching(ax, x, roller_y - ROLLER_RADIUS, SUPPORT_SIZE / 2)


def plot_supports(ax: plt.Axes) -> None:
    """Draw every support, automatically choosing the pin or roller symbol."""
    for node, support_type in _support_types().items():
        position = NODES[node]
        if support_type == "pin":
            _draw_pin_support(ax, position)
        else:
            _draw_roller_support(ax, position)


# --------------------------------------------------------------------
# Desenho da carga
# --------------------------------------------------------------------

def plot_load(ax: plt.Axes, load_node: str, mass: float) -> None:
    """
    Draw the applied load at `load_node`: a rope, a hanging block, and a
    downward force arrow labeled with the mass and weight.

    The rope length and block size are fixed visual sizes — they do not
    represent any physical quantity, only where to draw the load below
    the node.
    """
    x, y = NODES[load_node]
    weight = calculate_weight(mass)

    rope_bottom_y = y - LOAD_ROPE_LENGTH
    ax.plot([x, x], [y, rope_bottom_y], color=LOAD_COLOR, linewidth=1.5, zorder=2)

    block_bottom_y = rope_bottom_y - LOAD_BLOCK_SIZE
    block = Rectangle(
        (x - LOAD_BLOCK_SIZE / 2, block_bottom_y),
        LOAD_BLOCK_SIZE,
        LOAD_BLOCK_SIZE,
        facecolor=LOAD_COLOR,
        edgecolor=LOAD_COLOR,
        alpha=0.85,
        zorder=2,
    )
    ax.add_patch(block)

    arrow_end_y = block_bottom_y - LOAD_ARROW_LENGTH
    ax.annotate(
        "",
        xy=(x, arrow_end_y),
        xytext=(x, block_bottom_y),
        arrowprops=dict(arrowstyle="-|>", color=LOAD_COLOR, linewidth=2),
        zorder=2,
    )

    label = f"{mass:.0f} kg\nP = {weight:.1f} N"
    ax.annotate(
        label,
        xy=(x, arrow_end_y),
        xytext=(8, -4),
        textcoords="offset points",
        ha="left",
        va="top",
        fontsize=LOAD_FONTSIZE,
        color=LOAD_COLOR,
    )


# --------------------------------------------------------------------
# Visualização das forças (barras e reações)
# --------------------------------------------------------------------

_FORCE_COLORS = {
    "tension": TENSION_COLOR,
    "compression": COMPRESSION_COLOR,
    "zero": ZERO_FORCE_COLOR,
}


def plot_internal_forces(ax: plt.Axes, solution: np.ndarray) -> None:
    """
    Label each bar with its internal force magnitude and state
    (tension / compression / zero), using `classify_force` from
    `statics.py` as the single source of truth for that classification.
    """
    for index, (start, end) in enumerate(BARS):
        force = solution[index]
        state = classify_force(force)

        start_pos = NODES[start]
        end_pos = NODES[end]
        midpoint = (start_pos + end_pos) / 2

        direction = end_pos - start_pos
        length = np.linalg.norm(direction)
        normal = np.array([-direction[1], direction[0]]) / length
        label_position = midpoint + normal * FORCE_LABEL_OFFSET

        ax.annotate(
            f"{abs(force):.1f} N\n({state})",
            xy=label_position,
            ha="center",
            va="center",
            fontsize=FORCE_LABEL_FONTSIZE,
            color=_FORCE_COLORS[state],
            zorder=4,
            bbox=dict(boxstyle="round,pad=0.15", facecolor="white", edgecolor="none", alpha=0.75),
        )


def plot_support_reactions(ax: plt.Axes, solution: np.ndarray) -> None:
    """Display the support reaction values as a small text box on the figure."""
    lines = [f"{node}{direction} = {solution[column]:.1f} N" for node, direction, column in REACTIONS]
    text = "Reactions:\n" + "\n".join(lines)

    ax.text(
        0.02,
        0.02,
        text,
        transform=ax.transAxes,
        fontsize=REACTIONS_BOX_FONTSIZE,
        va="bottom",
        ha="left",
        bbox=dict(boxstyle="round,pad=0.4", facecolor="white", edgecolor=SUPPORT_COLOR, alpha=0.9),
    )


# --------------------------------------------------------------------
# Validação
# --------------------------------------------------------------------

def is_equilibrium_valid(
    solution: np.ndarray,
    load_node: str,
    mass: float,
    tolerance: float = EQUILIBRIUM_TOLERANCE,
) -> bool:
    """Return whether a solved truss actually satisfies equilibrium."""
    residual = check_equilibrium(solution, load_node, mass)
    return bool(np.all(np.abs(residual) < tolerance))


# --------------------------------------------------------------------
# Função principal de desenho
# --------------------------------------------------------------------

def _set_plot_limits(ax: plt.Axes) -> None:
    """Fit the axis limits to the structure, leaving room for supports and the load."""
    xs = [position[0] for position in NODES.values()]
    ys = [position[1] for position in NODES.values()]

    load_drop = LOAD_ROPE_LENGTH + LOAD_BLOCK_SIZE + LOAD_ARROW_LENGTH

    ax.set_xlim(min(xs) - PLOT_MARGIN, max(xs) + PLOT_MARGIN)
    ax.set_ylim(min(ys) - PLOT_MARGIN - SUPPORT_SIZE - load_drop, max(ys) + PLOT_MARGIN)


def plot_truss(
    load_node: str = "D",
    mass: float = 100.0,
    solution: np.ndarray | None = None,
    show_forces: bool = False,
    show_reactions: bool = False,
) -> plt.Figure:
    """
    Draw the truss: bars, nodes, supports, and the applied load, with
    optional labeling of internal forces and support reactions.

    If `solution` is not given, it is computed with
    `solve_truss(load_node, mass)`. Pass a precomputed solution to avoid
    solving twice when the caller already has one.
    """
    if solution is None:
        solution = solve_truss(load_node, mass)

    fig, ax = plt.subplots(figsize=FIGURE_SIZE)

    plot_bars(ax)
    plot_nodes(ax)
    plot_supports(ax)
    plot_load(ax, load_node, mass)

    if show_forces:
        plot_internal_forces(ax, solution)

    if show_reactions:
        plot_support_reactions(ax, solution)

    ax.set_xlabel("x (m)")
    ax.set_ylabel("y (m)")
    ax.set_title(f"2D Truss — {mass:.0f} kg load at node {load_node}")
    ax.set_aspect("equal")
    ax.grid(True, linestyle="--", linewidth=0.5, alpha=0.4)

    _set_plot_limits(ax)
    fig.tight_layout()

    return fig


# --------------------------------------------------------------------
# Main
# --------------------------------------------------------------------

def main() -> None:
    mass = 100.0
    load_node = "D"

    solution = solve_truss(load_node, mass)

    if not is_equilibrium_valid(solution, load_node, mass):
        raise RuntimeError(
            f"solve_truss returned a solution that does not satisfy "
            f"equilibrium for load_node={load_node!r}, mass={mass} kg "
            f"(tolerance={EQUILIBRIUM_TOLERANCE}). Refusing to plot it as valid."
        )

    plot_truss(
        load_node=load_node,
        mass=mass,
        solution=solution,
        show_forces=True,
        show_reactions=True,
    )
    plt.show()


if __name__ == "__main__":
    main()