"""Block 1 — contract: what the functions return.

These tests do not evaluate algorithm quality; they only check that the shape 
of the response matches what the autograder expects.
"""

import pytest

from ayuda import Pos, camino_valido, invariante

CLAVES = {"camino", "acciones", "coste", "encontrada", "contadores"}


@pytest.mark.parametrize("nombre", ["anchura", "coste_uniforme", "voraz", "a_estrella"])
def test_devuelve_las_claves_esperadas(estrategias, pasillo, nombre):
    r = estrategias[nombre](pasillo, Pos(0, 1, 1), Pos(0, 3, 3))
    assert isinstance(r, dict), "cada estrategia devuelve un diccionario"
    assert CLAVES <= set(r), f"faltan claves: {sorted(CLAVES - set(r))}"


@pytest.mark.parametrize("nombre", ["anchura", "coste_uniforme", "voraz", "a_estrella"])
def test_camino_y_acciones_encajan(estrategias, pasillo, nombre):
    r = estrategias[nombre](pasillo, Pos(0, 1, 1), Pos(0, 3, 3))
    assert r["encontrada"] is True
    assert len(r["acciones"]) == len(r["camino"]) - 1, (
        "hay una acción por cada paso, es decir, una menos que posiciones")
    camino_valido(pasillo, r)


@pytest.mark.parametrize("nombre", ["anchura", "coste_uniforme", "voraz", "a_estrella"])
def test_contadores_coherentes(estrategias, pasillo, nombre):
    c = invariante(estrategias[nombre](pasillo, Pos(0, 1, 1), Pos(0, 3, 3)))
    assert c["nodos_generados"] >= 1, "el nodo raíz también cuenta como generado"
    assert c["max_frontera"] >= 1 and c["max_alcanzados"] >= 1


def test_el_bucle_esta_parametrizado_por_f(entrega, pasillo):
    """primero_el_mejor tiene que aceptar la f que se le pase."""
    r = entrega["primero_el_mejor"](pasillo, Pos(0, 1, 1), Pos(0, 3, 3), lambda n, h: n.coste)
    assert r["coste"] == 4, "con f(n) = g(n) sale el camino más barato: 4"
    camino_valido(pasillo, r)
