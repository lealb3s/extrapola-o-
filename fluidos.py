"""
Propriedades da água (ITTC 7.5-02-01-03, "Fresh Water and Seawater Properties").

As correlações abaixo são as aproximações polinomiais da ITTC, válidas
aproximadamente entre 0 °C e 30 °C (água salgada com salinidade 3,5 %).

Na prática do exercício resolvido usa-se diretamente:
    água doce  (tanque, 15 °C): ν = 1,140e-6 m²/s ; ρ = 1000 kg/m³
    água salgada (mar, 15 °C):  ν = 1,190e-6 m²/s ; ρ = 1025 kg/m³
"""

from __future__ import annotations

FAIXA_VALIDA_T = (0.0, 30.0)


def nu_agua_doce(t: float) -> float:
    """Viscosidade cinemática da água doce [m²/s] para temperatura t [°C]."""
    x = t - 12.0
    return ((0.585e-3 * x - 0.03361) * x + 1.2350) * 1e-6


def nu_agua_salgada(t: float) -> float:
    """Viscosidade cinemática da água salgada [m²/s] para temperatura t [°C]."""
    x = t - 1.0
    return ((0.659e-3 * x - 0.05076) * x + 1.7688) * 1e-6


def rho_agua_doce(t: float) -> float:
    """Massa específica da água doce [kg/m³] para temperatura t [°C]."""
    return 1000.1 + 0.0552 * t - 0.0077 * t**2 + 0.00004 * t**3


def rho_agua_salgada(t: float) -> float:
    """Massa específica da água salgada [kg/m³] para temperatura t [°C]."""
    return 1028.14 - 0.0735 * t - 0.00469 * t**2


def propriedades(tipo: str, t: float) -> tuple[float, float]:
    """Retorna (ρ, ν) para tipo 'doce' ou 'salgada'."""
    if tipo == "doce":
        return rho_agua_doce(t), nu_agua_doce(t)
    if tipo == "salgada":
        return rho_agua_salgada(t), nu_agua_salgada(t)
    raise ValueError(f"tipo de água desconhecido: {tipo!r}")
