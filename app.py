import io
import streamlit as st
from config import SAMPLE_CSV, NIVEL_CORES
from dados import carregar_e_limpar
from graficos import montar_heatmap, montar_grafico_barras

st.set_page_config(page_title="Matriz de Riscos", layout="wide", page_icon="🛡️")

st.title("Dashboard de Matriz de Riscos")
st.caption("Faça upload de um CSV de riscos e obtenha a Matriz de Riscos e relatórios automaticamente.")

# Sidebar
with st.sidebar:
    st.header("📁 Dados")
    arquivo = st.file_uploader("Envie o CSV de riscos", type=["csv"])
    st.markdown("**Colunas esperadas:**")
    st.code("risco, probabilidade (1-5), impacto (1-5)\n[opcional] categoria, responsavel, descricao")
    st.download_button("⬇ Baixar CSV de exemplo", data=SAMPLE_CSV, file_name="riscos_exemplo.csv", mime="text/csv")
    usar_exemplo = st.checkbox("Usar dados de exemplo", value=(arquivo is None))

fonte = arquivo if arquivo is not None else (io.StringIO(SAMPLE_CSV) if usar_exemplo else None)

if fonte is None:
    st.info("⬅ Envie um arquivo CSV na barra lateral (ou marque 'Usar dados de exemplo') para começar.")
    st.stop()

# Carregamento e Tratamento de Erros
try:
    df, removidos = carregar_e_limpar(fonte)
except ValueError as e:
    st.error(str(e))
    st.stop()

if df.empty:
    st.warning("Nenhum risco válido encontrado após a limpeza dos dados.")
    st.stop()

if removidos:
    st.warning(f"{removidos} linha(s) descartada(s) por dados inválidos em probabilidade, impacto ou risco.")

# KPIs
c1, c2, c3, c4 = st.columns(4)
c1.metric("Total de riscos", len(df))
c2.metric("Críticos", int((df["nivel"] == "Crítico").sum()))
c3.metric("Altos", int((df["nivel"] == "Alto").sum()))
c4.metric("Score médio", f"{df['score'].mean():.1f}")

st.divider()

# Gráficos
col_heat, col_dist = st.columns([2, 1])
with col_heat:
    st.plotly_chart(montar_heatmap(df), width="stretch")
with col_dist:
    st.subheader("Distribuição por nível")
    st.plotly_chart(montar_grafico_barras(df), width="stretch")

st.divider()

# Relatório Crítico
st.subheader("Relatório de Riscos Críticos e Altos")
criticos = df[df["nivel"].isin(["Crítico", "Alto"])]

if criticos.empty:
    st.success("Nenhum risco crítico ou alto identificado. 🎉")
else:
    for _, row in criticos.iterrows():
        cor = NIVEL_CORES[row["nivel"]]
        with st.container():
            st.markdown(
                f"""
                <div style="border-left:6px solid {cor}; padding:10px 16px; margin-bottom:10px; background-color:rgba(0,0,0,0.03); border-radius:6px;">
                    <b>{row['risco']}</b> — <span style="color:{cor}; font-weight:600;">{row['nivel']} (score {row['score']})</span><br>
                    <small>Categoria: {row['categoria']} · Responsável: {row['responsavel']} · Prob: {row['probabilidade']} · Impacto: {row['impacto']}</small><br>
                    {f"<span>{row['descricao']}</span>" if row['descricao'] else ""}
                </div>
                """, unsafe_allow_html=True
            )

st.divider()

# Tabela Completa
st.subheader("Base completa de riscos")
st.dataframe(
    df[["risco", "categoria", "probabilidade", "impacto", "score", "nivel", "responsavel", "descricao"]],
    width="stretch",
    hide_index=True,
)

csv_saida = df.to_csv(index=False).encode("utf-8-sig")
st.download_button("⬇ Baixar relatório processado (CSV)", data=csv_saida, file_name="matriz_processada.csv", mime="text/csv")
