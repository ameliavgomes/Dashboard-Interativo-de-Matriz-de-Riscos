import pandas as pd
from config import REQUIRED_COLS, OPTIONAL_COLS

def classificar_nivel(score: int) -> str:
    if score >= 15:
        return "Crítico"
    if score >= 10:
        return "Alto"
    if score >= 5:
        return "Médio"
    return "Baixo"

def carregar_e_limpar(arquivo) -> tuple[pd.DataFrame, int]:
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
