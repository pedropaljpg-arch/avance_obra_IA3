"""Genera datos sintéticos de una obra (edificio multifamiliar de 6 pisos) en Excel."""
import numpy as np
import pandas as pd

SEMILLA = 19
N_SEMANAS = 48          # duración programada de la obra
SEMANA_CORTE = 30       # semana de corte del control de avance
FECHA_INICIO = pd.Timestamp("2026-01-05")
ARCHIVO = "datos_obra.xlsx"

# (código, partida, unidad, metrado, precio unitario S/, inicio, fin, retraso real: factor de ritmo)
# factor < 1: la partida avanza más lento que lo programado; > 1: más rápido
PARTIDAS = [
    ("01.01", "Trabajos preliminares",        "glb", 1,      38000,  1,  3, 1.00),
    ("01.02", "Movimiento de tierras",        "m3",  4200,   42,     2,  6, 1.05),
    ("02.01", "Cimentación y platea",         "m3",  620,    610,    5, 11, 0.92),
    ("02.02", "Columnas y placas",            "m3",  540,    780,    9, 26, 0.85),
    ("02.03", "Vigas y losas aligeradas",     "m2",  5400,   165,   10, 28, 0.82),
    ("02.04", "Acero de refuerzo",            "kg",  98000,  5.6,    7, 27, 0.88),
    ("03.01", "Muros de albañilería",         "m2",  6800,   78,    16, 34, 0.80),
    ("03.02", "Tarrajeo y revoques",          "m2",  13500,  34,    22, 40, 0.70),
    ("04.01", "Instalaciones sanitarias",     "pto", 360,    185,   18, 40, 0.90),
    ("04.02", "Instalaciones eléctricas",     "pto", 880,    92,    20, 42, 0.95),
    ("05.01", "Pisos y contrapisos",          "m2",  5100,   58,    30, 44, 1.00),
    ("05.02", "Carpintería de madera",        "und", 140,    720,   32, 46, 1.00),
    ("05.03", "Carpintería metálica y vidrios","m2", 460,    340,   34, 47, 1.00),
    ("06.01", "Pintura",                      "m2",  21000,  16,    38, 48, 1.00),
    ("06.02", "Aparatos sanitarios y acabados","glb", 1,     96000, 40, 48, 1.00),
]


def curva_s(n, a=3.0):
    """Avance acumulado (0-1) de una partida con forma de S (sigmoide normalizada)."""
    t = np.linspace(0, 1, n + 1)[1:]
    s = 1 / (1 + np.exp(-a * 2 * (t - 0.5)))
    s0, s1 = 1 / (1 + np.exp(a)), 1 / (1 + np.exp(-a))
    return (s - s0) / (s1 - s0)


def main():
    rng = np.random.default_rng(SEMILLA)
    semanas = np.arange(1, N_SEMANAS + 1)

    partidas = pd.DataFrame(
        PARTIDAS,
        columns=["Código", "Partida", "Unidad", "Metrado", "P.U. (S/)",
                 "Semana inicio", "Semana fin", "Ritmo real"],
    )
    partidas["Presupuesto (S/)"] = (partidas["Metrado"] * partidas["P.U. (S/)"]).round(2)
    partidas["Peso (%)"] = (partidas["Presupuesto (S/)"] / partidas["Presupuesto (S/)"].sum() * 100).round(2)

    prog = pd.DataFrame({"Semana": semanas})
    real = pd.DataFrame({"Semana": semanas[:SEMANA_CORTE]})

    for _, p in partidas.iterrows():
        dur = p["Semana fin"] - p["Semana inicio"] + 1
        acum = curva_s(dur)
        plan = np.zeros(N_SEMANAS)
        plan[p["Semana inicio"] - 1: p["Semana fin"]] = acum
        plan[p["Semana fin"]:] = 1.0
        prog[p["Código"]] = (plan * 100).round(2)

        # Avance real: inicio con 0-2 semanas de desfase, ritmo distinto y ruido
        desfase = int(rng.integers(0, 3)) if p["Ritmo real"] < 1 else 0
        r = np.zeros(SEMANA_CORTE)
        for w in range(SEMANA_CORTE):
            k = w + 1 - (p["Semana inicio"] + desfase)
            if k < 0:
                continue
            x = min((k + 1) * p["Ritmo real"] / dur, 1.0)
            idx = x * dur
            base = np.interp(idx, np.arange(0, dur + 1), np.concatenate([[0], acum]))
            r[w] = base
        r = r + rng.normal(0, 0.008, SEMANA_CORTE) * (r > 0) * (r < 1)
        r = np.clip(np.maximum.accumulate(r), 0, 1)   # el avance acumulado no retrocede
        real[p["Código"]] = (r * 100).round(2)

    resumen = pd.DataFrame({
        "Dato": ["Proyecto", "Ubicación", "Fecha de inicio", "Duración (semanas)",
                 "Semana de corte", "Fecha de corte", "Presupuesto total (S/)"],
        "Valor": ["Edificio multifamiliar 6 pisos + semisótano", "Lima, Perú",
                  FECHA_INICIO.date().isoformat(), N_SEMANAS, SEMANA_CORTE,
                  (FECHA_INICIO + pd.Timedelta(weeks=SEMANA_CORTE - 1)).date().isoformat(),
                  float(partidas["Presupuesto (S/)"].sum())],
    })

    with pd.ExcelWriter(ARCHIVO, engine="openpyxl") as xl:
        resumen.to_excel(xl, sheet_name="Proyecto", index=False)
        partidas.drop(columns="Ritmo real").to_excel(xl, sheet_name="Partidas", index=False)
        prog.to_excel(xl, sheet_name="Programado_acum_%", index=False)
        real.to_excel(xl, sheet_name="Real_acum_%", index=False)
        for ws in xl.book.worksheets:
            for col in ws.columns:
                ws.column_dimensions[col[0].column_letter].width = max(len(str(c.value or "")) for c in col) + 3
    print(f"Archivo generado: {ARCHIVO} | Presupuesto total S/ {partidas['Presupuesto (S/)'].sum():,.0f}")


if __name__ == "__main__":
    main()

