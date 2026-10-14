"""Lee datos_obra.xlsx y genera la curva S y el avance por partidas (PNG en /graficos)."""
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

ARCHIVO = "datos_obra.xlsx"
SALIDA = Path("graficos")

BEIGE, VERDE, VERDE_OSC, VERDE_CLARO = "#F5EBDC", "#4F7942", "#2F4F2F", "#A9C29A"
MARRON, MARRON_OSC, MARRON_CLARO = "#8B5A2B", "#5C3A1E", "#C9A57A"

plt.rcParams.update({
    "figure.facecolor": BEIGE, "axes.facecolor": BEIGE, "savefig.facecolor": BEIGE,
    "axes.edgecolor": MARRON_OSC, "axes.labelcolor": MARRON_OSC, "text.color": MARRON_OSC,
    "xtick.color": MARRON_OSC, "ytick.color": MARRON_OSC, "grid.color": MARRON_CLARO,
    "grid.alpha": 0.4, "font.size": 10, "axes.spines.top": False, "axes.spines.right": False,
})


def cargar():
    xl = pd.ExcelFile(ARCHIVO)
    info = xl.parse("Proyecto").set_index("Dato")["Valor"]
    partidas = xl.parse("Partidas", dtype={"Código": str})
    prog = xl.parse("Programado_acum_%").set_index("Semana")
    real = xl.parse("Real_acum_%").set_index("Semana")
    return info, partidas, prog, real


def avance_global(df, partidas):
    """Avance acumulado ponderado por presupuesto (%)."""
    pesos = partidas.set_index("Código")["Presupuesto (S/)"]
    pesos = pesos / pesos.sum()
    return (df[pesos.index] * pesos).sum(axis=1)


def grafico_curva_s(info, partidas, prog, real):
    plan = avance_global(prog, partidas)
    ejec = avance_global(real, partidas)
    corte = int(info["Semana de corte"])
    pl_c, re_c = plan.loc[corte], ejec.loc[corte]

    fig, ax = plt.subplots(figsize=(11, 6))
    ax.plot(plan.index, plan, color=MARRON, lw=2.8, label="Programado")
    ax.plot(ejec.index, ejec, color=VERDE, lw=2.8, label="Real")
    ax.fill_between(ejec.index, ejec, plan.loc[ejec.index], color=MARRON_CLARO, alpha=0.35, label="Brecha")
    ax.axvline(corte, color=MARRON_OSC, ls="--", lw=1)
    ax.scatter([corte, corte], [pl_c, re_c], color=[MARRON, VERDE], zorder=5, s=50)
    ax.annotate(f"Prog. {pl_c:.1f}%", (corte, pl_c), (corte - 9, pl_c + 6), color=MARRON_OSC, fontweight="bold")
    ax.annotate(f"Real {re_c:.1f}%", (corte, re_c), (corte + 1, re_c - 8), color=VERDE_OSC, fontweight="bold")
    ax.set(xlabel="Semana", ylabel="Avance acumulado (%)", xlim=(0, plan.index.max()), ylim=(0, 102))
    ax.set_title(f"Curva S – {info['Proyecto']}\nCorte semana {corte}: desviación {re_c - pl_c:+.1f} puntos %",
                 color=VERDE_OSC, fontsize=14, fontweight="bold", loc="left")
    ax.grid(True)
    ax.legend(frameon=False, loc="upper left")
    fig.tight_layout()
    fig.savefig(SALIDA / "curva_s.png", dpi=150)
    plt.close(fig)


