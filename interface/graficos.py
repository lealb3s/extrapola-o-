"""Figuras Plotly."""

from __future__ import annotations

import numpy as np
import pandas as pd
import plotly.graph_objects as go

from extrap import Parametros, coef_atrito, HP_EM_W

COR_F = "#2E6FBA"   # Froude
COR_H = "#D9822B"   # Hughes
COR_M = "#5B6770"   # modelo / neutro

EIXOS_X = {
    "Fn": ("Fn", "Número de Froude, Fn"),
    "V_s [nós]": ("V_s_nos", "Velocidade do navio, V_s [nós]"),
    "V_s [m/s]": ("V_s", "Velocidade do navio, V_s [m/s]"),
}


def _layout(fig: go.Figure, titulo: str, xt: str, yt: str) -> go.Figure:
    fig.update_layout(
        title=dict(text=titulo, x=0.0, xanchor="left"),
        xaxis_title=xt, yaxis_title=yt,
        hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=10, r=10, t=70, b=10),
        height=430,
    )
    fig.update_xaxes(showgrid=True, gridcolor="rgba(128,128,128,0.2)")
    fig.update_yaxes(showgrid=True, gridcolor="rgba(128,128,128,0.2)", rangemode="tozero")
    return fig


def _duas_curvas(df, xcol, yF, yH, fmt, nome_y):
    fig = go.Figure()
    for col, nome, cor, simb in ((yF, "Froude (sem k)", COR_F, "circle"), (yH, "Hughes (com k)", COR_H, "square")):
        fig.add_trace(go.Scatter(
            x=df[xcol], y=df[col], mode="lines+markers", name=nome,
            line=dict(color=cor, width=2.5), marker=dict(symbol=simb, size=8, color=cor),
            hovertemplate=f"{nome_y} = %{{y:{fmt}}}<extra>{nome}</extra>",
        ))
    return fig


def fig_resistencia(df: pd.DataFrame, eixo: str = "Fn") -> go.Figure:
    xcol, xt = EIXOS_X[eixo]
    fig = _duas_curvas(df, xcol, "R_Ts_F_kN", "R_Ts_H_kN", ",.1f", "R_Ts [kN]")
    return _layout(fig, "Resistência total ao avanço do navio", xt, "R_Ts [kN]")


def fig_potencia(df: pd.DataFrame, eixo: str = "Fn", unidade: str = "kW") -> go.Figure:
    xcol, xt = EIXOS_X[eixo]
    suf = "kW" if unidade == "kW" else "hp"
    fig = _duas_curvas(df, xcol, f"P_E_F_{suf}", f"P_E_H_{suf}", ",.0f", f"P_E [{suf}]")
    return _layout(fig, "Potência efetiva do navio", xt, f"P_E [{suf}]")


def fig_coeficientes(df: pd.DataFrame, k: float, eixo: str = "Fn") -> go.Figure:
    xcol, xt = EIXOS_X[eixo]
    fig = go.Figure()
    tr = [
        ("C_Tm", "C_Tm (modelo, medido)", COR_M, "solid", "circle"),
        ("C_Fm", "C_Fm", COR_M, "dot", None),
        ("C_Vm", "(1+k)·C_Fm", COR_M, "dash", None),
        ("C_Ts_F", "C_Ts Froude", COR_F, "solid", "circle"),
        ("C_Ts_H", "C_Ts Hughes", COR_H, "solid", "square"),
        ("C_Fs", "C_Fs", "#7FA7D6", "dot", None),
        ("C_Vs", "(1+k)·C_Fs", "#E9B27F", "dash", None),
    ]
    for col, nome, cor, dash, simb in tr:
        fig.add_trace(go.Scatter(
            x=df[xcol], y=df[col] * 1e3, name=nome, mode="lines+markers" if simb else "lines",
            line=dict(color=cor, dash=dash, width=2), marker=dict(symbol=simb or "circle", size=7),
            hovertemplate="%{y:.4f}×10⁻³<extra>" + nome + "</extra>",
        ))
    return _layout(fig, "Coeficientes de resistência (modelo × navio)", xt, "C × 10³")


def fig_parcelas(df: pd.DataFrame, eixo: str = "Fn") -> go.Figure:
    xcol, xt = EIXOS_X[eixo]
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df[xcol], y=df["C_R"] * 1e3, name="C_R (Froude)", mode="lines+markers",
                             line=dict(color=COR_F, width=2)))
    fig.add_trace(go.Scatter(x=df[xcol], y=df["C_W"] * 1e3, name="C_W (Hughes)", mode="lines+markers",
                             line=dict(color=COR_H, width=2), marker=dict(symbol="square")))
    fig.add_hline(y=0, line=dict(color="gray", width=1))
    fig = _layout(fig, "Parcela transferida sem correção de escala", xt, "C × 10³")
    fig.update_yaxes(rangemode="normal")
    return fig


