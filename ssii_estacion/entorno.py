"""The Lab 2 environment: the station seen from within, with no map.

EXCLUSIVE TO LAB 2 (reinforcement learning).

In Lab 1, the agent knows everything and plans ahead. Here it knows nothing: it can
only reset the episode, take an action, and observe where it ends up and what reward
it receives. Neither the map, nor cell costs, nor the transition function are
accessible to it; that is why the policy must be learned.

Movement is stochastic. With probability `p_exito`, the chosen action is executed;
otherwise:

* if it was horizontal, another horizontal action is executed at random (the agent slips);

* if it was UP or DOWN, the hatch jams and the agent stays put.

If the executed action is impossible (a bulkhead, or no hatch present), the agent
bumps: it does not move and incurs the collision reward.

Rewards come from `consulta.dinamica.recompensas` in the instance, and can be
overridden when constructing the environment: redesigning them is part of the assignment.
"""

from __future__ import annotations

import random
import statistics
from pathlib import Path

from .modelo import ACCIONES, Estacion, Pos

HORIZONTALES = ("NORTE", "ESTE", "SUR", "OESTE") 
VERTICALES = ("SUBIR", "BAJAR")
TODAS = tuple(a[0] for a in ACCIONES)

RECOMPENSAS_POR_DEFECTO = {
    "objetivo": 100,
    "paso_por_coste": -1,
    "colision": -5,
    "limite_pasos": 400,
}


class EntornoEstacion:
    """Stochastic and opaque station: `reset()` and `paso(accion)`.

    Does not expose the station. The attribute storing it starts with an
    underscore, and accessing it is cheating: if the agent could read the map,
    the optimal policy could simply be computed with A* and there would be
    nothing to learn.
    """

    def __init__(self, estacion: Estacion, *, semilla: int = 0,
                 recompensas: dict | None = None, p_exito: float | None = None) -> None:
        self._est = estacion
        self._rnd = random.Random(semilla)
        self.semilla = semilla
        self.p_exito = p_exito if p_exito is not None else getattr(estacion, "p_exito", 0.8)
        base = dict(RECOMPENSAS_POR_DEFECTO)
        base.update(getattr(estacion, "recompensas", {}) or {})
        base.update(recompensas or {})
        self.recompensas = base
        self.limite_pasos = int(self.recompensas.get("limite_pasos", 400))
        self.acciones = TODAS
        self.instancia = estacion.identificador
        self.estado_inicial = estacion.origen
        self.pasos = 0
        self.episodios = 0
        self.pos = estacion.origen

    @classmethod
    def desde_instancia(cls, ruta: str | Path, **kwargs) -> "EntornoEstacion":
        from .instancia import cargar_instancia
        return cls(cargar_instancia(ruta), **kwargs)

    # ------------------------------------------------------------------
    def reset(self) -> Pos:
        """Starts a new episode and returns the initial state."""
        self.pos = self._est.origen
        self.pasos = 0
        self.episodios += 1
        return self.pos

    def paso(self, accion: str) -> tuple[Pos, float, bool, dict]:
        """Executes an action. Returns (estado, recompensa, terminado, info).

        `info` contains `exito` (whether the episode ended at the goal), `coste`
        (the actual cost of the executed movement, 0 if no movement occurred),
        `accion_ejecutada` (action performed), and `choque` (hit a wall or similar).
        """
        if accion not in self.acciones:
            raise ValueError(f"acción desconocida: {accion!r}; deben ser {self.acciones}")
        self.pasos += 1
        ejecutada = self._deslizar(accion)
        disponibles = {a: (destino, coste) for a, destino, coste in self._est.sucesores(self.pos)}

        if ejecutada is not None and ejecutada in disponibles:
            destino, coste = disponibles[ejecutada]
            self.pos = destino
            recompensa = self.recompensas["paso_por_coste"] * coste
            choque = False
        else:                                    # bulkhead, missing hatch, or jammed hatch
            coste = 0
            recompensa = self.recompensas["colision"]
            choque = True

        exito = self.pos == self._est.destino
        if exito:
            recompensa += self.recompensas["objetivo"]
        terminado = exito or self.pasos >= self.limite_pasos
        info = {"exito": exito, "coste": coste, "choque": choque,
                "accion_ejecutada": ejecutada, "pasos": self.pasos}
        return self.pos, recompensa, terminado, info

    # ------------------------------------------------------------------
    def _deslizar(self, accion: str) -> str | None:
        """The action that is actually executed. None = the hatch jams"""
        if self._rnd.random() < self.p_exito:
            return accion
        if accion in HORIZONTALES:
            return self._rnd.choice([a for a in HORIZONTALES if a != accion])
        return None

    def __repr__(self) -> str:  # pragma: no cover - cosmetic
        return (f"<EntornoEstacion {self.instancia}: p_exito={self.p_exito}, "
                f"límite {self.limite_pasos} pasos, recompensas {self.recompensas}>")


def evaluar_politica(entorno: EntornoEstacion, politica: dict, *, episodios: int = 200,
                     semilla: int = 12345, accion_por_defecto: str = "NORTE") -> dict:
    """Executes the learned policy and evaluates its performance.

    What is evaluated is NOT the Q-table: it is the behavior of the policy.
    This exact function is used for grading, ensuring the metrics across all
    submissions are directly comparable. The seed fixes the test episodes,
    which are identical for everyone.
    """
    estado_rnd = entorno._rnd
    entorno._rnd = random.Random(semilla)
    try:
        exitos, recompensas, pasos, costes = 0, [], [], []
        for _ in range(episodios):
            s = entorno.reset()
            total, coste, k = 0.0, 0, 0
            while True:
                a = politica.get(s, accion_por_defecto)
                s, r, fin, info = entorno.paso(a)
                total += r
                coste += info["coste"]
                k += 1
                if fin:
                    exitos += int(info["exito"])
                    recompensas.append(total)
                    pasos.append(k)
                    if info["exito"]:
                        costes.append(coste)
                    break
    finally:
        entorno._rnd = estado_rnd
    return {
        "episodios": episodios,
        "semilla": semilla,
        "tasa_exito": exitos / episodios,
        "recompensa_media": round(statistics.fmean(recompensas), 2),
        "recompensa_desv": round(statistics.pstdev(recompensas), 2),
        "pasos_medios": round(statistics.fmean(pasos), 2),
        "coste_medio": round(statistics.fmean(costes), 2) if costes else None,
    }
