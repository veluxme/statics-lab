# STATICS LAB

🇧🇷 [Leia em português](README.pt-BR.md) · 🇺🇸 **Read in English**

![Python](https://img.shields.io/badge/python-3.x-3776AB?logo=python&logoColor=white)
![Status](https://img.shields.io/badge/status-educational%20project-yellow)

> An educational computational laboratory for analyzing a 2D truss using Python, linear algebra, and static equilibrium.

---

## Table of Contents

- [Overview](#overview)
- [Demonstration](#demonstration)
- [Problem Statement](#problem-statement)
- [Physical Model](#physical-model)
- [Assumptions](#assumptions)
- [Mathematical Model](#mathematical-model)
- [Force Decomposition](#force-decomposition)
- [Load Model](#load-model)
- [Numerical Method](#numerical-method)
- [Equilibrium Validation](#equilibrium-validation)
- [Example](#example)
- [Project Structure](#project-structure)
- [statics.py](#staticspy)
- [visualization.py](#visualizationpy)
- [Installation](#installation)
- [Running the Project](#running-the-project)
- [Development Philosophy](#development-philosophy)
- [Roadmap](#roadmap)
- [Limitations](#limitations)
- [Validation](#validation)
- [Educational Purpose](#educational-purpose)
- [Technologies](#technologies)
- [License](#license)

---

## Overview

A **truss** is a structure made of straight, slender members connected at joints (nodes) and loaded only at those joints, so that every member carries a purely axial force — either tension or compression. Trusses are one of the foundational structures in mechanical and civil engineering, and their analysis is one of the clearest places where **statics** and **linear algebra** meet.

**Statics Lab** is a small educational project that models a 2D truss, sets up its equilibrium equations, and solves for the internal member forces and support reactions using Python and NumPy. The goal is not to build a full structural-analysis tool, but to work through — end to end, in code — the chain that connects a physical engineering problem to a mathematical model, and that model to a numerical solution.

The current version analyzes a single, fixed, **statically determinate** plane truss with:

- 5 nodes;
- 7 members;
- a pin support at node A;
- a roller support at node B;
- one vertical load applied at a chosen node.

Future versions are intended to let the user choose where the load is applied and observe how the internal forces respond (see [Roadmap](#roadmap)).

## Demonstration

![Truss visualization](assets/truss_visualization.png)

*Expected asset — not yet included in the repository.* Once available, the image above will show the truss geometry, the supports, and a vertical load applied at node D, as produced by `visualization.py`.

## Problem Statement

The central question this project explores is:

> How do the internal forces of a statically determinate truss change when a load is applied at different nodes?

The intended (and partly still-future) workflow is:

1. Choose a node where a load will be applied.
2. Define the mass of a block placed at that node.
3. Compute the corresponding weight.
4. Solve for the internal member forces and support reactions.
5. Classify each member as tension or compression.
6. Verify that the equilibrium equations are satisfied.
7. Eventually, evaluate the load position against explicitly defined criteria.

Step 7 — evaluating whether a given node is an "adequate" location for a load — is **not implemented yet**. It is a planned extension (see [Roadmap](#roadmap) and [Limitations](#limitations)), not a current feature.

## Physical Model

**Nodes**

| Node | x (m) | y (m) |
|------|------:|------:|
| A    | 0.0   | 0.0   |
| B    | 4.0   | 0.0   |
| C    | 0.0   | 3.0   |
| D    | 2.0   | 1.5   |
| E    | 2.0   | 0.0   |

**Members**

| Member |
|--------|
| AC     |
| AD     |
| CD     |
| DE     |
| DB     |
| EB     |
| AE     |

- Node **A** is a **pin support** (restrains horizontal and vertical displacement).
- Node **B** is a **roller support** (restrains vertical displacement only).
- The structure is fully **planar (2D)**.
- **D** lies at the midpoint of segment **CB**.
- **E** lies at the midpoint of segment **AB**.
- The outer triangle **A–B–C** has side lengths 4 m, 3 m, and 5 m — the familiar 3-4-5 right triangle. This relationship applies to the outer geometry only; the internal members (AD, CD, DB, DE, AE) have their own, distinct geometries and angles.

## Assumptions

The model rests on a set of explicit simplifications that define its scope:

- 2D planar truss;
- joints idealized as frictionless pins;
- members carry axial force only (no bending);
- loads are applied only at joints;
- support A provides horizontal and vertical reactions;
- support B provides a vertical reaction only;
- the structure is in static equilibrium;
- gravitational acceleration $g = 9.81\ \text{m/s}^2$;
- the current model supports a single vertical load at a time;
- members are treated as ideal, weightless truss elements;
- **deformation is not currently modeled**;
- **material properties are not currently modeled**;
- **buckling is not currently modeled**;
- **stress distribution within members is not currently modeled**.

## Mathematical Model

Each joint of the truss must satisfy static equilibrium in both directions:

$$
\sum F_x = 0 \qquad \sum F_y = 0
$$

With 5 nodes, this gives:

$$
2 \times 5 = 10
$$

independent equilibrium equations.

The unknown vector combines the 7 internal member forces with the 3 support reaction components:

$$
7 + 3 = 10
$$

unknowns — exactly matching the number of equations, which is what makes the truss **statically determinate**.

The system is assembled into a single linear system:

$$
\mathbf{A}\mathbf{x} = \mathbf{b}
$$

where:

- $\mathbf{A}$ is the equilibrium matrix, built from the unit direction vectors of every member meeting at each node;
- $\mathbf{x}$ is the vector of unknowns;
- $\mathbf{b}$ is the external load vector.

$$
\mathbf{x} =
\begin{bmatrix}
F_{AC} & F_{AD} & F_{CD} & F_{DE} & F_{DB} & F_{EB} & F_{AE} & A_x & A_y & B_y
\end{bmatrix}^{T}
$$

By convention, a **positive** internal force means **tension**, and a **negative** internal force means **compression**.

## Force Decomposition

Rather than hand-coding a sine and cosine for every member, the implementation decomposes each member's force along its **unit direction vector**, computed directly from node coordinates. This generalizes cleanly to any geometry, without special-casing each member's angle.

As an example, for member **AD**:

$$
\vec{AD} = (2,\ 1.5), \qquad |\vec{AD}| = 2.5
$$

$$
\hat{u}_{AD} = \frac{(2,\ 1.5)}{2.5} = (0.8,\ 0.6)
$$

Here $0.8 = \cos\theta$ and $0.6 = \sin\theta$ for this particular member. A force $F_{AD}$ acting along AD therefore contributes:

$$
F_x = 0.8\,F_{AD}, \qquad F_y = 0.6\,F_{AD}
$$

to the equilibrium equations at each of its endpoints. Every member in the truss is handled the same way, using its own unit vector.

## Load Model

The applied load comes from a mass placed at a node:

$$
P = m\,g
$$

where $P$ is the resulting load in newtons, $m$ is the mass in kilograms, and $g = 9.81\ \text{m/s}^2$.

For example, a 100 kg mass produces:

$$
P = 100 \times 9.81 = 981\ \text{N}
$$

The load is applied **vertically downward** at the chosen node. Mass and force/weight are kept as distinct quantities throughout the model.

## Numerical Method

The linear system is assembled automatically from the truss geometry and connectivity — nothing about the equilibrium matrix is hand-derived per case. The pipeline is:

```
Geometry
  ↓
Node connectivity
  ↓
Unit vectors
  ↓
Equilibrium matrix
  ↓
Load vector
  ↓
Linear system (A x = b)
  ↓
NumPy solver
  ↓
Internal forces + reactions
```

The linear system is solved with:

```python
np.linalg.solve(A, b)
```

This is a classic **joint-equilibrium method for a statically determinate truss**, not a finite element method (FEM). No stiffness matrix, shape functions, or discretization are involved.

## Equilibrium Validation

The project doesn't stop at producing a solution — it also checks that the solution actually satisfies equilibrium, by computing the residual:

$$
\mathbf{r} = \mathbf{A}\mathbf{x} + \mathbf{f}_{ext}
$$

A valid solution should give:

$$
\mathbf{r} \approx \mathbf{0}
$$

Very small nonzero values (on the order of floating-point precision) are expected and are simply a consequence of finite-precision arithmetic, not a modeling error.

## Example

**Load case:** a 100 kg mass placed at node **D**.

$$
m = 100\ \text{kg}, \qquad P = 981\ \text{N}
$$

**Support reactions**

$$
A_x = 0\ \text{N}, \qquad A_y = 490.5\ \text{N}, \qquad B_y = 490.5\ \text{N}
$$

**Internal member forces**

| Member | Force (N) | State       |
|--------|----------:|-------------|
| AC     |      0.00 | Zero-force  |
| AD     |   -817.50 | Compression |
| CD     |      0.00 | Zero-force  |
| DE     |     ≈ 0   | Zero-force  |
| DB     |   -817.50 | Compression |
| EB     |    654.00 | Tension     |
| AE     |    654.00 | Tension     |

Sign convention: **positive = tension, negative = compression**.

## Project Structure

**Current structure**

```
statics-lab/
├── src/
│   ├── statics.py
│   └── visualization.py
└── README.md
```

**Planned structure**

```
statics-lab/
├── src/
│   ├── statics.py
│   └── visualization.py
├── tests/
├── README.md
├── README.pt-BR.md
├── LICENSE
└── .gitignore
```

## statics.py

`src/statics.py` is the core of the project. It is responsible for:

- truss geometry (node coordinates);
- truss topology (member-to-node connectivity);
- computing unit direction vectors for each member;
- assembling the equilibrium matrix;
- assembling the load vector;
- solving the linear system;
- classifying each member's force as tension or compression;
- validating the equilibrium residuals.

A minimal usage example:

```python
solution = solve_truss("D", 100.0)
```

This solves the truss for a 100 kg load applied at node D and returns the internal forces and support reactions.

## visualization.py

`src/visualization.py` is responsible for the graphical side of the project. Currently, it:

- draws the truss geometry;
- draws the nodes;
- draws the supports;
- draws the applied load;
- displays the resulting forces.

It is also the foundation for future interactivity (see [Roadmap](#roadmap)), but full interactivity — such as clicking to place a load — does **not** exist yet.

## Installation

Clone the repository:

```bash
git clone <repository-url>
cd statics-lab
```

Install the dependencies:

```bash
python -m pip install numpy matplotlib
```

Optionally, use a virtual environment.

**Windows**

```bash
python -m venv .venv
.venv\Scripts\activate
python -m pip install numpy matplotlib
```

**Linux / macOS**

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install numpy matplotlib
```

## Running the Project

Run the solver from the terminal:

```bash
python src/statics.py
```

This assembles the equilibrium matrix for the current geometry, solves for the internal forces and reactions, and reports the results.

Open the visualization:

```bash
python src/visualization.py
```

This draws the truss, its supports, and the applied load.

## Development Philosophy

Statics Lab is built incrementally, following the same sequence an engineer would use to approach the problem by hand before writing any code:

1. model the physical problem;
2. derive the governing equations;
3. implement a solver;
4. validate the results;
5. visualize the structure and the solution;
6. add interaction;
7. expand the model's capabilities.

Complexity is added one layer at a time — the project does not use, or claim to use, techniques beyond what is currently implemented.

## Roadmap

**Phase 1 — Structural Solver**

- [x] Define fixed geometry
- [x] Define truss connectivity
- [x] Define support reactions
- [x] Build equilibrium matrix
- [x] Solve internal forces
- [x] Classify tension/compression
- [x] Check equilibrium residuals

**Phase 2 — Visualization**

- [x] Draw truss geometry
- [x] Draw nodes
- [x] Draw supports
- [x] Draw applied load
- [ ] Improve force visualization
- [ ] Add reaction arrows
- [ ] Add polished engineering diagram

**Phase 3 — Interaction**

- [ ] Select load node
- [ ] Select mass
- [ ] Recalculate automatically
- [ ] Display force values
- [ ] Highlight tension/compression
- [ ] Interactive load placement

**Phase 4 — Structural Interpretation**

- [ ] Define explicit criteria for load placement
- [ ] Identify highly loaded members
- [ ] Introduce safety-related educational metrics
- [ ] Explain limitations of the simplified model

**Phase 5 — Extensions**

- [ ] Multiple loads
- [ ] More complex truss geometries
- [ ] Shear/moment analysis where physically appropriate
- [ ] Stress calculations
- [ ] Material properties
- [ ] Buckling considerations
- [ ] Educational failure visualization

## Limitations

The current model is intentionally simplified. It:

- is two-dimensional (2D) only;
- is static, not dynamic;
- treats the truss as an idealized pin-jointed structure;
- applies loads only at joints;
- does **not** model deformation;
- does **not** model elasticity;
- does **not** model real stress within member cross-sections;
- does **not** model buckling;
- does **not** model real (non-pin) connections;
- does **not** account for geometric imperfections;
- is **not** a structural design tool;
- must **not** be used to make safety decisions about real structures.

A future "adequate load location" feature (see Roadmap, Phase 4) will be a classification within this educational model, based on explicitly defined criteria — it will **not** be a statement about whether a real structure is safe. A location is never called "safe" or "unsafe" simply because the computed internal forces are smaller or larger.

## Validation

Beyond computing residuals (see [Equilibrium Validation](#equilibrium-validation)), results are intended to be checked against:

- global equilibrium of the whole structure;
- equilibrium at each individual node;
- hand (manual) calculations;
- symmetric load cases;
- other known, independently verifiable cases.

The first validation case is the 100 kg load at node D described in [Example](#example): because D sits horizontally midway between supports A and B, the vertical reactions come out equal, $A_y = B_y = 490.5\ \text{N}$ — exactly as expected from symmetry.

## Educational Purpose

Statics Lab exists to study, in a hands-on way, the connection between:

- mechanical engineering;
- statics;
- linear algebra;
- Python;
- scientific computing;
- data visualization;
- mathematical modeling.

The goal isn't just to produce numbers — it's to work through, and understand, the full chain:

```
physical system
  → mathematical model
  → computational model
  → numerical solution
  → validation
  → visualization
```

## Technologies

- Python
- NumPy
- Matplotlib
- Git
- GitHub

## License

License terms have not been finalized in this repository yet. If a `LICENSE` file is added (for example, under the MIT License), it will govern the terms of use — check the `LICENSE` file in the repository for the current, authoritative terms.
