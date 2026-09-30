"""Conteúdo de cada aba da área principal."""

from __future__ import annotations

import numpy as np
import pandas as pd
import streamlit as st

from extrap import (
    Parametros, gerar_memorial, prohaska, ROTULOS, Aviso,
)
from extrap.exportar import gerar_xlsx
from . import graficos as G

ICONES = {"erro": "🛑", "alerta": "⚠️", "info": "ℹ️"}


# ---------------------------------------------------------------------------
def mostrar_avisos(avisos: list[Aviso]) -> None:
    """DETECTAR → EXPLICAR → AVISAR → MOSTRAR CONSEQUÊNCIAS → O USUÁRIO DECIDE."""
    if not avisos:
        st.success("✅ Nenhuma inconsistência detectada nos dados de entrada ou nos resultados.")
        return
    for a in avisos:
        corpo = f"**{a.titulo}** — {a.explicacao}"
        if a.consequencia:
            corpo += f"\n\n*Consequência:* {a.consequencia}"
        {"erro": st.error, "alerta": st.warning, "info": st.info}[a.nivel](corpo, icon=ICONES[a.nivel])


def _fmt_tabela(df: pd.DataFrame, colunas: list[str]) -> pd.DataFrame:
    return df[colunas].rename(columns=ROTULOS)


def _config_colunas(colunas: list[str]) -> dict:
    cfg = {}
    for c in colunas:
        rot = ROTULOS.get(c, c)
        if c.startswith(("C_",)):
            cfg[rot] = st.column_config.NumberColumn(rot, format="%.4e")
        elif c.startswith("Re"):
            cfg[rot] = st.column_config.NumberColumn(rot, format="%.3e")
        elif c in ("Fn", "Fn_s"):
            cfg[rot] = st.column_config.NumberColumn(rot, format="%.4f")
        elif c == "dif_%":
            cfg[rot] = st.column_config.NumberColumn(rot, format="%.2f")
        else:
            cfg[rot] = st.column_config.NumberColumn(rot, format="%.3f")
    return cfg


# ---------------------------------------------------------------------------
def aba_dados() -> pd.DataFrame:
    ss = st.session_state
    c1, c2 = st.columns([3, 2], gap="large")
    with c1:
        st.subheader("Ensaio de reboque do modelo")
        st.caption("Cole ou digite os pares (V_m, R_Tm). Use o **+** no rodapé para adicionar linhas; "
                   "selecione e apague linhas com a tecla Delete.")
        editado = st.data_editor(
            ss.tabela,
            num_rows="dynamic",
            key=f"editor_{ss.tabela_ver}",
            column_config={
                "V_m [m/s]": st.column_config.NumberColumn("V_m [m/s]", min_value=0.0, format="%.4f", required=True),
                "R_Tm [N]": st.column_config.NumberColumn("R_Tm [N]", min_value=0.0, format="%.4f", required=True),
            },
            hide_index=False,
        )
    with c2:
        st.subheader("Modelo selecionado")
        st.text_input("Nome / identificação", key="nome")
        st.text_area("Referência bibliográfica", key="referencia", height=90,
                     placeholder="Autor(es), título, periódico/instituição, ano, DOI/URL…")
        st.text_area("Características principais", key="caracteristicas", height=110,
                     placeholder="Tipo de navio, L_pp, B, T, C_B, deslocamento, escala, tanque de ensaio…")
        img = st.file_uploader("Imagem do modelo", type=["png", "jpg", "jpeg"])
        if img is not None:
            ss.imagem = img.getvalue()
        if ss.get("imagem"):
            st.image(ss.imagem, caption=ss.nome or None)
            if st.button("Remover imagem"):
                ss.imagem = None
                st.rerun()
    return editado


