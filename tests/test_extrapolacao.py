"""
Testes automáticos do núcleo de cálculo.

Rodar com:  python -m pytest -q
"""

import math

import numpy as np
import pytest

from extrap import Parametros, extrapolar, prohaska, fluidos, coef_atrito
from extrap import verificar_parametros, verificar_resultados, verificar_dados, gerar_memorial
from extrap.casos import EXERCICIO_PDF, RESPOSTAS_PDF, CASO_PLANILHA2


@pytest.fixture
def df_pdf():
    c = EXERCICIO_PDF
    return extrapolar(c["params"], c["V_m"], c["R_Tm"])


# --- 1. Verificação contra o exercício resolvido (PDF) ----------------------
@pytest.mark.parametrize("nome", list(RESPOSTAS_PDF))
def test_confere_com_pdf(df_pdf, nome):
    col, valor_pdf, tol = RESPOSTAS_PDF[nome]
    assert df_pdf[col].iloc[0] == pytest.approx(valor_pdf, rel=tol / 100)


def test_confere_com_planilha1_exata(df_pdf):
    """Valores exatos (sem arredondamento) calculados pela Planilha1 do Excel."""
    r = df_pdf.iloc[0]
    assert r.V_s == pytest.approx(8.215838362577491, rel=1e-12)
    assert r.R_Ts_F == pytest.approx(291783.2771958572, rel=1e-10)
    assert r.R_Ts_H == pytest.approx(260828.2687752358, rel=1e-10)
    assert r.P_E_F == pytest.approx(2397244.242344306, rel=1e-10)
    assert r.P_E_H == pytest.approx(2142922.896648255, rel=1e-10)


# --- 2. Identidades físicas --------------------------------------------------
def test_froude_igual_modelo_navio(df_pdf):
    assert df_pdf.Fn.iloc[0] == pytest.approx(df_pdf.Fn_s.iloc[0], rel=1e-12)


def test_k_zero_hughes_igual_froude():
    c = CASO_PLANILHA2
    p = Parametros(**{**c["params"].__dict__, "k": 0.0})
    df = extrapolar(p, c["V_m"], c["R_Tm"])
    np.testing.assert_allclose(df.P_E_H, df.P_E_F, rtol=1e-12)


def test_mesma_escala_reproduz_modelo():
    """Com λ = 1 e mesma água, o 'navio' é o próprio modelo."""
    p = Parametros(L_m=5, S_m=4, L_s=5, rho_s=1000, nu_s=1.14e-6, k=0.2)
    df = extrapolar(p, [1.0, 1.5], [10.0, 25.0])
    np.testing.assert_allclose(df.R_Ts_F, [10.0, 25.0], rtol=1e-12)
    np.testing.assert_allclose(df.R_Ts_H, [10.0, 25.0], rtol=1e-12)


def test_S_s_por_semelhanca():
    p = EXERCICIO_PDF["params"]
    assert p.S_s_usada == pytest.approx(3375.0)


def test_potencia_monotona_caso_estudo():
    c = CASO_PLANILHA2
    df = extrapolar(c["params"], c["V_m"], c["R_Tm"])
    assert np.all(np.diff(df.P_E_F) > 0)
    assert np.all(np.diff(df.P_E_H) > 0)


# --- 3. Linhas de atrito e fluidos ---------------------------------------------
def test_schoenherr_satisfaz_equacao():
    re = np.array([1e6, 1e7, 1e9])
    cf = coef_atrito(re, "Schoenherr (ATTC-1947)")
    np.testing.assert_allclose(0.242 / np.sqrt(cf), np.log10(re * cf), rtol=1e-10)


def test_linha_desconhecida():
    with pytest.raises(ValueError):
        coef_atrito(1e7, "inventada")


def test_propriedades_agua_15C():
    assert fluidos.nu_agua_doce(15) == pytest.approx(1.1394e-6, rel=1e-3)
    assert fluidos.nu_agua_salgada(15) == pytest.approx(1.1873e-6, rel=1e-3)
    assert fluidos.rho_agua_doce(15) == pytest.approx(999.1, abs=0.5)
    assert fluidos.rho_agua_salgada(15) == pytest.approx(1026.0, abs=0.5)


# --- 4. Prohaska ---------------------------------------------------------------
def test_prohaska_recupera_k_sintetico():
    k, c = 0.18, 25.0
    Fn = np.linspace(0.08, 0.2, 8)
    CF = coef_atrito(Fn * 3e7, "ITTC-1957")
    CT = (1 + k) * CF + c * Fn**4
    r = prohaska(Fn, CT, CF)
    assert r.k == pytest.approx(k, abs=1e-9)
    assert r.c == pytest.approx(c, rel=1e-6)
    assert r.r2 == pytest.approx(1.0)


def test_prohaska_poucos_pontos():
    with pytest.raises(ValueError):
        prohaska([0.1, 0.12], [4e-3, 4e-3], [3e-3, 3e-3])


# --- 5. Verificações (DETECTAR → AVISAR) ---------------------------------------
def test_detecta_S_s_digitada_errada():
    p = Parametros(**{**CASO_PLANILHA2["params"].__dict__, "S_s": 19.592})
    titulos = [a.titulo for a in verificar_parametros(p)]
    assert any("S_s" in t for t in titulos)


def test_S_s_correta_sem_aviso():
    titulos = [a.titulo for a in verificar_parametros(CASO_PLANILHA2["params"])]
    assert not any("S_s" in t for t in titulos)


def test_detecta_nu_em_unidade_errada():
    p = Parametros(L_m=4.3, S_m=3.75, L_s=129, nu_m=1.14)
    assert any("ν_m" in a.titulo for a in verificar_parametros(p))


def test_detecta_CW_negativo():
    p = Parametros(L_m=4.3, S_m=3.75, L_s=129, k=0.6)
    df = extrapolar(p, [1.5], [18.0])
    assert any("C_W negativo" in a.titulo for a in verificar_resultados(df, p))


def test_dados_invalidos():
    av = verificar_dados([1.0, -1.0], [10.0, 5.0])
    assert any(a.nivel == "erro" for a in av)


# --- 6. Memorial ---------------------------------------------------------------
def test_memorial_tem_as_duas_partes(df_pdf):
    passos = gerar_memorial(EXERCICIO_PDF["params"], df_pdf.iloc[0])
    secoes = {p.secao for p in passos}
    assert any("Froude" in s for s in secoes) and any("Hughes" in s for s in secoes)
    assert any("291{,}8" in p.latex for p in passos)   # R_Ts (A) em kN
