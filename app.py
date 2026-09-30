"""
Extrapolação Modelo-Protótipo — Métodos de Froude e Hughes

Rodar localmente:
    pip install -r requirements.txt
    streamlit run app.py
"""

import numpy as np
import streamlit as st

st.set_page_config(
    page_title="Extrapolação Modelo-Protótipo",
    page_icon="🚢",
    layout="wide",
)

from extrap import extrapolar, verificar_parametros, verificar_dados, verificar_resultados  # noqa: E402
from interface import estado, lateral, abas  # noqa: E402

estado.inicializar()
lateral.desenhar()
p = estado.parametros_atuais()

st.title("🚢 Extrapolação Modelo → Protótipo")
st.caption(
    "Resistência total ao avanço e potência efetiva do navio a partir do ensaio de reboque do modelo — "
    "**Método de Froude** (sem fator de forma) e **Método de Hughes** (com fator de forma k)."
)

t_dados, t_res, t_graf, t_mem, t_k, t_exp, t_teoria = st.tabs([
    "📋 Dados do ensaio", "📊 Resultados", "📈 Gráficos", "✍️ Memorial de cálculo",
    "🔬 Fator de forma (Prohaska)", "💾 Exportar", "📖 Teoria",
])

with t_dados:
    tabela = abas.aba_dados()

# ---- Limpeza dos pontos (DETECTAR) ---------------------------------------------
tab = tabela.dropna(how="all")
V_all = tab["V_m [m/s]"].to_numpy(dtype=float)
R_all = tab["R_Tm [N]"].to_numpy(dtype=float)
avisos = verificar_parametros(p) + verificar_dados(V_all, R_all)
validos = np.isfinite(V_all) & np.isfinite(R_all) & (V_all > 0) & (R_all > 0)
V_m, R_Tm = V_all[validos], R_all[validos]

erro_param = any(a.nivel == "erro" for a in verificar_parametros(p))
if erro_param or V_m.size == 0:
    import pandas as pd
    df = pd.DataFrame()
else:
    with np.errstate(all="ignore"):
        df = extrapolar(p, V_m, R_Tm)
    avisos += verificar_resultados(df, p)

with t_res:
    abas.aba_resultados(df, p, avisos)
with t_graf:
    abas.aba_graficos(df, p)
with t_mem:
    abas.aba_memorial(df, p)
with t_k:
    if not df.empty:
        abas.aba_prohaska(df, p)
with t_exp:
    if not df.empty:
        abas.aba_exportar(df, p, V_m, R_Tm)
    else:
        st.info("Corrija os dados de entrada para exportar.")
with t_teoria:
    from interface import teoria
    teoria.mostrar()

n_alertas = sum(a.nivel in ("erro", "alerta") for a in avisos)
if n_alertas:
    st.sidebar.warning(f"{n_alertas} aviso(s) — veja a aba **Resultados**.", icon="⚠️")
