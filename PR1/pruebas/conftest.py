"""Configuration for Lab 1 public tests.

By default, the notebook Lab1_26-27_ES.ipynb in the parent directory is tested.
To test a different file:

    SII_ENTREGA=path/to/notebook.ipynb python3 -m pytest PR1/pruebas -q
"""

import os
import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[2]   # file 26-27
sys.path.insert(0, str(RAIZ))

from ssii_estacion.entrega import cargar_entrega          # noqa: E402
from ayuda import Pos, estacion as _estacion              # noqa: E402

ENTREGA_POR_DEFECTO = RAIZ / "PR1" / "Lab1_26-27_ES.ipynb"


@pytest.fixture(scope="session")
def entrega():
    return cargar_entrega(os.environ.get("SSII_ENTREGA") or ENTREGA_POR_DEFECTO)


@pytest.fixture(scope="session")
def estrategias(entrega):
    """The four strategies, ready to be called as (est, origen, destino)."""
    h2 = lambda est, destino: (lambda p: est.h_manhattan_conexiones(p, destino))
    h1 = lambda est, destino: (lambda p: est.h_manhattan(p, destino))
    return {
        "anchura": lambda est, o, d: entrega["anchura"](est, o, d),
        "coste_uniforme": lambda est, o, d: entrega["coste_uniforme"](est, o, d),
        "voraz": lambda est, o, d: entrega["voraz"](est, o, d, h2(est, d)),
        "a_estrella": lambda est, o, d: entrega["a_estrella"](est, o, d, h1(est, d)),
    }



@pytest.fixture
def pasillo():
    """3x3 grid of cost-1 cells. From (0,1,1) to (0,3,3): cost 4 in 4 steps."""
    n = [[0, 0, 0, 0, 0],
         [0, 1, 1, 1, 0],
         [0, 1, 1, 1, 0],
         [0, 1, 1, 1, 0],
         [0, 0, 0, 0, 0]]
    return _estacion([n], identificador="pasillo")


@pytest.fixture
def desvio():
    """Expensive shortcut (3 steps, cost 9) vs. cheap detour (7 steps, cost 7)."""
    n = [[0, 0, 0, 0, 0, 0],
         [0, 1, 3, 3, 1, 0],
         [0, 1, 0, 0, 1, 0],
         [0, 1, 1, 1, 1, 0],
         [0, 0, 0, 0, 0, 0]]
    return _estacion([n], identificador="desvio")


@pytest.fixture
def dos_niveles():
    """Two floors with a single hatch, located at (2,2) with cost 2."""
    n = [[0, 0, 0, 0, 0],
         [0, 1, 1, 1, 0],
         [0, 1, 1, 1, 0],
         [0, 1, 1, 1, 0],
         [0, 0, 0, 0, 0]]
    return _estacion([n, n], [{"nivel": 0, "fila": 2, "col": 2, "coste": 2}],
                     identificador="dos-niveles")


@pytest.fixture
def incomunicada():
    """Two doorless compartments: the goal is unreachable."""
    n = [[0, 0, 0, 0, 0],
         [0, 1, 0, 1, 0],
         [0, 1, 0, 1, 0],
         [0, 1, 0, 1, 0],
         [0, 0, 0, 0, 0]]
    return _estacion([n], identificador="incomunicada")
