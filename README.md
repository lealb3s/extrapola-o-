# 🚢 Extrapolação Modelo → Protótipo (Froude e Hughes)

Aplicativo Streamlit da **AP1 — Questão 1 (ponto bônus)**: calcula a resistência total ao avanço e a
potência efetiva do navio a partir do ensaio de reboque do modelo, pelos métodos de **Froude**
(sem fator de forma) e **Hughes** (com fator de forma *k*), para várias velocidades.

## Como rodar

```bash
pip install -r requirements.txt
streamlit run app.py
```

Testes automáticos (36 testes, incluindo a conferência com o exercício resolvido):

```bash
python -m pytest -q
```

Deploy no Streamlit Community Cloud: suba a pasta para um repositório no GitHub e aponte o app
para `app.py` (o `requirements.txt` já está pronto).

## Estrutura

```
app.py                 → ponto de entrada (monta a página e as abas)
extrap/                → núcleo de cálculo, sem Streamlit (testável isoladamente)
  extrapolacao.py      → Froude e Hughes, vetorizado para N velocidades
  atrito.py            → linhas ITTC-1957, Hughes (1954) e Schoenherr
  fluidos.py           → ρ e ν da água doce/salgada pela temperatura (ITTC 7.5-02-01-03)
  prohaska.py          → estimativa de k pelo método de Prohaska
  validacao.py         → DETECTAR → EXPLICAR → AVISAR → CONSEQUÊNCIAS
  memorial.py          → passo a passo em LaTeX (mesmo roteiro do exercício)
  exportar.py          → planilha .xlsx com FÓRMULAS e gráficos nativos do Excel
  casos.py             → exercício do PDF, caso de estudo (Planilha2) e caso em branco
interface/             → camada Streamlit (barra lateral, abas, gráficos Plotly, teoria)
tests/                 → pytest
```

## Abas

| Aba | Conteúdo |
|---|---|
| Dados do ensaio | tabela editável (V_m, R_Tm) + nome, referência, características e imagem do modelo |
| Resultados | verificações automáticas, resumo e tabelas (modelo, Froude, Hughes, comparação) |
| Gráficos | R_Ts e P_E × Fn (ou V_s em nós/m·s), coeficientes, C_R × C_W, diferença entre métodos |
| Memorial de cálculo | procedimento completo para uma velocidade, com números substituídos + diagrama C × Re |
| Verificação (exercício) | roda o exercício do PDF e compara 19 grandezas com a resolução à mão |
| Fator de forma (Prohaska) | regressão C_T/C_F × Fn⁴/C_F; botão para usar o k estimado |
| Exportar | .xlsx com fórmulas (recalcula ao mudar as entradas) e .csv com todos os resultados |
| Teoria | resumo das equações |

## Verificação

Com os dados do exercício (L_m = 4,3 m, S_m = 3,75 m², V_m = 1,5 m/s, R_Tm = 18 N, L_s = 129 m,
k = 0,15, ITTC-1957):

| | App | PDF (à mão) |
|---|---|---|
| R_Ts Froude | 291,78 kN | 292,18 kN |
| P_E Froude | 2397,2 kW / 3215 hp | 2401,7 kW / 3221 hp |
| R_Ts Hughes | 260,83 kN | 261,2 kN |
| P_E Hughes | 2142,9 kW / 2874 hp | 2147,1 kW / 2879 hp |

Diferenças < 0,5 %, causadas pelos arredondamentos intermediários do PDF (ex.: V_s = 8,22 m/s em vez
de 8,2158 m/s). Com valores exatos o app reproduz a Planilha1 até a 10ª casa decimal.

Unidades: 1 nó = 0,514444 m/s; 1 hp = 745,7 W (1 kW = 1,341 hp).
