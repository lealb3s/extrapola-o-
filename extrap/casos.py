"""
Casos pré-carregados.

- EXERCICIO_PDF: exercício resolvido anexo à AP1 (modelo 4,3 m → navio 129 m).
- CASO_PLANILHA2: dados de ensaio do caso de estudo lançados na Planilha2 do
  arquivo ap1_hidro.xlsx (modelo 6,9541 m → navio 280 m). Preencha a
  referência bibliográfica na interface.
"""

from __future__ import annotations

from .extrapolacao import Parametros

EXERCICIO_PDF = {
    "nome": "Exercício resolvido (PDF da AP1)",
    "referencia": "Exercício de extrapolação — 2 métodos (material da disciplina)",
    "params": Parametros(
        L_m=4.3, S_m=3.75, rho_m=1000.0, nu_m=1.140e-6,
        L_s=129.0, S_s=None, rho_s=1025.0, nu_s=1.190e-6,
        k=0.15,
    ),
    "V_m": [1.5],
    "R_Tm": [18.0],
}

# Valores publicados no PDF (resolvidos à mão, com arredondamentos intermediários)
RESPOSTAS_PDF = {
    "V_s [m/s]": ("V_s", 8.22, 1.0),
    "Fn": ("Fn", 0.23, 1.0),
    "Re_m": ("Re_m", 5.66e6, 1.0),
    "Re_s": ("Re_s", 8.91e8, 1.0),
    "C_Tm": ("C_Tm", 4.267e-3, 1.0),
    "C_Fm": ("C_Fm", 3.32e-3, 1.0),
    "C_Rm (A)": ("C_R", 0.947e-3, 1.0),
    "C_Fs": ("C_Fs", 1.553e-3, 1.0),
    "C_Ts (A)": ("C_Ts_F", 2.5e-3, 1.0),
    "R_Ts (A) [kN]": ("R_Ts_F_kN", 292.18, 1.0),
    "P_E (A) [kW]": ("P_E_F_kW", 2401.7, 1.0),
    "P_E (A) [hp]": ("P_E_F_hp", 3221.0, 1.0),
    "C_Vm (B)": ("C_Vm", 3.818e-3, 1.0),
    "C_Wm (B)": ("C_W", 0.449e-3, 1.0),
    "C_Vs (B)": ("C_Vs", 1.786e-3, 1.0),
    "C_Ts (B)": ("C_Ts_H", 2.235e-3, 1.0),
    "R_Ts (B) [kN]": ("R_Ts_H_kN", 261.2, 1.0),
    "P_E (B) [kW]": ("P_E_H_kW", 2147.1, 1.0),
    "P_E (B) [hp]": ("P_E_H_hp", 2879.0, 1.0),
}  # nome: (coluna, valor do PDF, tolerância relativa em %)

CASO_PLANILHA2 = {
    "nome": "Caso de estudo (dados da Planilha2)",
    "referencia": "",
    "params": Parametros(
        L_m=6.9541, S_m=12.0848, rho_m=1000.0, nu_m=1.140e-6,
        L_s=280.0, S_s=19592.0, rho_s=1025.0, nu_s=1.190e-6,
        k=0.2988,
    ),
    "V_m": [0.73, 0.809, 0.89, 0.97, 1.049, 1.13, 1.221, 1.30, 1.38, 1.46],
    "R_Tm": [15.13, 18.318, 21.876, 25.682, 29.707, 34.099, 39.466, 45.079, 51.841, 59.74],
}

EM_BRANCO = {
    "nome": "Novo caso (em branco)",
    "referencia": "",
    "params": Parametros(L_m=5.0, S_m=5.0, L_s=100.0, k=0.15),
    "V_m": [1.0, 1.2, 1.4],
    "R_Tm": [10.0, 15.0, 22.0],
}

CASOS = {c["nome"]: c for c in (EXERCICIO_PDF, CASO_PLANILHA2, EM_BRANCO)}
