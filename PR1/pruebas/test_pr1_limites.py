"""Block 2 — edge cases.

These are the ones easily missed if only tested against the catalog: 
start equals goal, unreachable goal, and a mandatory vertical transition.
"""

import pytest

from ayuda import Pos, camino_valido, invariante

TODAS = ["anchura", "coste_uniforme", "voraz", "a_estrella"]


@pytest.mark.parametrize("nombre", TODAS)
def test_origen_igual_a_destino(estrategias, pasillo, nombre):
    r = estrategias[nombre](pasillo, Pos(0, 2, 2), Pos(0, 2, 2))
    assert r["encontrada"] is True
    assert r["coste"] == 0
    assert len(r["camino"]) == 1 and r["acciones"] == []
    c = invariante(r)
    assert c["nodos_expandidos"] == 0, "si el origen ya es el objetivo, no se expande nada"


@pytest.mark.parametrize("nombre", TODAS)
def test_destino_inalcanzable(estrategias, incomunicada, nombre):
    """Must terminate and indicate that no path exists, rather than raising an exception."""
    r = estrategias[nombre](incomunicada, Pos(0, 1, 1), Pos(0, 1, 3))
    assert r["encontrada"] is False


@pytest.mark.parametrize("nombre", ["coste_uniforme", "a_estrella"])
def test_escotilla_obligatoria(estrategias, dos_niveles, nombre):
    r = estrategias[nombre](dos_niveles, Pos(0, 1, 1), Pos(1, 3, 3))
    assert r["encontrada"] is True
    assert "SUBIR" in r["acciones"], "la única forma de cambiar de nivel es la escotilla"
    assert r["coste"] == 6, "2 + escotilla (2) + 2"
    camino_valido(dos_niveles, r)


def test_anchura_optimiza_pasos_no_coste(estrategias, desvio):
    """The shortcut takes fewer steps but costs more: this is the distinction from Unit 2."""
    a = estrategias["anchura"](desvio, Pos(0, 1, 1), Pos(0, 1, 4))
    u = estrategias["coste_uniforme"](desvio, Pos(0, 1, 1), Pos(0, 1, 4))
    camino_valido(desvio, a)
    camino_valido(desvio, u)
    assert len(a["camino"]) - 1 == 3 and a["coste"] == 9
    assert u["coste"] == 7, "coste uniforme prefiere el rodeo barato"


def test_a_estrella_es_optima(estrategias, desvio):
    r = estrategias["a_estrella"](desvio, Pos(0, 1, 1), Pos(0, 1, 4))
    assert r["coste"] == 7, "con una heurística admisible, A* da el coste óptimo"