def aba_resultados(df: pd.DataFrame, p: Parametros, avisos: list[Aviso]) -> None:
    st.subheader("Verificações automáticas")
    mostrar_avisos(avisos)
    if df.empty:
        return
    st.subheader("Resumo")
    i_max = df["V_s"].idxmax()
    r = df.loc[i_max]
    c = st.columns(5)
    c[0].metric("Escala λ", f"{p.escala:.3f}")
    c[1].metric("S_s usada", f"{p.S_s_usada:,.1f} m²")
    c[2].metric(f"V_s máx. (Fn = {r.Fn:.3f})", f"{r.V_s_nos:.2f} nós")
    c[3].metric("P_E Froude (V_s máx.)", f"{r.P_E_F_kW:,.0f} kW", help=f"{r.P_E_F_hp:,.0f} hp")
    c[4].metric("P_E Hughes (V_s máx.)", f"{r.P_E_H_kW:,.0f} kW", f"{r['dif_%']:+.1f} % vs Froude",
                delta_color="off", help=f"{r.P_E_H_hp:,.0f} hp")

    grupos = {
        "Modelo e semelhança": ["V_m", "R_Tm", "Fn", "Re_m", "C_Tm", "C_Fm", "V_s", "V_s_nos", "Re_s", "C_Fs"],
        "(A) Froude": ["V_s_nos", "Fn", "C_Tm", "C_Fm", "C_R", "C_Fs", "C_Ts_F", "R_Ts_F_kN", "P_E_F_kW", "P_E_F_hp"],
        "(B) Hughes": ["V_s_nos", "Fn", "C_Tm", "C_Vm", "C_W", "C_Vs", "C_Ts_H", "R_Ts_H_kN", "P_E_H_kW", "P_E_H_hp"],
        "Comparação": ["V_s_nos", "Fn", "R_Ts_F_kN", "R_Ts_H_kN", "P_E_F_kW", "P_E_H_kW", "P_E_F_hp", "P_E_H_hp", "dif_%"],
    }
    tabs = st.tabs(list(grupos))
    for t, (nome, cols) in zip(tabs, grupos.items()):
        with t:
            st.dataframe(_fmt_tabela(df, cols), column_config=_config_colunas(cols), hide_index=True)


def aba_graficos(df: pd.DataFrame, p: Parametros) -> None:
    if df.empty:
        st.info("Sem pontos válidos para traçar.")
        return
    c1, c2 = st.columns(2)
    eixo = c1.radio("Eixo horizontal", list(G.EIXOS_X), horizontal=True, key="eixo_x")
    un = c2.radio("Unidade de potência", ["kW", "hp"], horizontal=True, key="un_pot")
    d = df.sort_values("V_m")
    st.plotly_chart(G.fig_resistencia(d, eixo), use_container_width=True, theme=None)
    st.plotly_chart(G.fig_potencia(d, eixo, un), use_container_width=True, theme=None)
    with st.expander("Mais gráficos: coeficientes, parcelas e diferença entre métodos", expanded=False):
        st.plotly_chart(G.fig_coeficientes(d, p.k, eixo), use_container_width=True, theme=None)
        st.plotly_chart(G.fig_parcelas(d, eixo), use_container_width=True, theme=None)
        st.plotly_chart(G.fig_diferenca(d, eixo), use_container_width=True, theme=None)
        st.caption(
            "Hughes separa a parcela viscosa (1+k)·C_F, que é corrigida pela escala via Re; "
            "Froude transfere integralmente C_R = C_T − C_F. Como a parte de forma escala junto com "
            "C_F no método de Hughes, ele normalmente prevê resistência menor para o navio — mas não sempre."
        )


def aba_memorial(df: pd.DataFrame, p: Parametros) -> None:
    if df.empty:
        st.info("Sem pontos válidos.")
        return
    d = df.sort_values("V_m").reset_index(drop=True)
    opcoes = [f"V_m = {v:.4g} m/s  →  V_s = {vs:.2f} nós (Fn = {fn:.4f})"
              for v, vs, fn in zip(d.V_m, d.V_s_nos, d.Fn)]
    i = st.selectbox("Velocidade para o memorial", range(len(opcoes)), format_func=lambda j: opcoes[j])
    linha = d.iloc[i]
    st.caption("Passo a passo calculado a partir dos dados informados. "
               "Números com 4 algarismos significativos; os cálculos internos não são arredondados.")
    with st.expander("Diagrama C × Re desta velocidade", expanded=True):
        st.plotly_chart(G.fig_diagrama_re(p, linha), use_container_width=True, theme=None)
        st.caption(
            "**Froude:** a distância C_T − C_F (azul) é transportada igual do modelo para o navio.  \n"
            "**Hughes:** a distância C_T − (1+k)·C_F (laranja) é transportada igual. "
            "Como a curva viscosa é mais alta, a parcela transportada é menor."
        )

    passos = gerar_memorial(p, linha)
    secoes = list(dict.fromkeys(ps.secao for ps in passos))
    contador = iter(range(1, len(passos) + 1))

    def _render(secao):
        st.markdown(f"#### {secao}")
        for ps in passos:
            if ps.secao == secao:
                st.markdown(f"**{next(contador)}. {ps.titulo}**")
                st.latex(ps.latex)

    _render(secoes[0])
    st.divider()
    ca, cb = st.columns(2, gap="large")
    with ca:
        _render(secoes[1])
    with cb:
        _render(secoes[2])


