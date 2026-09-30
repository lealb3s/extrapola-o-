"""
Memorial de cálculo passo a passo para UMA velocidade, no mesmo roteiro do
exercício resolvido (Parte A — Froude; Parte B — Hughes).

Gera uma lista de passos com expressões LaTeX já com os números substituídos,
útil para conferir o procedimento feito "à mão".
"""

from __future__ import annotations

from dataclasses import dataclass
import math

import pandas as pd

from .extrapolacao import Parametros, HP_EM_W


@dataclass
class Passo:
    secao: str
    titulo: str
    latex: str
    nota: str = ""


def num(x: float, sig: int = 4) -> str:
    """Formata para LaTeX com vírgula decimal e notação ×10^n quando conveniente."""
    if x == 0 or not math.isfinite(x):
        return str(x)
    exp = int(math.floor(math.log10(abs(x))))
    if -2 <= exp <= 5:
        casas = max(sig - 1 - exp, 0)
        s = f"{x:,.{casas}f}"
        s = s.replace(",", "X").replace(".", "{,}").replace("X", r"\,")
        return s
    mant = x / 10**exp
    s = f"{mant:.{sig - 1}f}".replace(".", "{,}")
    return rf"{s} \times 10^{{{exp}}}"


def coef(x: float, sig: int = 4) -> str:
    """Coeficiente adimensional sempre na forma  m × 10⁻³  (como no exercício)."""
    m = x * 1e3
    casas = max(sig - 1 - (int(math.floor(math.log10(abs(m)))) if m else 0), 0)
    return f"{m:.{casas}f}".replace(".", "{,}") + r" \times 10^{-3}"


def texto(x: float, sig: int = 4) -> str:
    """Versão em texto simples (para Excel/markdown)."""
    if x == 0 or not math.isfinite(x):
        return str(x)
    exp = int(math.floor(math.log10(abs(x))))
    if -2 <= exp <= 5:
        casas = max(sig - 1 - exp, 0)
        return f"{x:.{casas}f}".replace(".", ",")
    mant = x / 10**exp
    return f"{mant:.{sig - 1}f}".replace(".", ",") + f"e{exp}"


def _cf_latex(linha: str, simb: str, re_str: str, log_str: str, cf_str: str) -> str:
    if linha == "ITTC-1957":
        return _al(rf"{simb} = \dfrac{{0{{,}}075}}{{(\log_{{10}} Re - 2)^2}}",
                   rf"\dfrac{{0{{,}}075}}{{(\log_{{10}} ({re_str}) - 2)^2}}",
                   rf"\dfrac{{0{{,}}075}}{{({log_str} - 2)^2}} = {cf_str}")
    if linha == "Hughes (1954)":
        return _al(rf"{simb} = \dfrac{{0{{,}}066}}{{(\log_{{10}} Re - 2{{,}}03)^2}}",
                   rf"\dfrac{{0{{,}}066}}{{(\log_{{10}} ({re_str}) - 2{{,}}03)^2}}",
                   rf"\dfrac{{0{{,}}066}}{{({log_str} - 2{{,}}03)^2}} = {cf_str}")
    return rf"\dfrac{{0{{,}}242}}{{\sqrt{{{simb}}}}} = \log_{{10}}(Re\,{simb}) \;\Rightarrow\; {simb} = {cf_str}"


def _al(*partes: str) -> str:
    """Expressão em várias linhas alinhadas no sinal de igual."""
    primeira = partes[0].replace("=", "&=", 1)
    corpo = primeira + r" \\ " + r" \\ ".join("&= " + x for x in partes[1:])
    return rf"\begin{{aligned}} {corpo} \end{{aligned}}"


