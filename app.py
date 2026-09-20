import io
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(page_title="Matriz de Riscos", layout="wide")

# Configuração
REQUIRED_COLS = ["risco", "probabilidade", "impacto"]
OPTIONAL_COLS = ["categoria", "responsavel", "descricao"]

NIVEL_CORES = {
    "Crítico": "#7f1d1d",
    "Alto": "#dc2626",
    "Médio": "#f59e0b",
    "Baixo": "#22c55e",
}

SAMPLE_CSV = """risco,categoria,probabilidade,impacto,responsavel,descricao
Falha no maquinário X,Operacional,4,5,Manutenção,Parada de linha por desgaste de peças críticas
Atraso na logística Y,Logística,3,4,Suprimentos,Fornecedor com histórico de atrasos na entrega
Vazamento de dados de clientes,TI/Segurança,2,5,TI,Sistema legado sem criptografia adequada
Rotatividade da equipe técnica,RH,3,3,RH,Perda de conhecimento operacional
Aumento do preço da matéria-prima,Financeiro,4,3,Compras,Volatilidade cambial impacta insumos importados
Não conformidade regulatória,Compliance,2,5,Jurídico,Mudança recente na legislação do setor
Queda de energia na planta,Operacional,2,4,Manutenção,Rede elétrica instável na região
Erro em relatório financeiro,Financeiro,2,3,Financeiro,Processo manual sujeito a falhas
Acidente de trabalho,Segurança,1,5,SESMT,Uso incorreto de EPI em algumas áreas
Concorrente lança produto similar,Estratégico,3,2,Comercial,Mercado aquecido para o segmento
"""

# Limpeza e preparação dos dados com Pandas
def carregar_e_limpar(arquivo) -> pd.DataFrame:
    df = pd.read_csv(arquivo)
    df.columns = [c.strip().lower() for c in df.columns]

    faltantes = [c for c in REQUIRED_COLS if c not in df.columns]
    if faltantes:
        raise ValueError(
            f"Colunas obrigatórias ausentes: {', '.join(faltantes)}. "
            f"O CSV precisa conter no mínimo: {', '.join(REQUIRED_COLS)}"
        )

    for c in OPTIONAL_COLS:
        if c not in df.columns:
            df[c] = "Não informado"

    df["risco"] = df["risco"].astype(str).str.strip()
    df["categoria"] = df["categoria"].fillna("Não informado").astype(str).str.strip()
    df["responsavel"] = df["responsavel"].fillna("Não informado").astype(str).str.strip()
    df["descricao"] = df["descricao"].fillna("").astype(str).str.strip()

    df["probabilidade"] = pd.to_numeric(df["probabilidade"], errors="coerce")
    df["impacto"] = pd.to_numeric(df["impacto"], errors="coerce")

    antes = len(df)
    df = df.dropna(subset=["probabilidade", "impacto", "risco"])
    removidos = antes - len(df)

    df["probabilidade"] = df["probabilidade"].round().clip(1, 5).astype(int)
    df["impacto"] = df["impacto"].round().clip(1, 5).astype(int)

    df["score"] = df["probabilidade"] * df["impacto"]
    df["nivel"] = df["score"].apply(classificar_nivel)

    df = df.sort_values("score", ascending=False).reset_index(drop=True)
    return df, removidos


def classificar_nivel(score: int) -> str:
    if score >= 15:
        return "Crítico"
    if score >= 10:
        return "Alto"
    if score >= 5:
        return "Médio"
    return "Baixo"


