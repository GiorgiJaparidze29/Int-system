"""Public test utilities: station construction and assertions."""

from ssii_estacion.modelo import Estacion, Pos


def estacion(rejillas, conexiones=(), identificador="prueba"):
    return Estacion([[list(f) for f in n] for n in rejillas], list(conexiones),
                    identificador=identificador)


def camino_valido(est, resultado):
    """Verifies that the path actually exists on the station."""
    camino = [Pos(*p) for p in resultado["camino"]]
    assert camino, "el camino está vacío"
    coste = 0
    for a, b in zip(camino, camino[1:]):
        c = est.coste_transicion(a, b)
        assert c is not None, f"{a} y {b} no son adyacentes"
        coste += c
    assert all(est.es_transitable(p) for p in camino), "el camino pisa celdas no transitables"
    assert coste == resultado["coste"], (
        f"el coste declarado ({resultado['coste']}) no coincide con el real ({coste})")
    return coste


def invariante(resultado):
    c = resultado["contadores"].como_dict()
    assert c["nodos_expandidos"] <= c["nodos_explorados"] <= c["nodos_generados"], c
    return c
