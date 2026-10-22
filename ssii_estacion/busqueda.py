"""Frontier, reached set, and instrumented counters.

EXCLUSIVE TO LAB 1 (state-space search). Lab 2 uses `entorno.py` and Lab 3 uses `recorrido.py`.

The reason this is provided by the teaching staff rather than written by students is automated grading: 
the five counters are extremely sensitive to successor generation order and tie-breaking behavior. With 
these classes, two correct implementations of the same algorithm produce the exact same numbers.
"""

from __future__ import annotations

import heapq
from dataclasses import dataclass, field
from typing import Any

from .modelo import Pos


@dataclass
class Nodo:
    """A node in the search tree.

    Remember the distinction from Unit 2: STATES do not have parents,
    depth, or path cost. NODES do. A single state can be represented
    by multiple distinct nodes.
    """

    estado: Pos
    padre: "Nodo | None" = None
    accion: str | None = None
    coste: int = 0          # g(n): path cost from the origin node
    profundidad: int = 0

    def camino(self) -> list["Nodo"]:
        """Nodes from the root until this node, in order."""
        ruta, actual = [], self
        while actual is not None:
            ruta.append(actual)
            actual = actual.padre
        ruta.reverse()
        return ruta


def reconstruir_camino(nodo: Nodo) -> tuple[list[Pos], list[str]]:
    """Returns (positions, actions) along the path leading to 'node'."""
    nodos = nodo.camino()
    posiciones = [n.estado for n in nodos]
    acciones = [n.accion for n in nodos[1:]]
    return posiciones, acciones


@dataclass
class Contadores:
    """The five counters that must be reported in the solution.

    NORMATIVE definitions (the exact ones used in lectures):

    - generados: generated nodes, including the root node.
    - explorados: nodes REMOVED from the frontier to be examined.
    - expandidos: of the explored nodes, those for which successors
    were generated. An extracted node whose state was already in reached
    is discarded without expanding, and a goal node ends the search
    without expanding. Therefore, always: expandidos <= explorados <= generados.
    - max_frontera: maximum size reached by the open list (frontera).
    - max_alcanzados: maximum size reached by the closed set (alcanzados).
    """

    generados: int = 0
    explorados: int = 0
    expandidos: int = 0
    max_frontera: int = 0
    max_alcanzados: int = 0

    def como_dict(self) -> dict[str, int]:
        return {
            "nodos_generados": self.generados,
            "nodos_explorados": self.explorados,
            "nodos_expandidos": self.expandidos,
            "max_frontera": self.max_frontera,
            "max_alcanzados": self.max_alcanzados,
        }


@dataclass(order=True)
class _Entrada:
    prioridad: float
    orden: int
    nodo: Any = field(compare=False)


class Frontera:
    """Priority queue with FIFO tie-breaking, including counters.

    Tie-breaking is NORMATIVE: between two nodes with the same priority f,
    the one inserted first comes out first. This is implemented using an insertion
    counter as the second component of the heap tuple. Without this rule, two
    equally correct implementations will yield different counter values.

    For Breadth-First Search, use f = depth; for Uniform-Cost Search,
    f = g; for Greedy Best-First, f = h; for A*, f = g + h. In other words:
    a single algorithm, parameterized by f. This is the BEST-FIRST-SEARCH
    framework from the 4th edition of Russell & Norvig.
    """

    def __init__(self, contadores: Contadores | None = None) -> None:
        self._monticulo: list[_Entrada] = []
        self._orden = 0
        self.contadores = contadores or Contadores()

    def insertar(self, nodo: Nodo, prioridad: float) -> None:
        heapq.heappush(self._monticulo, _Entrada(prioridad, self._orden, nodo))
        self._orden += 1
        self.contadores.max_frontera = max(
            self.contadores.max_frontera, len(self._monticulo)
        )

    def extraer(self) -> Nodo:
        """Pops the node with the lowest f value. Counts as 'explorado' (explored)"""
        entrada = heapq.heappop(self._monticulo)
        self.contadores.explorados += 1
        return entrada.nodo

    def vacia(self) -> bool:
        return not self._monticulo

    def __len__(self) -> int:
        return len(self._monticulo)


class Cerrados:
    """Set of reached states, tracking the best known cost for each.

    Recommended usage (the one from Unit 3 following the 4th edition):
    before inserting a successor, call `mejora(estado, g)`. It returns True
    if the state has never been reached before or if it was reached via a
    cheaper path, updating the record in that case. This prevents the classic
    bug of discarding a repeated state that arrived via a better path, which
    breaks the optimality of Uniform-Cost Search and A*.
    """

    def __init__(self, contadores: Contadores | None = None) -> None:
        self._mejor: dict[Pos, int] = {}
        self.contadores = contadores or Contadores()

    def mejora(self, estado: Pos, coste: int) -> bool:
        previo = self._mejor.get(estado)
        if previo is None or coste < previo:
            self._mejor[estado] = coste
            self.contadores.max_alcanzados = max(
                self.contadores.max_alcanzados, len(self._mejor)
            )
            return True
        return False

    def contiene(self, estado: Pos) -> bool:
        return estado in self._mejor

    def coste(self, estado: Pos) -> int | None:
        return self._mejor.get(estado)

    def __len__(self) -> int:
        return len(self._mejor)
