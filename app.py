"""Página web (Streamlit) para ver los datos y gráficos de la obra."""
from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # backend sin ventana, necesario dentro de Streamlit
import streamlit as st

import graficos_obra as g

st.set_page_config(page_title="Control de obra", page_icon="🏗️", layout="wide")

st.markdown(
    f"""<style>
    .stApp {{ background-color: {g.BEIGE}; }}
    h1, h2, h3 {{ color: {g.VERDE_OSC}; }}
    [data-testid="stMetricValue"] {{ color: {g.MARRON_OSC}; }}
    </style>""",
    unsafe_allow_html=True,
)

if not Path(g.ARCHIVO).exists():
    st.error(f"No se encontró {g.ARCHIVO}. Ejecuta primero generar_datos.py.")
    st.stop()

# Regenera los PNG para que siempre reflejen el Excel actual
g.SALIDA.mkdir(exist_ok=True)
info, partidas, prog, real = g.cargar()
g.grafico_curva_s(info, partidas, prog, real)
g.grafico_barras_partidas(info, partidas, prog, real)
g.grafico_desviacion(info, partidas, prog, real)
g.grafico_curvas_partidas(info, partidas, prog, real)

corte = int(info["Semana de corte"])
plan = g.avance_global(prog, partidas).loc[corte]
ejec = g.avance_global(real, partidas).loc[corte]

st.title("🏗️ Control de avance de obra")
st.caption(f"{info['Proyecto']} · {info['Ubicación']} · corte semana {corte} ({info['Fecha de corte']})")

c1, c2, c3, c4 = st.columns(4)
c1.metric("Presupuesto total", f"S/ {float(info['Presupuesto total (S/)']):,.0f}")
c2.metric("Avance programado", f"{plan:.1f} %")
c3.metric("Avance real", f"{ejec:.1f} %")
c4.metric("Desviación", f"{ejec - plan:+.1f} pts", delta=f"{ejec - plan:.1f}")

tab1, tab2, tab3, tab4 = st.tabs(["Curva S", "Avance por partidas", "Curvas por partida", "Datos"])

with tab1:
    st.image(str(g.SALIDA / "curva_s.png"), width="stretch")
with tab2:
    a, b = st.columns(2)
    a.image(str(g.SALIDA / "avance_por_partidas.png"), width="stretch")
    b.image(str(g.SALIDA / "desviacion_partidas.png"), width="stretch")
with tab3:
    st.image(str(g.SALIDA / "curvas_por_partida.png"), width="stretch")
with tab4:
    st.subheader("Partidas")
    tabla = partidas.copy()
    tabla["Programado (%)"] = prog.loc[corte, tabla["Código"]].values
    tabla["Real (%)"] = real.loc[corte, tabla["Código"]].values
    tabla["Desviación (pts)"] = (tabla["Real (%)"] - tabla["Programado (%)"]).round(2)
    st.dataframe(tabla, width="stretch", hide_index=True)
    st.subheader("Avance acumulado programado (%)")
    st.dataframe(prog, width="stretch")
    st.subheader("Avance acumulado real (%)")
    st.dataframe(real, width="stretch")

