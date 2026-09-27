"""
Verificações de consistência dos dados de entrada e dos resultados.

Filosofia (a mesma do app de hidrostática):
    DETECTAR → EXPLICAR → AVISAR → MOSTRAR CONSEQUÊNCIAS → O USUÁRIO DECIDE

Nenhuma verificação altera os dados: elas só produzem Avisos. O cálculo
continua sendo feito com o que o usuário informou.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

import numpy as np
import pandas as pd

from .extrapolacao import Parametros

Nivel = Literal["erro", "alerta", "info"]


@dataclass
class Aviso:
    nivel: Nivel
    titulo: str
    explicacao: str
    consequencia: str = ""


def _fmt_idx(idx) -> str:
    return ", ".join(str(i + 1) for i in idx)


def verificar_parametros(p: Parametros) -> list[Aviso]:
    av: list[Aviso] = []
    positivos = {
        "L_m": p.L_m, "S_m": p.S_m, "L_s": p.L_s, "ρ_m": p.rho_m, "ν_m": p.nu_m,
        "ρ_s": p.rho_s, "ν_s": p.nu_s, "g": p.g,
    }
    if p.S_s is not None:
        positivos["S_s"] = p.S_s
    ruins = [n for n, v in positivos.items() if not (v is not None and v > 0)]
    if ruins:
        av.append(Aviso(
            "erro", "Parâmetros não positivos",
            f"Os parâmetros {', '.join(ruins)} precisam ser maiores que zero.",
            "O cálculo não tem significado físico com esses valores.",
        ))
        return av

    if p.escala < 1:
        av.append(Aviso(
            "alerta", "Escala λ < 1",
            f"λ = L_s/L_m = {p.escala:.3f}: o protótipo está menor que o modelo.",
            "Verifique se L_m e L_s não foram trocados.",
        ))

    for nome, nu in (("ν_m", p.nu_m), ("ν_s", p.nu_s)):
        if not (0.5e-6 <= nu <= 2.0e-6):
            av.append(Aviso(
                "alerta", f"{nome} fora da faixa usual da água",
                f"{nome} = {nu:.4g} m²/s. Água entre 0 e 30 °C tem ν ≈ 0,8–1,8 × 10⁻⁶ m²/s.",
                "Um erro de unidade em ν desloca Re e altera C_F — e portanto todos os resultados.",
            ))
    for nome, rho in (("ρ_m", p.rho_m), ("ρ_s", p.rho_s)):
        if not (990 <= rho <= 1035):
            av.append(Aviso(
                "alerta", f"{nome} fora da faixa usual da água",
                f"{nome} = {rho:g} kg/m³ (água doce ≈ 1000, salgada ≈ 1025).",
                "R_T e P_E escalam diretamente com ρ.",
            ))

    if p.S_s is not None:
        ref = p.S_s_semelhanca
        desvio = (p.S_s - ref) / ref * 100
        if abs(desvio) > 1.0:
            av.append(Aviso(
                "alerta", "S_s informada não segue S_m·λ²",
                f"S_s informada = {p.S_s:,.4g} m², mas S_m·λ² = {ref:,.4g} m² "
                f"(desvio de {desvio:+.1f} %).",
                "Pequenas diferenças são normais (apêndices, arredondamento da escala). "
                "Diferenças grandes geralmente indicam erro de digitação ou de unidade "
                "(ex.: 19,592 no lugar de 19592). R_Ts e P_E são proporcionais a S_s.",
            ))

    if not (0.0 <= p.k <= 0.6):
        av.append(Aviso(
            "alerta", "Fator de forma fora da faixa usual",
            f"k = {p.k:g}. Valores típicos: 0,05–0,20 (navios finos) até ~0,4 (cascos cheios).",
            "No método de Hughes, k alto transfere resistência da parcela de ondas "
            "para a viscosa e reduz a potência extrapolada.",
        ))
    if p.C_A != 0:
        av.append(Aviso(
            "info", "Correção C_A ativa",
            f"C_A = {p.C_A:.3e} está sendo somado ao C_Ts nos dois métodos.",
            "O exercício resolvido não usa C_A; para verificação, deixe C_A = 0.",
        ))
    return av


def verificar_dados(V_m, R_Tm) -> list[Aviso]:
    av: list[Aviso] = []
    V_m = np.asarray(V_m, dtype=float)
    R_Tm = np.asarray(R_Tm, dtype=float)
    if V_m.size == 0:
        av.append(Aviso("erro", "Sem dados de ensaio", "Informe ao menos um par (V_m, R_Tm)."))
        return av
    ruins = np.where(~(np.isfinite(V_m) & np.isfinite(R_Tm) & (V_m > 0) & (R_Tm > 0)))[0]
    if ruins.size:
        av.append(Aviso(
            "erro", "Pontos inválidos",
            f"Linha(s) {_fmt_idx(ruins)}: V_m e R_Tm devem ser números positivos.",
            "Essas linhas foram ignoradas no cálculo.",
        ))
    ok = np.isfinite(V_m) & np.isfinite(R_Tm) & (V_m > 0) & (R_Tm > 0)
    v = V_m[ok]
    if v.size != np.unique(v).size:
        av.append(Aviso(
            "info", "Velocidades repetidas",
            "Há velocidades do modelo repetidas (ensaios repetidos?).",
            "As curvas podem apresentar 'zig-zag' nesses pontos.",
        ))
    if v.size > 1 and np.any(np.diff(v) <= 0):
        av.append(Aviso(
            "info", "Velocidades fora de ordem",
            "As velocidades não estão em ordem crescente.",
            "Os gráficos serão traçados com os pontos ordenados por velocidade.",
        ))
    return av


def verificar_resultados(df: pd.DataFrame, p: Parametros) -> list[Aviso]:
    av: list[Aviso] = []
    if df.empty:
        return av
    baixo = np.where(df["Re_m"].to_numpy() < 2.0e6)[0]
    if baixo.size:
        av.append(Aviso(
            "alerta", "Número de Reynolds do modelo baixo",
            f"Linha(s) {_fmt_idx(baixo)} têm Re_m < 2×10⁶.",
            "Pode haver escoamento laminar em parte do casco do modelo; as linhas de "
            "atrito turbulentas (ITTC-57 etc.) superestimam C_Fm e a extrapolação fica menos confiável.",
        ))
    neg_r = np.where(df["C_R"].to_numpy() < 0)[0]
    if neg_r.size:
        av.append(Aviso(
            "erro", "C_R negativo (Froude)",
            f"Linha(s) {_fmt_idx(neg_r)}: C_Tm < C_Fm — a resistência medida é menor que a de atrito de placa plana.",
            "Fisicamente improvável: verifique R_Tm, S_m, V_m, ν_m e a linha de atrito.",
        ))
    neg_w = np.where(df["C_W"].to_numpy() < 0)[0]
    if neg_w.size:
        av.append(Aviso(
            "alerta", "C_W negativo (Hughes)",
            f"Linha(s) {_fmt_idx(neg_w)}: (1+k)·C_Fm > C_Tm, logo C_W < 0.",
            "Costuma ocorrer em Fn baixos quando k está superestimado. O navio receberia "
            "uma 'resistência de ondas' negativa. Considere revisar k (aba Fator de forma — Prohaska).",
        ))
    fn_alto = np.where(df["Fn"].to_numpy() > 0.45)[0]
    if fn_alto.size:
        av.append(Aviso(
            "info", "Fn elevado",
            f"Linha(s) {_fmt_idx(fn_alto)} têm Fn > 0,45 (regime de semi-planeio/planeio).",
            "A hipótese de C_W independente de Re continua valendo, mas efeitos de "
            "trim/afundamento dinâmico tornam a extrapolação 2D/3D menos precisa.",
        ))
    return av
