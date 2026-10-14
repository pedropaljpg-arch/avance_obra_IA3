# Curva S y avance de obra por partidas

Proyecto de ejemplo: edificio multifamiliar de 6 pisos (48 semanas, presupuesto ≈ S/ 4.58 M), con control de avance al corte de la **semana 30**.

## Estructura

| Archivo | Función |
|---|---|
| `generar_datos.py` | Crea los datos sintéticos y los guarda en `datos_obra.xlsx`. |
| `datos_obra.xlsx` | Base de datos de la obra (ver hojas abajo). |
| `graficos_obra.py` | Lee el Excel y genera los gráficos en `graficos/`. |
| `.venv/` | Entorno virtual (pandas, numpy, matplotlib, openpyxl). |

## Hojas del Excel

- **Proyecto**: nombre, fechas, semana de corte y presupuesto total.
- **Partidas**: 15 partidas con metrado, unidad, precio unitario, presupuesto, peso (%) y semanas de inicio/fin programadas.
- **Programado_acum_%**: avance acumulado programado por partida y semana (semanas 1–48).
- **Real_acum_%**: avance acumulado real por partida hasta la semana de corte (1–30).

## Cómo se generan los datos (coherencia)

- Presupuesto de cada partida = metrado × precio unitario; el peso es su proporción del total.
- El avance programado de cada partida sigue una **curva en S** (sigmoide normalizada) entre su semana de inicio y fin, por lo que la secuencia constructiva es lógica (estructura → albañilería → instalaciones → acabados).
- El avance real usa la misma curva pero con un **ritmo distinto** por partida (las de estructura y tarrajeo rinden menos), posibles desfases de inicio y ruido aleatorio. Nunca retrocede. La semilla (`SEMILLA = 19`) hace los datos reproducibles.

## Cómo funcionan los gráficos

El avance global se calcula como el **promedio ponderado por presupuesto** del avance de cada partida. Se generan en `graficos/`:

1. `curva_s.png`: curva S programada vs. real, con la brecha sombreada y la desviación al corte.
2. `avance_por_partidas.png`: barras programado vs. real por partida al corte.
3. `desviacion_partidas.png`: real − programado por partida (verde adelantada, marrón atrasada).
4. `curvas_por_partida.png`: mini curvas S de cada partida.

Estilo: fondo beige, verde para lo real y marrón para lo programado.

## Uso

```bash
.venv\Scripts\python.exe generar_datos.py
.venv\Scripts\python.exe graficos_obra.py
```

Para usar datos propios, reemplaza `datos_obra.xlsx` manteniendo los nombres de hojas y columnas, y ejecuta solo `graficos_obra.py`.

## Página web (Streamlit)

`app.py` muestra indicadores, gráficos y tablas en pestañas. Ejecutar con:

```bash
.venv\Scripts\streamlit run app.py
```