# Matriz de calor com Plotly
def montar_heatmap(df: pd.DataFrame) -> go.Figure:
    grid = np.zeros((5, 5), dtype=int)
    hover_txt = [["" for _ in range(5)] for _ in range(5)]

    for prob in range(1, 6):
        for imp in range(1, 6):
            subset = df[(df["probabilidade"] == prob) & (df["impacto"] == imp)]
            grid[prob - 1, imp - 1] = len(subset)
            if len(subset):
                nomes = "<br>".join(f"• {r}" for r in subset["risco"].head(8))
                extra = "<br>..." if len(subset) > 8 else ""
                hover_txt[prob - 1][imp - 1] = (
                    f"<b>Prob {prob} x Impacto {imp}</b><br>{len(subset)} risco(s):<br>{nomes}{extra}"
                )
            else:
                hover_txt[prob - 1][imp - 1] = f"Prob {prob} x Impacto {imp}<br>Nenhum risco"

    score_grid = np.array([[p * i for i in range(1, 6)] for p in range(1, 6)])

    colorscale = [
        [0.0, "#22c55e"],
        [0.25, "#22c55e"],
        [0.25, "#f59e0b"],
        [0.45, "#f59e0b"],
        [0.45, "#dc2626"],
        [0.65, "#dc2626"],
        [0.65, "#7f1d1d"],
        [1.0, "#7f1d1d"],
    ]

    fig = go.Figure(
        data=go.Heatmap(
            z=score_grid,
            x=[1, 2, 3, 4, 5],
            y=[1, 2, 3, 4, 5],
            colorscale=colorscale,
            showscale=False,
            hoverinfo="text",
            text=hover_txt,
            xgap=3,
            ygap=3,
        )
    )

    annotations = []
    for prob in range(1, 6):
        for imp in range(1, 6):
            count = grid[prob - 1, imp - 1]
            if count > 0:
                annotations.append(
                    dict(
                        x=imp,
                        y=prob,
                        text=f"<b>{count}</b>",
                        showarrow=False,
                        font=dict(color="white", size=18),
                    )
                )

    fig.update_layout(
        title="Matriz de Riscos — Probabilidade x Impacto",
        xaxis=dict(title="Impacto", tickmode="array", tickvals=[1, 2, 3, 4, 5], dtick=1),
        yaxis=dict(title="Probabilidade", tickmode="array", tickvals=[1, 2, 3, 4, 5], dtick=1),
        annotations=annotations,
        height=520,
        margin=dict(l=10, r=10, t=60, b=10),
    )
    return fig

# Interface
st.title("Dashboard de Matriz de Riscos")
st.caption(
    "Faça upload de um CSV de riscos e obtenha automaticamente a Matriz de Riscos "
    "e o relatório dos riscos críticos."
)

with st.sidebar:
    st.header("Dados")
    arquivo = st.file_uploader("Envie o CSV de riscos", type=["csv"])
    st.markdown("**Colunas esperadas:**")
    st.code("risco, probabilidade (1-5), impacto (1-5)\n[opcional] categoria, responsavel, descricao")
    st.download_button(
        "⬇ Baixar CSV de exemplo",
        data=SAMPLE_CSV,
        file_name="riscos_exemplo.csv",
        mime="text/csv",
    )
    usar_exemplo = st.checkbox("Usar dados de exemplo", value=(arquivo is None))

fonte = None
if arquivo is not None:
    fonte = arquivo
elif usar_exemplo:
    fonte = io.StringIO(SAMPLE_CSV)

if fonte is None:
    st.info("⬅ Envie um arquivo CSV na barra lateral (ou marque 'Usar dados de exemplo') para começar.")
    st.stop()

try:
    df, removidos = carregar_e_limpar(fonte)
except ValueError as e:
    st.error(str(e))
    st.stop()

if df.empty:
    st.warning("Nenhum risco válido encontrado após a limpeza dos dados.")
    st.stop()

if removidos:
    st.warning(f"{removidos} linha(s) foram descartadas por dados inválidos/ausentes em probabilidade, impacto ou risco.")

# KPIs
c1, c2, c3, c4 = st.columns(4)
c1.metric("Total de riscos", len(df))
c2.metric("Críticos", int((df["nivel"] == "Crítico").sum()))
c3.metric("Altos", int((df["nivel"] == "Alto").sum()))
c4.metric("Score médio", f"{df['score'].mean():.1f}")

st.divider()

# Matriz de calor
col_heat, col_dist = st.columns([2, 1])
with col_heat:
    st.plotly_chart(montar_heatmap(df), width='stretch')
with col_dist:
    st.subheader("Distribuição por nível")
    contagem = df["nivel"].value_counts().reindex(["Crítico", "Alto", "Médio", "Baixo"]).fillna(0)
    fig_bar = go.Figure(
        go.Bar(
            x=contagem.index,
            y=contagem.values,
            marker_color=[NIVEL_CORES[n] for n in contagem.index],
            text=contagem.values.astype(int),
            textposition="outside",
        )
    )
    fig_bar.update_layout(height=430, margin=dict(l=10, r=10, t=10, b=10), yaxis_title="Qtd. riscos")
    st.plotly_chart(fig_bar, width='stretch')

st.divider()

# Relatório de riscos críticos
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
                """,
                unsafe_allow_html=True,
            )

st.divider()

# Tabela completa e exportação
st.subheader("Base completa de riscos")
st.dataframe(
    df[["risco", "categoria", "probabilidade", "impacto", "score", "nivel", "responsavel", "descricao"]],
    width='stretch',
    hide_index=True,
)

csv_saida = df.to_csv(index=False).encode("utf-8-sig")
st.download_button(
    "⬇ Baixar relatório processado (CSV)",
    data=csv_saida,
    file_name="matriz_de_riscos_processada.csv",
    mime="text/csv",
)
