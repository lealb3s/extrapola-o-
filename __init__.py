"""Núcleo de cálculo: extrapolação modelo-protótipo (Froude e Hughes)."""

from .extrapolacao import Parametros, extrapolar, ROTULOS, NO_EM_MS, HP_EM_W
from .atrito import coef_atrito, LINHAS
from .prohaska import prohaska
from .validacao import verificar_parametros, verificar_dados, verificar_resultados, Aviso
from .memorial import gerar_memorial
from . import fluidos

__all__ = [
    "Parametros", "extrapolar", "ROTULOS", "NO_EM_MS", "HP_EM_W",
    "coef_atrito", "LINHAS", "prohaska",
    "verificar_parametros", "verificar_dados", "verificar_resultados", "Aviso",
    "gerar_memorial", "fluidos", "casos",
]
