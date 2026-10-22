"""
ssii_estacion — shared infrastructure for the Intelligent Systems lab assignments.

Academic year 2026-27. ESII Albacete, UCLM.

This package is provided by the teaching staff. Students must NOT modify it:
implement algorithms, not plumbing. Everything here (instance loading,
successors in canonical order, frontier with deterministic tie-breaking,
counters, validation, and solution dumping) is designed so that two
correct implementations yield the exact same numbers.

Scope of each module:

    modelo.py       shared      the station, positions, and actions
    instancia.py    shared      instance loading and validation
    solucion.py     shared      solution construction and validation
    vis.py          shared      floor plan drawing (primarily for Lab 1)
    entrega.py      shared      submission loading for test suites
    busqueda.py     Lab 1 only  frontier, closed set, nodes, and counters
    entorno.py      Lab 2 only  stochastic and opaque environment (reset / step)
    recorrido.py    Lab 3 only  matrix, path cost, and Evaluator
"""

from .modelo import Estacion, Pos, ACCIONES
from .instancia import cargar_instancia, InstanciaInvalida
from .busqueda import Frontera, Cerrados, Contadores, Nodo, reconstruir_camino
from .solucion import (
    solucion_pr1,
    solucion_pr2,
    solucion_pr3,
    guardar_solucion,
    validar_solucion_pr1,
    validar_solucion_pr2,
    validar_solucion_pr3,
)

__version__ = "1.0.0"
ESQUEMA_VERSION = "ssii-estacion/1"

__all__ = [
    "Estacion",
    "Pos",
    "ACCIONES",
    "cargar_instancia",
    "InstanciaInvalida",
    "Frontera",
    "Cerrados",
    "Contadores",
    "Nodo",
    "reconstruir_camino",
    "solucion_pr1",
    "solucion_pr2",
    "solucion_pr3",
    "guardar_solucion",
    "validar_solucion_pr1",
    "validar_solucion_pr2",
    "validar_solucion_pr3",
    "ESQUEMA_VERSION",
    "__version__",
]
