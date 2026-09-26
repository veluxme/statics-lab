import numpy as np


# -------------------------
# Geometry
# -------------------------

NODES = {
    "A": np.array([0.0, 0.0]),
    "B": np.array([4.0, 0.0]),
    "C": np.array([0.0, 3.0]),
    "D": np.array([2.0, 1.5]),
    "E": np.array([2.0, 0.0]),
}


BARS = [
    ("A", "C"),
    ("A", "D"),
    ("C", "D"),
    ("D", "E"),
    ("D", "B"),
    ("E", "B"),
    ("A", "E"),
]


GRAVITY = 9.81

def bar_length(node_1, node_2):
    """Return the length of a bar between two nodes."""
    position_1 = NODES[node_1]
    position_2 = NODES[node_2]

    return np.linalg.norm(position_2 - position_1)

if __name__ == "__main__":
    print("A =", NODES["A"])
    print("B =", NODES["B"])
    print("C =", NODES["C"])
    print("D =", NODES["D"])
    print("E =", NODES["E"])

    print("\nBar lengths:")

    print("AC =", bar_length("A", "C"))
    print("AB =", bar_length("A", "B"))
    print("CB =", bar_length("C", "B"))
    print("AD =", bar_length("A", "D"))
    print("DB =", bar_length("D", "B"))
    print("DE =", bar_length("D", "E"))