"""
Linhas de atrito (coeficiente de resistência friccional de placa plana, C_F).

- ITTC-1957 (linha de correlação modelo-navio) — usada no exercício:
      C_F = 0,075 / (log10 Re − 2)²
- Hughes (1954):
      C_F0 = 0,066 / (log10 Re − 2,03)²
- Schoenherr / ATTC (1947), implícita:
      0,242 / √C_F = log10(Re · C_F)
"""

from __future__ import annotations

import numpy as np

LINHAS = {
    "ITTC-1957": r"C_F = \dfrac{0{,}075}{(\log_{10} Re - 2)^2}",
    "Hughes (1954)": r"C_F = \dfrac{0{,}066}{(\log_{10} Re - 2{,}03)^2}",
    "Schoenherr (ATTC-1947)": r"\dfrac{0{,}242}{\sqrt{C_F}} = \log_{10}(Re\,C_F)",
}


def cf_ittc57(re):
    re = np.asarray(re, dtype=float)
    return 0.075 / (np.log10(re) - 2.0) ** 2


def cf_hughes(re):
    re = np.asarray(re, dtype=float)
    return 0.066 / (np.log10(re) - 2.03) ** 2


def cf_schoenherr(re, tol: float = 1e-12, max_iter: int = 100):
    """Resolve 0,242/√CF = log10(Re·CF) por Newton-Raphson (vetorizado)."""
    re = np.asarray(re, dtype=float)
    cf = cf_ittc57(re)  # chute inicial muito próximo
    for _ in range(max_iter):
        f = 0.242 / np.sqrt(cf) - np.log10(re * cf)
        df = -0.121 * cf ** -1.5 - 1.0 / (cf * np.log(10.0))
        passo = f / df
        cf = cf - passo
        if np.all(np.abs(passo) < tol):
            break
    return cf


_FUNCOES = {
    "ITTC-1957": cf_ittc57,
    "Hughes (1954)": cf_hughes,
    "Schoenherr (ATTC-1947)": cf_schoenherr,
}


def coef_atrito(re, linha: str = "ITTC-1957"):
    try:
        return _FUNCOES[linha](re)
    except KeyError as exc:
        raise ValueError(f"linha de atrito desconhecida: {linha!r}") from exc
