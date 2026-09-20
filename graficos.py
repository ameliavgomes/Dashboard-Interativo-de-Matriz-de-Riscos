import pandas as pd
import numpy as np
import plotly.graph_objects as go
from config import NIVEL_CORES

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
        [0.0, "#22c55e"], [0.25, "#22c55e"],
        [0.25, "#f59e0b"], [0.45, "#f59e0b"],
        [0.45, "#dc2626"], [0.65, "#dc2626"],
        [0.65, "#7f1d1d"], [1.0, "#7f1d1d"],
    ]

    fig = go.Figure(
        data=go.Heatmap(
            z=score_grid, x=[1, 2, 3, 4, 5], y=[1, 2, 3, 4, 5],
            colorscale=colorscale, showscale=False, hoverinfo="text",
            text=hover_txt, xgap=3, ygap=3,
        )
    )

    annotations = []
    for prob in range(1, 6):
        for imp in range(1, 6):
            count = grid[prob - 1, imp - 1]
            if count > 0:
                annotations.append(
                    dict(x=imp, y=prob, text=f"<b>{count}</b>", showarrow=False, font=dict(color="white", size=18))
                )

    fig.update_layout(
        title="Matriz de Riscos — Probabilidade x Impacto",
        xaxis=dict(title="Impacto", tickmode="array", tickvals=[1, 2, 3, 4, 5], dtick=1),
        yaxis=dict(title="Probabilidade", tickmode="array", tickvals=[1, 2, 3, 4, 5], dtick=1),
        annotations=annotations, height=520, margin=dict(l=10, r=10, t=60, b=10),
    )
    return fig


def montar_grafico_barras(df: pd.DataFrame) -> go.Figure:
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
    return fig_bar
