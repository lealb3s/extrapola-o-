"""Estado da sessão Streamlit: carregar casos e montar Parametros a partir dos widgets."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from extrap import Parametros, fluidos


def limpar_dados() -> None:
    """Inicia um ensaio vazio, sem dados de embarcações de referência."""
    ss = st.session_state
    ss.L_m, ss.S_m, ss.L_s, ss.S_s = 0.0, 0.0, 0.0, 0.0
    ss.rho_m, ss.rho_s = 1000.0, 1025.0
    ss.nu_m_e6, ss.nu_s_e6 = 1.140, 1.190
    ss.S_s_manual = False
    ss.k, ss.g, ss.linha, ss.C_A_e3 = 0.0, 9.81, "ITTC-1957", 0.0
    ss.modo_agua = "Informar ρ e ν"
    ss.T_m, ss.T_s = 15.0, 15.0
    ss.nome, ss.referencia, ss.caracteristicas = "", "", ""
    ss.imagem = None
    ss.tabela = pd.DataFrame({
        "V_m [m/s]": pd.Series(dtype=float),
        "R_Tm [N]": pd.Series(dtype=float),
    })
    ss.tabela_ver = ss.get("tabela_ver", 0) + 1


def inicializar() -> None:
    if "inicializado" not in st.session_state:
        limpar_dados()
        st.session_state.inicializado = True


def parametros_atuais() -> Parametros:
    ss = st.session_state
    if ss.modo_agua == "Pela temperatura (ITTC)":
        rho_m, nu_m = fluidos.propriedades("doce", ss.T_m)
        rho_s, nu_s = fluidos.propriedades("salgada", ss.T_s)
    else:
        rho_m, nu_m = ss.rho_m, ss.nu_m_e6 * 1e-6
        rho_s, nu_s = ss.rho_s, ss.nu_s_e6 * 1e-6
    return Parametros(
        L_m=ss.L_m, S_m=ss.S_m, rho_m=rho_m, nu_m=nu_m,
        L_s=ss.L_s, S_s=ss.S_s if ss.S_s_manual else None, rho_s=rho_s, nu_s=nu_s,
        k=ss.k, g=ss.g, linha_atrito=ss.linha, C_A=ss.C_A_e3 * 1e-3,
    )
