"""
Estimativa do fator de forma k pelo método de Prohaska (ITTC 7.5-02-02-01).

Hipótese: em baixas velocidades C_W ∝ Fn⁴, logo
    C_T / C_F = (1 + k) + c · Fn⁴ / C_F
Regressão linear de y = C_T/C_F contra x = Fn⁴/C_F:
    intercepto = 1 + k ;  inclinação = c
A ITTC recomenda usar pontos com 0,1 ≤ Fn ≤ 0,2.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass
class ResultadoProhaska:
    um_mais_k: float
    c: float
    r2: float
    n_pontos: int
    x: np.ndarray
    y: np.ndarray
    mascara: np.ndarray  # pontos usados na regressão

    @property
    def k(self) -> float:
        return self.um_mais_k - 1.0


def prohaska(Fn, C_T, C_F, fn_min: float = 0.0, fn_max: float = 0.2) -> ResultadoProhaska:
    Fn = np.asarray(Fn, dtype=float)
    C_T = np.asarray(C_T, dtype=float)
    C_F = np.asarray(C_F, dtype=float)
    x = Fn**4 / C_F
    y = C_T / C_F
    m = (Fn >= fn_min) & (Fn <= fn_max) & np.isfinite(x) & np.isfinite(y)
    n = int(m.sum())
    if n < 3:
        raise ValueError(
            f"Prohaska precisa de pelo menos 3 pontos na faixa {fn_min} ≤ Fn ≤ {fn_max} "
            f"(encontrados: {n})."
        )
    c, a = np.polyfit(x[m], y[m], 1)
    y_hat = a + c * x[m]
    ss_res = float(np.sum((y[m] - y_hat) ** 2))
    ss_tot = float(np.sum((y[m] - y[m].mean()) ** 2))
    r2 = 1.0 - ss_res / ss_tot if ss_tot > 0 else 1.0
    return ResultadoProhaska(float(a), float(c), r2, n, x, y, m)
