# Extrapolação Modelo → Protótipo

Calcula resistência total e potência efetiva pelos métodos de Froude e Hughes.

## Executar

```bash
pip install -r requirements.txt
streamlit run app.py
```

O aplicativo inicia com dimensões zeradas e tabela de ensaio vazia. Informe os comprimentos do modelo e navio, a superfície molhada do modelo, o fator de forma e os pares de velocidade e resistência. As propriedades da água e a gravidade têm valores iniciais editáveis; confirme os valores para seu ensaio. O botão “Novo ensaio / limpar dados” reinicia as entradas.

As abas incluem dados, resultados, gráficos, memorial, Prohaska, exportação e teoria. Não há casos de exemplo ou comparação com exercícios na interface. Os gráficos ocupam a largura disponível e têm legendas abaixo da área de traçado, com fonte maior e fundo branco. Clique em uma legenda para ocultar ou mostrar uma curva.

Exportação: Excel com fórmulas e CSV. O núcleo de cálculo foi preservado.

## Verificação do código

```bash
python -m pytest -q
```

Os dados de referência ficam somente em `tests/casos_referencia.py`, para verificar regressões nos cálculos; não são carregados pelo aplicativo.