def grafico_barras_partidas(info, partidas, prog, real):
    corte = int(info["Semana de corte"])
    d = partidas[["Código", "Partida"]].copy()
    d["Prog"] = prog.loc[corte, d["Código"]].values
    d["Real"] = real.loc[corte, d["Código"]].values
    d = d.iloc[::-1].reset_index(drop=True)
    y = range(len(d))

    fig, ax = plt.subplots(figsize=(11, 8))
    ax.barh([i + 0.2 for i in y], d["Prog"], height=0.38, color=MARRON_CLARO, edgecolor=MARRON, label="Programado")
    ax.barh([i - 0.2 for i in y], d["Real"], height=0.38, color=VERDE, edgecolor=VERDE_OSC, label="Real")
    for i, (p, r) in enumerate(zip(d["Prog"], d["Real"])):
        ax.text(r + 1, i - 0.2, f"{r:.0f}%", va="center", fontsize=8, color=VERDE_OSC)
        ax.text(p + 1, i + 0.2, f"{p:.0f}%", va="center", fontsize=8, color=MARRON_OSC)
    ax.set_yticks(list(y))
    ax.set_yticklabels(d["Código"] + "  " + d["Partida"])
    ax.set(xlim=(0, 112), xlabel="Avance acumulado (%)")
    ax.set_title(f"Avance por partidas al corte (semana {corte})", color=VERDE_OSC,
                 fontsize=14, fontweight="bold", loc="left")
    ax.grid(True, axis="x")
    ax.legend(frameon=False, loc="lower right")
    fig.tight_layout()
    fig.savefig(SALIDA / "avance_por_partidas.png", dpi=150)
    plt.close(fig)


def grafico_desviacion(info, partidas, prog, real):
    corte = int(info["Semana de corte"])
    d = partidas[["Código", "Partida"]].copy()
    d["Desv"] = real.loc[corte, d["Código"]].values - prog.loc[corte, d["Código"]].values
    d = d.sort_values("Desv")
    fig, ax = plt.subplots(figsize=(11, 7))
    ax.barh(d["Código"] + "  " + d["Partida"], d["Desv"],
            color=[VERDE if v >= 0 else MARRON for v in d["Desv"]])
    ax.axvline(0, color=MARRON_OSC, lw=1)
    ax.set(xlabel="Real – Programado (puntos %)")
    ax.set_title("Desviación del avance por partida", color=VERDE_OSC, fontsize=14, fontweight="bold", loc="left")
    ax.grid(True, axis="x")
    fig.tight_layout()
    fig.savefig(SALIDA / "desviacion_partidas.png", dpi=150)
    plt.close(fig)


def grafico_curvas_partidas(info, partidas, prog, real):
    """Mini-curvas programado vs real para cada partida."""
    corte = int(info["Semana de corte"])
    n = len(partidas)
    cols = 4
    filas = -(-n // cols)
    fig, axs = plt.subplots(filas, cols, figsize=(14, 2.6 * filas), sharex=True, sharey=True)
    for ax, (_, p) in zip(axs.flat, partidas.iterrows()):
        ax.plot(prog.index, prog[p["Código"]], color=MARRON, lw=1.8)
        ax.plot(real.index, real[p["Código"]], color=VERDE, lw=1.8)
        ax.set_title(f"{p['Código']} {p['Partida']}", fontsize=8, color=VERDE_OSC, loc="left")
        ax.grid(True)
    for ax in list(axs.flat)[n:]:
        ax.axis("off")
    fig.suptitle("Curvas S por partida (marrón: programado, verde: real)", color=VERDE_OSC,
                 fontsize=14, fontweight="bold")
    fig.supxlabel("Semana")
    fig.supylabel("Avance (%)")
    fig.tight_layout()
    fig.savefig(SALIDA / "curvas_por_partida.png", dpi=150)
    plt.close(fig)


def main():
    SALIDA.mkdir(exist_ok=True)
    info, partidas, prog, real = cargar()
    grafico_curva_s(info, partidas, prog, real)
    grafico_barras_partidas(info, partidas, prog, real)
    grafico_desviacion(info, partidas, prog, real)
    grafico_curvas_partidas(info, partidas, prog, real)
    print(f"Gráficos guardados en {SALIDA.resolve()}")


if __name__ == "__main__":
    main()
