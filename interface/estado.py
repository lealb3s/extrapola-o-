"""Estado da sessão Streamlit: carregar casos e montar Parametros a partir dos widgets."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from extrap import Parametros, fluidos
from extrap.casos import CASOS, CASO_PLANILHA2

CASO_INICIAL = CASO_PLANILHA2["nome"]


def _tabela(V_m, R_Tm) -> pd.DataFrame:
    return pd.DataFrame({"V_m [m/s]": list(map(float, V_m)), "R_Tm [N]": list(map(float, R_Tm))})


def carregar_caso(nome: str | None = None) -> None:
    """Copia um caso pré-definido para o session_state (callback do seletor)."""
    nome = nome or st.session_state.get("caso", CASO_INICIAL)
    c = CASOS[nome]
    p: Parametros = c["params"]
    ss = st.session_state
    ss.L_m, ss.S_m, ss.rho_m, ss.nu_m_e6 = p.L_m, p.S_m, p.rho_m, p.nu_m * 1e6
    ss.L_s, ss.rho_s, ss.nu_s_e6 = p.L_s, p.rho_s, p.nu_s * 1e6
    ss.S_s_manual = p.S_s is not None
    ss.S_s = p.S_s if p.S_s is not None else p.S_m * p.escala**2
    ss.k, ss.g, ss.linha, ss.C_A_e3 = p.k, p.g, p.linha_atrito, p.C_A * 1e3
    ss.modo_agua = "Informar ρ e ν"
    ss.T_m, ss.T_s = 15.0, 15.0
    ss.nome = c["nome"] if c is not CASOS.get("Novo caso (em branco)") else ""
    ss.referencia = c["referencia"]
    ss.caracteristicas = ""
    ss.tabela = _tabela(c["V_m"], c["R_Tm"])
    ss.tabela_ver = ss.get("tabela_ver", 0) + 1


def inicializar() -> None:
    if "inicializado" not in st.session_state:
        st.session_state.caso = CASO_INICIAL
        carregar_caso(CASO_INICIAL)
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