def aba_prohaska(df: pd.DataFrame, p: Parametros) -> None:
    st.markdown(
        "Em baixas velocidades supõe-se C_W ∝ Fn⁴, então "
        r"$\dfrac{C_T}{C_F} = (1+k) + c\,\dfrac{Fn^4}{C_F}$. "
        "A reta ajustada aos pontos do ensaio cruza o eixo vertical em **1+k** (ITTC 7.5-02-02-01; "
        "recomenda-se 0,1 ≤ Fn ≤ 0,2)."
    )
    if len(df) < 3:
        st.info("São necessários pelo menos 3 pontos de ensaio.")
        return
    fmin, fmax = float(df.Fn.min()), float(df.Fn.max())
    faixa = st.slider("Faixa de Fn usada na regressão", 0.0, max(0.5, round(fmax + 0.02, 2)),
                      (0.0, min(0.2, round(fmax + 0.005, 3))), step=0.005)
    try:
        res = prohaska(df.Fn, df.C_Tm, df.C_Fm, *faixa)
    except ValueError as e:
        st.warning(str(e))
        return
    c1, c2 = st.columns([3, 1])
    c1.plotly_chart(G.fig_prohaska(res, p.k), use_container_width=True, theme=None)
    c2.metric("k estimado", f"{res.k:.4f}")
    c2.metric("R² do ajuste", f"{res.r2:.4f}")
    c2.metric("Pontos usados", res.n_pontos)
    c2.metric("k em uso", f"{p.k:.4f}")
    if fmin > 0.1 or res.n_pontos < 4:
        c2.caption("⚠️ Poucos pontos ou Fn fora da faixa recomendada: estimativa pouco robusta.")
    if res.r2 < 0.9:
        c2.caption("⚠️ R² baixo: os pontos não seguem bem a hipótese C_W ∝ Fn⁴.")

    def _usar():
        st.session_state.k = round(res.k, 4)

    c2.button("Usar este k no cálculo", on_click=_usar, type="primary")
    st.caption("O app **não** troca k sozinho: compare com o k da literatura e decida.")


def aba_exportar(df: pd.DataFrame, p: Parametros, V_m, R_Tm) -> None:
    ss = st.session_state
    st.markdown(
        "A planilha exportada contém **fórmulas** (não só valores): alterar qualquer célula azul "
        "recalcula a extrapolação e os gráficos de R_Ts e P_E × Fn. Inclui também a aba **Modelo** "
        "com nome, referência, características e a imagem enviada na aba *Dados*."
    )
    nome_arq = (ss.nome or "extrapolacao").strip().replace(" ", "_")[:40]
    xlsx = gerar_xlsx(p, V_m, R_Tm, ss.nome, ss.referencia, ss.caracteristicas, ss.get("imagem"))
    c1, c2 = st.columns(2)
    c1.download_button("⬇️ Planilha Excel (.xlsx) com fórmulas", xlsx, file_name=f"{nome_arq}.xlsx",
                       mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                       type="primary")
    csv = df.rename(columns=ROTULOS).to_csv(index=False, sep=";", decimal=",").encode("utf-8-sig")
    c2.download_button("⬇️ Resultados completos (.csv)", csv, file_name=f"{nome_arq}_resultados.csv",
                       mime="text/csv")