def gerar_memorial(p: Parametros, linha: pd.Series) -> list[Passo]:
    r = linha
    lam = p.escala
    S_s = p.S_s_usada
    P: list[Passo] = []
    A = "Dados e semelhança"
    P.append(Passo(A, "Escala geométrica",
        rf"\lambda = \dfrac{{L_s}}{{L_m}} = \dfrac{{{num(p.L_s)}}}{{{num(p.L_m)}}} = {num(lam)}"))
    if p.S_s is None:
        P.append(Passo(A, "Superfície molhada do navio (escala de Froude)",
            rf"S_s = S_m\,\lambda^2 = {num(p.S_m)} \times ({num(lam)})^2 = {num(S_s)}\ \text{{m}}^2"))
    else:
        P.append(Passo(A, "Superfície molhada do navio (informada)",
            rf"S_s = {num(S_s)}\ \text{{m}}^2 \quad (S_m\lambda^2 = {num(p.S_s_semelhanca)}\ \text{{m}}^2)"))
    P.append(Passo(A, "Velocidade do navio — igualdade de Froude",
        _al(rf"V_s = V_m\sqrt{{\dfrac{{L_s}}{{L_m}}}} = {num(r.V_m)}\sqrt{{{num(lam)}}}",
            rf"{num(r.V_s)}\ \text{{m/s}} = {num(r.V_s_nos)}\ \text{{nós}}")))
    P.append(Passo(A, "Número de Froude",
        rf"Fn = \dfrac{{V_m}}{{\sqrt{{g L_m}}}} = \dfrac{{{num(r.V_m)}}}{{\sqrt{{{num(p.g)} \times {num(p.L_m)}}}}} = {num(r.Fn, 3)} = Fn_s"))
    P.append(Passo(A, "Reynolds do modelo (água do tanque)",
        rf"Re_m = \dfrac{{V_m L_m}}{{\nu_m}} = \dfrac{{{num(r.V_m)} \times {num(p.L_m)}}}{{{num(p.nu_m)}}} = {num(r.Re_m, 3)}"))
    P.append(Passo(A, "Reynolds do navio (água do mar)",
        rf"Re_s = \dfrac{{V_s L_s}}{{\nu_s}} = \dfrac{{{num(r.V_s)} \times {num(p.L_s)}}}{{{num(p.nu_s)}}} = {num(r.Re_s, 3)}"))

    B = "Parte (A) — Método de Froude (sem fator de forma)"
    P.append(Passo(B, "Coeficiente de resistência total do modelo",
        _al(rf"C_{{Tm}} = \dfrac{{R_{{Tm}}}}{{\tfrac12 \rho_m S_m V_m^2}}",
            rf"\dfrac{{{num(r.R_Tm)}}}{{0{{,}}5 \times {num(p.rho_m)} \times {num(p.S_m)} \times {num(r.V_m)}^2}} = {coef(r.C_Tm)}")))
    P.append(Passo(B, f"Atrito do modelo — {p.linha_atrito}",
        _cf_latex(p.linha_atrito, "C_{Fm}", num(r.Re_m, 3), num(math.log10(r.Re_m)), coef(r.C_Fm))))
    P.append(Passo(B, "Resistência residual do modelo",
        _al(r"C_{Rm} = C_{Tm} - C_{Fm}", rf"{coef(r.C_Tm)} - {coef(r.C_Fm)} = {coef(r.C_R)}")))
    P.append(Passo(B, "Hipótese de Froude",
        rf"C_{{Rs}} = C_{{Rm}} = {coef(r.C_R)}"))
    P.append(Passo(B, f"Atrito do navio — {p.linha_atrito}",
        _cf_latex(p.linha_atrito, "C_{Fs}", num(r.Re_s, 3), num(math.log10(r.Re_s)), coef(r.C_Fs))))
    ca = rf" + {coef(p.C_A)}" if p.C_A else ""
    cat = r" + C_A" if p.C_A else ""
    P.append(Passo(B, "Coeficiente total do navio",
        _al(rf"C_{{Ts}} = C_{{Fs}} + C_{{Rs}}{cat}", rf"{coef(r.C_Fs)} + {coef(r.C_R)}{ca} = {coef(r.C_Ts_F)}")))
    P.append(Passo(B, "Resistência total do navio",
        _al(r"R_{Ts} = C_{Ts}\,\tfrac12 \rho_s S_s V_s^2",
            rf"{coef(r.C_Ts_F)} \times 0{{,}}5 \times {num(p.rho_s)} \times {num(S_s)} \times {num(r.V_s)}^2",
            rf"{num(r.R_Ts_F)}\ \text{{N}} = {num(r.R_Ts_F / 1e3)}\ \text{{kN}}")))
    P.append(Passo(B, "Potência efetiva",
        _al(r"P_E = R_{Ts}\,V_s",
            rf"{num(r.R_Ts_F / 1e3)}\ \text{{kN}} \times {num(r.V_s)}\ \text{{m/s}}",
            rf"{num(r.P_E_F / 1e3)}\ \text{{kW}} = {num(r.P_E_F / HP_EM_W)}\ \text{{hp}}")))

    C = "Parte (B) — Método de Hughes (com fator de forma)"
    P.append(Passo(C, "Coeficiente total do modelo (igual à parte A)",
        rf"C_{{Tm}} = {coef(r.C_Tm)} \qquad C_{{Fm}} = {coef(r.C_Fm)}"))
    P.append(Passo(C, "Resistência viscosa do modelo",
        _al(r"C_{Vm} = (1+k)\,C_{Fm}", rf"{num(1 + p.k)} \times {coef(r.C_Fm)} = {coef(r.C_Vm)}")))
    P.append(Passo(C, "Resistência de ondas do modelo",
        _al(r"C_{Wm} = C_{Tm} - C_{Vm}", rf"{coef(r.C_Tm)} - {coef(r.C_Vm)} = {coef(r.C_W)}")))
    P.append(Passo(C, "Hipótese de Hughes",
        rf"C_{{Ws}} = C_{{Wm}} = {coef(r.C_W)}"))
    P.append(Passo(C, "Resistência viscosa do navio",
        _al(r"C_{Vs} = (1+k)\,C_{Fs}", rf"{num(1 + p.k)} \times {coef(r.C_Fs)} = {coef(r.C_Vs)}")))
    P.append(Passo(C, "Coeficiente total do navio",
        _al(rf"C_{{Ts}} = C_{{Vs}} + C_{{Ws}}{cat}", rf"{coef(r.C_Vs)} + {coef(r.C_W)}{ca} = {coef(r.C_Ts_H)}")))
    P.append(Passo(C, "Resistência total do navio",
        _al(r"R_{Ts} = C_{Ts}\,\tfrac12 \rho_s S_s V_s^2",
            rf"{coef(r.C_Ts_H)} \times 0{{,}}5 \times {num(p.rho_s)} \times {num(S_s)} \times {num(r.V_s)}^2",
            rf"{num(r.R_Ts_H)}\ \text{{N}} = {num(r.R_Ts_H / 1e3)}\ \text{{kN}}")))
    P.append(Passo(C, "Potência efetiva",
        _al(r"P_E = R_{Ts}\,V_s",
            rf"{num(r.R_Ts_H / 1e3)}\ \text{{kN}} \times {num(r.V_s)}\ \text{{m/s}}",
            rf"{num(r.P_E_H / 1e3)}\ \text{{kW}} = {num(r.P_E_H / HP_EM_W)}\ \text{{hp}}")))
    return P
