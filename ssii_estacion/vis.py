"""Station visualization, floor by floor.

COMMON, though primarily used in Lab 1: plots the floors with the path
overlaid. It is also used to pinpoint visit points in Lab 3.

With three or more levels, a 3D rendering becomes unreadable and useless for
debugging. What actually works is a row of 2D floor plans, with hatches marked
and the path overlaid. This is what is provided to students.
"""

from __future__ import annotations

# Backend is not hardcoded: in Jupyter the inline backend is used and the figure is displayed;
# outside a graphical environment, matplotlib automatically falls back to Agg.
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from matplotlib.lines import Line2D

from .modelo import Estacion, Pos

# 0 bulkhead · 1 corridor · 2 low gravity · 3 service duct
COLORES = ListedColormap(["#2F3640", "#F5F6FA", "#FFD9A0", "#F0A07C"])
NOMBRES = ["mamparo", "coste 1", "coste 2", "coste 3"]


def dibujar(
    estacion: Estacion,
    *,
    camino: list[Pos] | None = None,
    puntos: dict[str, Pos] | None = None,
    titulo: str | None = None,
    ruta_salida: str | None = None,
    ancho_planta: float = 3.6,
):
    """Draws all floors in a single row. Returns the matplotlib figure."""
    n = estacion.niveles
    fig, ejes = plt.subplots(
        1, n, figsize=(ancho_planta * n, ancho_planta * estacion.filas / estacion.columnas + 1.2)
    )
    if n == 1:
        ejes = [ejes]

    escotillas: dict[int, list[tuple[int, int]]] = {}
    for con in estacion.conexiones:
        escotillas.setdefault(con["nivel"], []).append((con["fila"], con["col"]))
        escotillas.setdefault(con["nivel"] + 1, []).append((con["fila"], con["col"]))

    for nivel, ax in enumerate(ejes):
        ax.imshow(
            estacion.rejillas[nivel], cmap=COLORES, vmin=0, vmax=3, interpolation="nearest"
        )
        ax.set_title(f"Nivel {nivel}", fontsize=11)
        ax.set_xticks([])
        ax.set_yticks([])

        for f, c in escotillas.get(nivel, []):
            ax.plot(c, f, marker="s", markersize=6, markerfacecolor="none",
                    markeredgecolor="#0B7285", markeredgewidth=1.8)

        if camino:
            tramo = [p for p in camino if p.nivel == nivel]
            # Drawn in contiguous segments to avoid connecting disconnected parts
            seg: list[Pos] = []
            for p in camino:
                if p.nivel == nivel:
                    seg.append(p)
                else:
                    if len(seg) > 1:
                        ax.plot([q.col for q in seg], [q.fila for q in seg],
                                color="#C2255C", linewidth=2.0, solid_capstyle="round")
                    seg = []
            if len(seg) > 1:
                ax.plot([q.col for q in seg], [q.fila for q in seg],
                        color="#C2255C", linewidth=2.0, solid_capstyle="round")
            if tramo:
                ax.plot([q.col for q in tramo], [q.fila for q in tramo], ".",
                        color="#C2255C", markersize=3)

        if puntos:
            for etiqueta, p in puntos.items():
                if p.nivel == nivel:
                    ax.plot(p.col, p.fila, marker="o", markersize=9,
                            markerfacecolor="#2B8A3E" if etiqueta.lower().startswith("o") else "#1864AB",
                            markeredgecolor="white", markeredgewidth=1.4)
                    ax.annotate(etiqueta, (p.col, p.fila), textcoords="offset points",
                                xytext=(7, 6), fontsize=9, color="#212529",
                                bbox=dict(boxstyle="round,pad=0.2", fc="white", ec="none", alpha=0.85))

    leyenda = [
        plt.Rectangle((0, 0), 1, 1, fc=COLORES(i), ec="#adb5bd") for i in range(4)
    ] + [Line2D([], [], marker="s", color="#0B7285", markerfacecolor="none", linestyle="none", markersize=7)]
    fig.legend(leyenda, NOMBRES + ["escotilla"], loc="lower center", ncol=5,
               frameon=False, fontsize=9, bbox_to_anchor=(0.5, -0.02))
    if titulo:
        fig.suptitle(titulo, fontsize=12)
    fig.tight_layout()
    if ruta_salida:
        fig.savefig(ruta_salida, dpi=150, bbox_inches="tight")
    return fig
