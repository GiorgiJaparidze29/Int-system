"""Lab 3: visiting N points across the station in the best possible order.

EXCLUSIVE TO LAB 3 (metaheuristics).

The distance matrix is built by running the Lab 1 algorithm between every pair
of points: the goal here is no longer to find a path, but rather the ORDER in which
to visit them. The solution space consists of permutations, and with 15 points there
are 1.3 trillion possibilities, so it must be explored using metaheuristics.

What this package provides is the bookkeeping, for the same reason it provides the
frontier and counters in Lab 1: to ensure two submissions are directly comparable.
The `Evaluador` tracks every objective function evaluation and logs the convergence
curve, so that claims like "my genetic algorithm outperforms my hill climbing"
can only be made under the exact same evaluation budget.
"""

from __future__ import annotations

import json
import random
from pathlib import Path

from .modelo import Pos


def cargar_matriz(ruta: str | Path) -> tuple[list[Pos], list[list[int]]]:
    """Reads a distance matrix from the catalog. Returns (points, matrix).

    `points[0]` is the depot (base); `matrix[i][j]` is the optimal cost of going from i to j.
    """
    datos = json.loads(Path(ruta).read_text(encoding="utf-8"))
    puntos = [Pos(*p) for p in datos["puntos"]]
    return puntos, datos["matriz"]


def coste_recorrido(matriz: list[list[int]], orden: list[int]) -> int:
    """Cost of the closed path: departs from the base (0), visits order, and returns."""
    ruta = [0] + list(orden) + [0]
    return sum(matriz[a][b] for a, b in zip(ruta, ruta[1:]))


def orden_valido(orden, n_puntos: int) -> bool:
    """Is order a permutation of 1..n_points? (the base is not included)"""
    return sorted(orden) == list(range(1, n_puntos + 1))


def orden_aleatorio(n_puntos: int, rnd: random.Random) -> list[int]:
    orden = list(range(1, n_puntos + 1))
    rnd.shuffle(orden)
    return orden


def invertir(orden: list[int], i: int, j: int) -> list[int]:
    """The 2-opt move: reverses the segment [i, j] (both inclusive)

    This is valid because the matrix is symmetric: reversing a segment does not
    change its internal cost, meaning only the two new edge connections must be paid for.
    """
    if i > j:
        i, j = j, i
    return orden[:i] + orden[i:j + 1][::-1] + orden[j + 1:]


class PresupuestoAgotado(Exception):
    """All allowed evaluations have been exhausted."""


class Evaluador:
    """Objective function with an evaluation counter and convergence curve.

    All metaheuristics in this lab are benchmarked against the EXACT SAME
    budget: it is the only way for the comparison to be meaningful.

        ev = Evaluador(matriz, presupuesto=20_000)
        c = ev.coste(orden)          # registers one evaluation
        while not ev.agotado: ...    # you control the loop
    """

    def __init__(self, matriz: list[list[int]], presupuesto: int, *,
                 ventana: int = 100, estricto: bool = False) -> None:
        self.matriz = matriz
        self.n_puntos = len(matriz) - 1
        self.presupuesto = presupuesto
        self.ventana = ventana
        self.estricto = estricto
        self.evaluaciones = 0
        self.mejor_coste: int | None = None
        self.mejor_orden: list[int] | None = None
        self.curva: list[int] = []

    @property
    def agotado(self) -> bool:
        return self.evaluaciones >= self.presupuesto

    def coste(self, orden: list[int]) -> int:
        if self.estricto and self.agotado:
            raise PresupuestoAgotado(
                f"{self.evaluaciones} evaluaciones: se acabó el presupuesto")
        c = coste_recorrido(self.matriz, orden)
        self.evaluaciones += 1
        if self.mejor_coste is None or c < self.mejor_coste:
            self.mejor_coste, self.mejor_orden = c, list(orden)
        if self.evaluaciones % self.ventana == 0:
            self.curva.append(self.mejor_coste)
        return c

    def reinicia_contador(self) -> None:
        """New run/repetition: keeps the matrix, resets tracking"""
        self.evaluaciones = 0
        self.mejor_coste = self.mejor_orden = None
        self.curva = []

    def resumen(self) -> dict:
        return {"evaluaciones": self.evaluaciones, "presupuesto": self.presupuesto,
                "mejor_coste": self.mejor_coste, "mejor_orden": self.mejor_orden,
                "curva": self.curva}

    def __repr__(self) -> str:  # pragma: no cover - cosmetic
        return (f"<Evaluador {self.n_puntos} puntos: {self.evaluaciones}/"
                f"{self.presupuesto} evaluaciones, mejor {self.mejor_coste}>")
