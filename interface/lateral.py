"""Barra lateral: seleção de caso e parâmetros de entrada."""

from __future__ import annotations

import streamlit as st

from extrap import LINHAS, fluidos
from extrap.casos import CASOS
from .estado import carregar_caso


def desenhar() -> None:
    ss = st.session_state
    sb = st.sidebar
    sb.header("⚙️ Parâmetros")
    sb.selectbox(
        "Caso carregado",
        list(CASOS),
        key="caso",
        on_change=carregar_caso,
        help="Trocar o caso substitui todos os parâmetros e a tabela de ensaio.",
    )

    with sb.expander("🧪 Modelo (tanque de provas)", expanded=True):
        st.number_input("L_m — comprimento [m]", min_value=0.0, step=0.1, format="%.4f", key="L_m")
        st.number_input("S_m — superfície molhada [m²]", min_value=0.0, step=0.1, format="%.4f", key="S_m")

    with sb.expander("🚢 Protótipo (navio)", expanded=True):
        st.number_input("L_s — comprimento [m]", min_value=0.0, step=1.0, format="%.3f", key="L_s")
        lam = ss.L_s / ss.L_m if ss.L_m else float("nan")
        st.caption(f"Escala λ = L_s / L_m = **{lam:.4f}**")
        st.toggle("Informar S_s manualmente", key="S_s_manual",
                  help="Desligado: S_s = S_m·λ² (semelhança geométrica, como no exercício).")
        if ss.S_s_manual:
            st.number_input("S_s — superfície molhada [m²]", min_value=0.0, step=10.0, format="%.2f", key="S_s")
        else:
            st.caption(f"S_s = S_m·λ² = **{ss.S_m * lam**2:,.2f} m²**")

    with sb.expander("💧 Propriedades da água", expanded=False):
        st.radio("Modo", ["Informar ρ e ν", "Pela temperatura (ITTC)"], key="modo_agua", horizontal=True)
        if ss.modo_agua == "Informar ρ e ν":
            c1, c2 = st.columns(2)
            c1.markdown("**Tanque (doce)**")
            c1.number_input("ρ_m [kg/m³]", min_value=0.0, step=1.0, format="%.2f", key="rho_m")
            c1.number_input("ν_m [×10⁻⁶ m²/s]", min_value=0.0, step=0.001, format="%.4f", key="nu_m_e6")
            c2.markdown("**Mar (salgada)**")
            c2.number_input("ρ_s [kg/m³]", min_value=0.0, step=1.0, format="%.2f", key="rho_s")
            c2.number_input("ν_s [×10⁻⁶ m²/s]", min_value=0.0, step=0.001, format="%.4f", key="nu_s_e6")
        else:
            c1, c2 = st.columns(2)
            c1.number_input("T tanque [°C]", min_value=0.0, max_value=30.0, step=0.5, key="T_m")
            c2.number_input("T mar [°C]", min_value=0.0, max_value=30.0, step=0.5, key="T_s")
            rm, nm = fluidos.propriedades("doce", ss.T_m)
            rs, ns = fluidos.propriedades("salgada", ss.T_s)
            c1.caption(f"ρ_m = {rm:.2f} kg/m³  \nν_m = {nm*1e6:.4f}×10⁻⁶ m²/s")
            c2.caption(f"ρ_s = {rs:.2f} kg/m³  \nν_s = {ns*1e6:.4f}×10⁻⁶ m²/s")
            st.caption("Correlações ITTC 7.5-02-01-03 (0–30 °C).")

    with sb.expander("📐 Método", expanded=True):
        st.number_input("k — fator de forma (Hughes)", min_value=-1.0, step=0.01, format="%.4f", key="k",
                        help="Pode ser estimado pelo método de Prohaska na aba 'Fator de forma'.")
        st.selectbox("Linha de atrito", list(LINHAS), key="linha",
                     help="O exercício resolvido usa a linha ITTC-1957 nos dois métodos.")
        st.latex(LINHAS[ss.linha])
        st.number_input("C_A — correção de correlação [×10⁻³]", step=0.01, format="%.3f", key="C_A_e3",
                        help="Somado ao C_Ts nos dois métodos. O exercício usa 0.")
        st.number_input("g [m/s²]", min_value=0.0, step=0.01, format="%.3f", key="g")
