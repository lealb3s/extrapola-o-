"""Aba com o resumo teórico (mesma notação do exercício resolvido)."""

import streamlit as st


def mostrar() -> None:
    c1, c2 = st.columns(2, gap="large")
    with c1:
        st.markdown("### Método de Froude (2D)")
        st.markdown("A resistência é dividida em atrito de placa plana e um resíduo:")
        st.latex(r"C_T = C_F + C_R")
        st.markdown("- $C_F$: resistência de atrito (*skin friction*), de uma linha de placa plana  \n"
                    "- $C_R$: resistência residual (\"o que sobra\"), suposta função **só de Fn**")
        st.latex(r"C_{Rs} = C_{Rm} = C_{Tm} - C_{Fm} \qquad C_{Ts} = C_{Fs} + C_{Rs}")
    with c2:
        st.markdown("### Método de Hughes (3D)")
        st.markdown("A parte viscosa inclui o efeito de forma do casco via fator de forma $k$:")
        st.latex(r"C_T = (1+k)\,C_F + C_W = C_V + C_W")
        st.markdown("- $C_V$: coeficiente viscoso (atrito + pressão viscosa), escala com **Re**  \n"
                    "- $C_W$: resistência de ondas, suposta função **só de Fn**")
        st.latex(r"C_{Ws} = C_{Wm} = C_{Tm} - (1+k)C_{Fm} \qquad C_{Ts} = (1+k)C_{Fs} + C_{Ws}")

    st.markdown("### Etapas comuns")
    st.latex(r"\lambda = \frac{L_s}{L_m} \qquad S_s = S_m\lambda^2 \qquad "
             r"Fn_m = Fn_s \Rightarrow V_s = V_m\sqrt{\lambda}")
    st.latex(r"Re = \frac{V L}{\nu} \qquad C_T = \frac{R_T}{\tfrac12\rho S V^2} \qquad "
             r"C_F^{ITTC\text{-}57} = \frac{0{,}075}{(\log_{10} Re - 2)^2}")
    st.latex(r"R_{Ts} = C_{Ts}\,\tfrac12\rho_s S_s V_s^2 \qquad P_E = R_{Ts}\,V_s")
    st.markdown(
        "**Por que os resultados diferem?** Como $C_F$ diminui com Re, a parcela que escala com Re é "
        "maior em Hughes ($(1+k)C_F$) do que em Froude ($C_F$). Assim a parcela transportada sem "
        "correção ($C_W < C_R$) é menor e, em geral, $P_E^{Hughes} < P_E^{Froude}$ — mas não sempre.  \n\n"
        "**Fator de forma:** pode vir da literatura, de fórmulas empíricas (ex.: Holtrop) ou do "
        "método de Prohaska, disponível na aba *Fator de forma*.  \n\n"
        "**Unidades:** 1 nó = 0,514444 m/s; 1 hp = 745,7 W (1 kW = 1,341 hp)."
    )
