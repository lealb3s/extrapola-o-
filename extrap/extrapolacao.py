"""
Extrapolação modelo → protótipo pelos métodos de Froude (2D) e Hughes (3D).

Método de Froude (sem fator de forma):
    C_T = C_F + C_R          C_Rs = C_Rm

Método de Hughes (com fator de forma k):
    C_T = (1 + k)·C_F + C_W  C_Ws = C_Wm

Em ambos:
    Fn_m = Fn_s  →  V_s = V_m·√λ ,  λ = L_s / L_m
    S_s = S_m·λ² (semelhança geométrica)
    R_Ts = C_Ts · ½ ρ_s S_s V_s²
    P_E  = R_Ts · V_s

Opcionalmente soma-se uma correção de correlação/rugosidade C_A ao C_Ts
(o exercício resolvido usa C_A = 0).
"""

from __future__ import annotations

from dataclasses import dataclass, asdict, field
from typing import Optional

import numpy as np
import pandas as pd

from .atrito import coef_atrito

NO_EM_MS = 0.514444  # 1 nó = 0,514444 m/s
HP_EM_W = 745.6999   # 1 hp (mecânico) = 745,7 W  →  1 kW = 1,341 hp
G_PADRAO = 9.81


@dataclass
class Parametros:
    # Modelo
    L_m: float
    S_m: float
    rho_m: float = 1000.0
    nu_m: float = 1.140e-6
    # Protótipo
    L_s: float = 100.0
    S_s: Optional[float] = None   # None → S_m·λ²
    rho_s: float = 1025.0
    nu_s: float = 1.190e-6
    # Método
    k: float = 0.15
    g: float = G_PADRAO
    linha_atrito: str = "ITTC-1957"
    C_A: float = 0.0

    @property
    def escala(self) -> float:
        return self.L_s / self.L_m

    @property
    def S_s_semelhanca(self) -> float:
        return self.S_m * self.escala**2

    @property
    def S_s_usada(self) -> float:
        return self.S_s if self.S_s is not None else self.S_s_semelhanca

    def como_dict(self) -> dict:
        d = asdict(self)
        d["escala"] = self.escala
        d["S_s_usada"] = self.S_s_usada
        return d


def extrapolar(p: Parametros, V_m, R_Tm) -> pd.DataFrame:
    """
    Calcula todas as grandezas intermediárias e finais para cada par (V_m, R_Tm).

    Retorna um DataFrame com uma linha por velocidade do modelo.
    Unidades SI: m/s, N, W.
    """
    V_m = np.atleast_1d(np.asarray(V_m, dtype=float))
    R_Tm = np.atleast_1d(np.asarray(R_Tm, dtype=float))
    if V_m.shape != R_Tm.shape:
        raise ValueError("V_m e R_Tm devem ter o mesmo número de pontos")

    lam = p.escala
    S_s = p.S_s_usada

    # --- Modelo --------------------------------------------------------------
    Fn = V_m / np.sqrt(p.g * p.L_m)
    Re_m = V_m * p.L_m / p.nu_m
    C_Tm = R_Tm / (0.5 * p.rho_m * p.S_m * V_m**2)
    C_Fm = coef_atrito(Re_m, p.linha_atrito)

    # --- Semelhança de Froude -------------------------------------------------
    V_s = V_m * np.sqrt(lam)
    Fn_s = V_s / np.sqrt(p.g * p.L_s)
    Re_s = V_s * p.L_s / p.nu_s
    C_Fs = coef_atrito(Re_s, p.linha_atrito)
    q_s = 0.5 * p.rho_s * S_s * V_s**2  # pressão dinâmica × área [N]

    # --- (a) Froude ---------------------------------------------------------
    C_R = C_Tm - C_Fm
    C_Ts_F = C_Fs + C_R + p.C_A
    R_Ts_F = C_Ts_F * q_s
    P_E_F = R_Ts_F * V_s

    # --- (b) Hughes ---------------------------------------------------------
    C_Vm = (1.0 + p.k) * C_Fm
    C_W = C_Tm - C_Vm
    C_Vs = (1.0 + p.k) * C_Fs
    C_Ts_H = C_Vs + C_W + p.C_A
    R_Ts_H = C_Ts_H * q_s
    P_E_H = R_Ts_H * V_s

    df = pd.DataFrame(
        {
            "V_m": V_m,
            "R_Tm": R_Tm,
            "Fn": Fn,
            "Re_m": Re_m,
            "C_Tm": C_Tm,
            "C_Fm": C_Fm,
            "V_s": V_s,
            "V_s_nos": V_s / NO_EM_MS,
            "Fn_s": Fn_s,
            "Re_s": Re_s,
            "C_Fs": C_Fs,
            # Froude
            "C_R": C_R,
            "C_Ts_F": C_Ts_F,
            "R_Ts_F": R_Ts_F,
            "P_E_F": P_E_F,
            # Hughes
            "C_Vm": C_Vm,
            "C_W": C_W,
            "C_Vs": C_Vs,
            "C_Ts_H": C_Ts_H,
            "R_Ts_H": R_Ts_H,
            "P_E_H": P_E_H,
        }
    )
    df["P_E_F_kW"] = df["P_E_F"] / 1e3
    df["P_E_H_kW"] = df["P_E_H"] / 1e3
    df["P_E_F_hp"] = df["P_E_F"] / HP_EM_W
    df["P_E_H_hp"] = df["P_E_H"] / HP_EM_W
    df["R_Ts_F_kN"] = df["R_Ts_F"] / 1e3
    df["R_Ts_H_kN"] = df["R_Ts_H"] / 1e3
    # diferença relativa Hughes vs Froude
    df["dif_%"] = (df["P_E_H"] - df["P_E_F"]) / df["P_E_F"] * 100.0
    return df


# Nomes amigáveis para exibição --------------------------------------------------
ROTULOS = {
    "V_m": "V_m [m/s]",
    "R_Tm": "R_Tm [N]",
    "Fn": "Fn [-]",
    "Re_m": "Re_m [-]",
    "C_Tm": "C_Tm",
    "C_Fm": "C_Fm",
    "V_s": "V_s [m/s]",
    "V_s_nos": "V_s [nós]",
    "Fn_s": "Fn_s [-]",
    "Re_s": "Re_s [-]",
    "C_Fs": "C_Fs",
    "C_R": "C_R (=C_Rm=C_Rs)",
    "C_Ts_F": "C_Ts Froude",
    "R_Ts_F_kN": "R_Ts Froude [kN]",
    "P_E_F_kW": "P_E Froude [kW]",
    "P_E_F_hp": "P_E Froude [hp]",
    "C_Vm": "C_Vm = (1+k)C_Fm",
    "C_W": "C_W (=C_Wm=C_Ws)",
    "C_Vs": "C_Vs = (1+k)C_Fs",
    "C_Ts_H": "C_Ts Hughes",
    "R_Ts_H_kN": "R_Ts Hughes [kN]",
    "P_E_H_kW": "P_E Hughes [kW]",
    "P_E_H_hp": "P_E Hughes [hp]",
    "dif_%": "ΔP_E Hughes−Froude [%]",
}
