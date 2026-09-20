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