def fig_diferenca(df: pd.DataFrame, eixo: str = "Fn") -> go.Figure:
    xcol, xt = EIXOS_X[eixo]
    fig = go.Figure(go.Bar(x=df[xcol], y=df["dif_%"], marker_color=COR_H,
                           hovertemplate="%{y:.2f} %<extra></extra>"))
    fig = _layout(fig, "Diferença de P_E: Hughes em relação a Froude", xt, "ΔP_E [%]")
    fig.update_yaxes(rangemode="normal")
    fig.update_layout(hovermode="closest")
    return fig


def fig_diagrama_re(p: Parametros, linha: pd.Series) -> go.Figure:
    """Diagrama conceitual C × Re (como na 1ª página do exercício) para uma velocidade."""
    r = linha
    re = np.logspace(np.log10(r.Re_m) - 0.6, np.log10(r.Re_s) + 0.4, 200)
    cf = coef_atrito(re, p.linha_atrito)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=re, y=cf * 1e3, name=f"C_F ({p.linha_atrito})",
                             line=dict(color=COR_M, width=2)))
    fig.add_trace(go.Scatter(x=re, y=(1 + p.k) * cf * 1e3, name="(1+k)·C_F",
                             line=dict(color=COR_M, width=2, dash="dash")))

    def seta(x, y0, y1, cor, texto, lado):
        fig.add_trace(go.Scatter(x=[x, x], y=[y0 * 1e3, y1 * 1e3], mode="lines",
                                 line=dict(color=cor, width=4), showlegend=False, hoverinfo="skip"))
        fig.add_annotation(x=np.log10(x), y=(y0 + y1) / 2 * 1e3, text=texto, showarrow=False,
                           xshift=lado * 42, font=dict(color=cor, size=12),
                           bgcolor="rgba(255,255,255,0.8)")

    # modelo
    seta(r.Re_m / 1.07, r.C_Fm, r.C_Tm, COR_F, f"C_Rm<br>{r.C_R*1e3:.3f}", -1)
    seta(r.Re_m * 1.07, r.C_Vm, r.C_Tm, COR_H, f"C_Wm<br>{r.C_W*1e3:.3f}", +1)
    # navio
    seta(r.Re_s / 1.07, r.C_Fs, r.C_Ts_F, COR_F, f"C_Rs<br>{r.C_R*1e3:.3f}", -1)
    seta(r.Re_s * 1.07, r.C_Vs, r.C_Ts_H, COR_H, f"C_Ws<br>{r.C_W*1e3:.3f}", +1)
    fig.add_trace(go.Scatter(x=[r.Re_m], y=[r.C_Tm * 1e3], mode="markers", name="C_Tm (medido)",
                             marker=dict(size=13, color="#C0392B")))
    fig.add_trace(go.Scatter(x=[r.Re_s / 1.07, r.Re_s * 1.07], y=[r.C_Ts_F * 1e3, r.C_Ts_H * 1e3], mode="markers",
                             name="C_Ts (Froude / Hughes)",
                             marker=dict(size=12, color=[COR_F, COR_H], symbol=["circle", "square"])))
    fig.add_vline(x=r.Re_m, line=dict(color="gray", dash="dot"), annotation_text="Modelo", annotation_position="bottom right")
    fig.add_vline(x=r.Re_s, line=dict(color="gray", dash="dot"), annotation_text="Navio (mesmo Fn)", annotation_position="bottom left")
    fig = _layout(fig, f"Diagrama C × Re — Fn = {r.Fn:.4f}", "Número de Reynolds, Re (escala log)", "C × 10³")
    fig.update_xaxes(type="log")
    fig.update_layout(hovermode="closest", height=460,
                      legend=dict(orientation="h", yanchor="top", y=-0.18, xanchor="left", x=0))
    return fig


def fig_prohaska(res, k_atual: float) -> go.Figure:
    fig = go.Figure()
    m = res.mascara
    fig.add_trace(go.Scatter(x=res.x[m], y=res.y[m], mode="markers", name="Pontos usados",
                             marker=dict(size=10, color=COR_H)))
    if (~m).any():
        fig.add_trace(go.Scatter(x=res.x[~m], y=res.y[~m], mode="markers", name="Fora da faixa",
                                 marker=dict(size=9, color="lightgray", line=dict(color="gray", width=1))))
    xx = np.linspace(0, res.x.max() * 1.05, 50)
    fig.add_trace(go.Scatter(x=xx, y=res.um_mais_k + res.c * xx, mode="lines",
                             name=f"Ajuste: 1+k = {res.um_mais_k:.4f}", line=dict(color=COR_H, width=2)))
    fig.add_hline(y=1 + k_atual, line=dict(color=COR_F, dash="dash"),
                  annotation_text=f"1+k em uso = {1 + k_atual:.4f}", annotation_position="top left")
    fig = _layout(fig, "Método de Prohaska", "Fn⁴ / C_F", "C_T / C_F")
    fig.update_yaxes(rangemode="normal")
    fig.update_xaxes(rangemode="tozero")
    fig.update_layout(hovermode="closest")
    return fig
