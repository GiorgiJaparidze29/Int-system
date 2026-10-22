"""Environment model: the multilevel space station.

COMMON to all three labs: the station, positions, and actions are the
same across Lab 1, Lab 2, and Lab 3."""

from __future__ import annotations

from typing import Iterator, NamedTuple


class Pos(NamedTuple):
    """Position in the station: [level, row, column]."""

    nivel: int
    fila: int
    col: int

    def __repr__(self) -> str:  # pragma: no cover - cosmetic
        return f"({self.nivel},{self.fila},{self.col})"

    def como_lista(self) -> list[int]:
        return [self.nivel, self.fila, self.col]


# ---------------------------------------------------------------------------
# CANONICAL SUCCESSOR GENERATION ORDER
# This order is NORMATIVE. Together with the frontier's FIFO tie-breaking,
# it ensures that the counter values of two correct implementations match
# exactly. Do not modify it.
# ---------------------------------------------------------------------------
ACCIONES: tuple[tuple[str, int, int, int], ...] = (
    ("NORTE", 0, -1, 0),
    ("ESTE", 0, 0, +1),
    ("SUR", 0, +1, 0),
    ("OESTE", 0, 0, -1),
    ("SUBIR", +1, 0, 0),
    ("BAJAR", -1, 0, 0),
)

MURO = 0


class Estacion:
    """A multilevel space station.

    Each level is a grid of `rows` x `columns`. The value of a cell represents
    its *occupancy cost*: 0 denotes non-traversable (bulkhead, restricted area)
    and k >= 1 represents the cost of occupying it (1 clear corridor, 2 low-gravity
    zone, 3 service duct, ...).

    Horizontal movement: 4-neighborhood within the same level.
    Vertical movement: strictly via explicit connections, linking the SAME
    (row, column) between two CONSECUTIVE levels. Physically, these represent
    hatches or elevators, which is why they share the same vertical alignment
    across both floors.

    Cost of a horizontal transition between cells u and v:

        c(u, v) = max(cell_cost(u), cell_cost(v))

    It is deliberately symmetric and integer-valued: symmetry ensures that the
    distance matrix in Lab 3 remains symmetric and that 2-opt remains valid.
    The physical intuition is "the segment costs as much as the worse of its two cells."

    Cost of a vertical transition: the cost specified by the connection, identical
    in both directions.
    """

    def __init__(
        self,
        rejillas: list[list[list[int]]],
        conexiones: list[dict],
        *,
        identificador: str = "sin-nombre",
        metadatos: dict | None = None,
    ) -> None:
        self.rejillas = rejillas
        self.niveles = len(rejillas)
        self.filas = len(rejillas[0])
        self.columnas = len(rejillas[0][0])
        self.identificador = identificador
        self.metadatos = metadatos or {}

        # Vertical connections indexed by (level, row, col) -> {destination: cost}
        self._conexiones: dict[Pos, dict[Pos, int]] = {}
        self.conexiones = conexiones
        for con in conexiones:
            n, f, c = con["nivel"], con["fila"], con["col"]
            coste = con["coste"]
            abajo, arriba = Pos(n, f, c), Pos(n + 1, f, c)
            self._conexiones.setdefault(abajo, {})[arriba] = coste
            self._conexiones.setdefault(arriba, {})[abajo] = coste

        self.coste_min_conexion = (
            min(con["coste"] for con in conexiones) if conexiones else 1
        )

    # ------------------------------------------------------------------
    # Basic queries
    # ------------------------------------------------------------------
    def dentro(self, p: Pos) -> bool:
        return (
            0 <= p.nivel < self.niveles
            and 0 <= p.fila < self.filas
            and 0 <= p.col < self.columnas
        )

    def coste_celda(self, p: Pos) -> int:
        """Occupancy cost of the cell. 0 = non-traversable."""
        if not self.dentro(p):
            return MURO
        return self.rejillas[p.nivel][p.fila][p.col]

    def es_transitable(self, p: Pos) -> bool:
        return self.coste_celda(p) > MURO

    def hay_conexion(self, a: Pos, b: Pos) -> bool:
        return b in self._conexiones.get(a, {})

    # ------------------------------------------------------------------
    # Successors — ALWAYS in canonical order
    # ------------------------------------------------------------------
    def sucesores(self, p: Pos) -> list[tuple[str, Pos, int]]:
        """Returns [(action, destination, cost)] in the CANONICAL ORDER of ACTIONS.

            This is the only function students should use to generate successors.
            Using a different order alters the counters and causes automated grading
            to fail, even if the discovered path is equally optimal.
        """
        salida: list[tuple[str, Pos, int]] = []
        for nombre, dn, df, dc in ACCIONES:
            destino = Pos(p.nivel + dn, p.fila + df, p.col + dc)
            if not self.dentro(destino) or not self.es_transitable(destino):
                continue
            if dn == 0:
                coste = max(self.coste_celda(p), self.coste_celda(destino))
            else:
                coste = self._conexiones.get(p, {}).get(destino)
                if coste is None:
                    continue  # no hatch here
            salida.append((nombre, destino, coste))
        return salida

    def coste_transicion(self, a: Pos, b: Pos) -> int | None:
        """Cost of transitioning from a to b if adjacent; None if they are not."""
        for _, destino, coste in self.sucesores(a):
            if destino == b:
                return coste
        return None

    # ------------------------------------------------------------------
    # Baseline heuristics
    # ------------------------------------------------------------------
    def h_manhattan(self, p: Pos, objetivo: Pos) -> int:
        """h1: 3D Manhattan distance, counting each level change as 1.

        Admissible: every action costs >= 1 and reduces the sum |dr|+|dc|+|dl|
        by at most 1. Consistent for the same reason.
        """
        return (
            abs(p.fila - objetivo.fila)
            + abs(p.col - objetivo.col)
            + abs(p.nivel - objetivo.nivel)
        )

    def h_manhattan_conexiones(self, p: Pos, objetivo: Pos) -> int:
        """h2: like h1, but each level change costs at least
        `coste_min_conexion`.

        Dominates h1 whenever the cheapest connection costs more than 1,
        which holds for all instances in the benchmark suite. Remains admissible:
        changing levels requires traversing a connection, and none costs less
        than the minimum.
        """
        return (
            abs(p.fila - objetivo.fila)
            + abs(p.col - objetivo.col)
            + abs(p.nivel - objetivo.nivel) * self.coste_min_conexion
        )

    # ------------------------------------------------------------------
    # Utilities
    # ------------------------------------------------------------------
    def celdas_transitables(self) -> Iterator[Pos]:
        for n in range(self.niveles):
            for f in range(self.filas):
                for c in range(self.columnas):
                    p = Pos(n, f, c)
                    if self.es_transitable(p):
                        yield p

    def n_transitables(self) -> int:
        return sum(1 for _ in self.celdas_transitables())

    def __repr__(self) -> str:  # pragma: no cover - cosmetic
        return (
            f"<Estacion {self.identificador}: {self.niveles} niveles de "
            f"{self.filas}x{self.columnas}, {self.n_transitables()} celdas "
            f"transitables, {len(self.conexiones)} conexiones>"
        )
