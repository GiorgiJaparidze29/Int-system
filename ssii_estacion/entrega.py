"""Loads functions from a submission so they can be tested.

COMMON to all three labs: FUNCIONES_PR1, FUNCIONES_PR2, and FUNCIONES_PR3
specify what is expected in each notebook. This is an auto-grading tool and is
not used by students.

A submission is the completed .ipynb notebook (or an equivalent .py file).
From a notebook, only definition cells are executed—those containing
functions or classes—never those that run exploratory code, plot figures, or
export files: this ensures running tests on a submission writes nothing to disk
and avoids running the time-consuming experimental study.

Common package imports are injected before executing anything, so it does not
matter in which cell each pair of students placed them.
"""

from __future__ import annotations

import ast
import json
import sys
from pathlib import Path

from . import busqueda, entorno as _entorno, modelo, recorrido as _recorrido, solucion

FUNCIONES_PR1 = ("primero_el_mejor", "anchura", "coste_uniforme", "voraz", "a_estrella")
FUNCIONES_PR2 = ("q_learning", "politica_de")
FUNCIONES_PR3 = ("ascension_colinas", "colinas_con_reinicios", "cruce_ox", "algoritmo_genetico")


class EntregaInvalida(Exception):
    """The submission cannot be loaded or does not define what it should."""


def _entorno_base() -> dict:
    return {
        "__name__": "entrega",
        "Pos": modelo.Pos,
        "Estacion": modelo.Estacion,
        "ACCIONES": modelo.ACCIONES,
        "Frontera": busqueda.Frontera,
        "Cerrados": busqueda.Cerrados,
        "Contadores": busqueda.Contadores,
        "Nodo": busqueda.Nodo,
        "reconstruir_camino": busqueda.reconstruir_camino,
        "solucion_pr1": solucion.solucion_pr1,
        "guardar_solucion": solucion.guardar_solucion,
        "validar_solucion_pr1": solucion.validar_solucion_pr1,
        "solucion_pr2": solucion.solucion_pr2,
        "EntornoEstacion": _entorno.EntornoEstacion,
        "evaluar_politica": _entorno.evaluar_politica,
        "random": __import__("random"),
        "solucion_pr3": solucion.solucion_pr3,
        "Evaluador": _recorrido.Evaluador,
        "cargar_matriz": _recorrido.cargar_matriz,
        "coste_recorrido": _recorrido.coste_recorrido,
        "invertir": _recorrido.invertir,
        "orden_aleatorio": _recorrido.orden_aleatorio,
        "orden_valido": _recorrido.orden_valido,
    }


def es_celda_de_definiciones(codigo: str) -> bool:
    """Does the cell only contain definitions? (functions, classes, imports, constants)"""
    try:
        arbol = ast.parse(codigo)
    except SyntaxError:
        return False
    permitidos = (ast.Import, ast.ImportFrom, ast.FunctionDef, ast.AsyncFunctionDef,
                  ast.ClassDef, ast.Assign, ast.AnnAssign)

    def es_cadena_suelta(n):   # docstring at the beginning of a cell
        return (isinstance(n, ast.Expr) and isinstance(n.value, ast.Constant)
                and isinstance(n.value.value, str))

    hay_funcion = any(isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))
                      for n in arbol.body)
    return hay_funcion and all(isinstance(n, permitidos) or es_cadena_suelta(n)
                               for n in arbol.body)


def codigo_de_cuaderno(ruta: str | Path) -> str:
    datos = json.loads(Path(ruta).read_text(encoding="utf-8"))
    trozos = []
    for celda in datos.get("cells", []):
        if celda.get("cell_type") != "code":
            continue
        codigo = "".join(celda.get("source", []))
        codigo = "\n".join(l for l in codigo.splitlines() if not l.lstrip().startswith(("%", "!")))
        if es_celda_de_definiciones(codigo):
            trozos.append(codigo)
    return "\n\n".join(trozos)


def cargar_entrega(ruta: str | Path, *, funciones: tuple[str, ...] = FUNCIONES_PR1) -> dict:
    """Returns the executed namespace of the submission.
        Raises EntregaInvalida if the file does not exist, if the code fails to
        compile, or if any of the required functions for the lab are missing.
    """
    ruta = Path(ruta)
    if not ruta.exists():
        raise EntregaInvalida(f"no existe la entrega {ruta}")
    if ruta.suffix == ".ipynb":
        codigo = codigo_de_cuaderno(ruta)
    else:
        codigo = ruta.read_text(encoding="utf-8")
    if not codigo.strip():
        raise EntregaInvalida(f"{ruta.name}: no hay ninguna celda con definiciones")

    raiz = ruta.resolve().parent.parent  # The lab folder, containing ssii_estacion
    if str(raiz) not in sys.path:
        sys.path.insert(0, str(raiz))

    espacio = _entorno_base()
    try:
        exec(compile(codigo, f"<{ruta.name}>", "exec"), espacio)
    except Exception as e:  # noqa: BLE001 - submission errors are reported as-is
        raise EntregaInvalida(f"{ruta.name}: error al ejecutar las definiciones: {e!r}") from e

    faltan = [f for f in funciones if not callable(espacio.get(f))]
    if faltan:
        raise EntregaInvalida(f"{ruta.name}: faltan funciones: {', '.join(faltan)}")
    return espacio
