# Dashboard Interativo de Matriz de Riscos

## Sobre o projeto

Este projeto é uma aplicação web que automatiza o processo de classificação e priorização de riscos corporativos. O usuário faz o upload de uma planilha CSV com a lista de riscos mapeados e o sistema realiza a limpeza dos dados, calcula o score de criticidade, plota automaticamente a Matriz de Riscos (gráfico de calor) e gera um relatório dos riscos que exigem tratamento imediato.

O objetivo é substituir o controle manual em planilhas por uma ferramenta reproduzível, visual e auditável de gestão de riscos.

## Problema

A gestão de riscos depende de classificar o que pode dar errado com base em duas dimensões: **Probabilidade** (qual a chance de acontecer) e **Impacto** (qual o tamanho do prejuízo).

Na prática, esse controle costuma ser feito em planilhas Excel manuais, o que gera três problemas:

- A matriz precisa ser redesenhada manualmente a cada atualização
- A classificação de criticidade fica sujeita a erro humano e critério inconsistente
- Não há relatório automático destacando o que realmente precisa de ação

Este projeto resolve isso: a partir do CSV bruto, toda a classificação, visualização e priorização é gerada automaticamente.

## Dados de entrada

A aplicação recebe um arquivo **CSV** com a lista de riscos mapeados pela organização.

**Colunas obrigatórias:**

| Coluna          | Tipo    | Descrição                                     |
| --------------- | ------- | --------------------------------------------- |
| `risco`         | texto   | Nome ou descrição curta do risco              |
| `probabilidade` | 1 a 5   | 1 = raro · 5 = quase certo                    |
| `impacto`       | 1 a 5   | 1 = insignificante · 5 = catastrófico         |

**Colunas opcionais** (usadas se presentes, ignoradas se ausentes):

| Coluna        | Descrição                                  |
| ------------- | ------------------------------------------ |
| `categoria`   | Natureza do risco (Operacional, TI, etc.)  |
| `responsavel` | Área ou pessoa responsável pelo tratamento |
| `descricao`   | Detalhamento do cenário de risco           |

Um arquivo `riscos_exemplo.csv` está incluído no projeto e também pode ser baixado diretamente pela barra lateral da aplicação.

## Tecnologias

- Python
- Pandas
- NumPy
- Plotly
- Streamlit

## Estrutura do projeto

```
risk_matrix_app/
│
├── app.py                  # Aplicação Streamlit (interface + lógica)
├── riscos_exemplo.csv      # Dataset de exemplo para teste
├── requirements.txt        # Dependências do projeto
└── README.md
```

## Metodologia

```
CSV de riscos (upload)
     ↓
Validação de colunas obrigatórias
     ↓
Limpeza e tipagem dos dados
     ↓
Cálculo do score (Probabilidade × Impacto)
     ↓
Classificação por nível de criticidade
     ↓
Visualização (Matriz de Riscos + distribuição)
     ↓
Relatório de riscos críticos
     ↓
Exportação da base processada
```

## Funcionalidades

### Limpeza e validação dos dados

Antes de qualquer cálculo, a base passa por um tratamento com Pandas:

- Normalização dos nomes das colunas (minúsculas, sem espaços extras)
- Verificação das colunas obrigatórias, com erro explícito se faltar alguma
- Criação automática das colunas opcionais ausentes
- Conversão de `probabilidade` e `impacto` para numérico, com `errors="coerce"`
- Descarte de linhas com dados inválidos, informando ao usuário quantas foram removidas
- Arredondamento e limitação dos valores à escala válida de 1 a 5

**Insight:** o tratamento defensivo garante que a aplicação não quebre com planilhas preenchidas manualmente, que frequentemente contêm células vazias, texto em campos numéricos ou notas fora da escala.

### Cálculo do score e classificação

O score de risco é calculado como o produto das duas dimensões:

```
score = probabilidade × impacto
```

A classificação segue as faixas abaixo:

| Score   | Nível      | Interpretação                            |
| ------- | ---------- | ---------------------------------------- |
| 15 – 25 | 🔴 Crítico | Ação imediata obrigatória                |
| 10 – 14 | 🟠 Alto    | Plano de mitigação necessário            |
| 5 – 9   | 🟡 Médio   | Monitoramento periódico                  |
| 1 – 4   | 🟢 Baixo   | Risco aceito / acompanhamento passivo    |

**Insight:** o produto das dimensões faz com que riscos raros porém catastróficos (ex.: acidente de trabalho, prob. 1 × impacto 5) não sejam ignorados, mas também não sejam tratados com a mesma urgência de riscos prováveis e graves.

### Matriz de Riscos (gráfico de calor)

Heatmap 5×5 interativo construído com Plotly, onde:

- O eixo Y representa a **Probabilidade** e o eixo X o **Impacto**
- A cor de cada célula reflete a faixa de criticidade daquela combinação
- O número dentro da célula indica **quantos riscos** caem naquela posição
- O hover exibe a **lista nominal dos riscos** de cada célula

**Insight:** a concentração visual dos riscos no quadrante superior direito indica de imediato se a organização está exposta a um cenário crítico, algo que uma tabela ordenada não comunica com a mesma clareza.

### Distribuição por nível

Gráfico de barras com a contagem de riscos em cada nível de criticidade, com cores consistentes com a matriz.

**Insight:** permite acompanhar a evolução do perfil de risco entre atualizações — o ideal é que a proporção de Críticos e Altos diminua ao longo dos ciclos de tratamento.

### Relatório de riscos críticos

Todos os riscos classificados como **Crítico** ou **Alto** são listados automaticamente em cards destacados, contendo nome, nível, score, categoria, responsável, notas de probabilidade/impacto e descrição.

**Insight:** este é o entregável que efetivamente vira pauta de reunião — a saída da ferramenta não é apenas um gráfico, mas uma lista priorizada de ação com responsável nomeado.

### Indicadores e exportação

- KPIs no topo: total de riscos, quantidade de Críticos, quantidade de Altos e score médio da carteira
- Tabela completa da base tratada, ordenada por criticidade
- Botão de download do relatório processado em CSV (com `score` e `nivel` já calculados), pronto para ser anexado a atas ou importado no software corporativo de gestão de riscos

## Conclusão

### Principais entregas

1. **Automação do ciclo completo:** do CSV bruto ao relatório priorizado, sem intervenção manual em nenhuma etapa.

2. **Classificação padronizada:** o critério de criticidade fica definido em código, eliminando a variação de julgamento entre quem preenche a planilha.

3. **Visualização imediata:** a Matriz de Riscos é regerada a cada upload, permitindo que a atualização de rotina deixe de ser um trabalho de formatação.

4. **Saída reaproveitável:** a base processada é exportada em CSV e pode alimentar outros sistemas ou ser versionada ao longo do tempo.

### Limitações

- As notas de probabilidade e impacto continuam sendo um julgamento humano de entrada; a ferramenta padroniza o cálculo, não a avaliação inicial
- A escala é fixa em 5×5, padrão mais comum no mercado, mas algumas organizações utilizam matrizes 3×3 ou 4×4
- Não há persistência entre sessões: cada upload é uma análise independente, sem histórico comparativo automático
- O score multiplicativo trata probabilidade e impacto com o mesmo peso, o que nem sempre reflete o apetite a risco de todas as organizações

### Importante

**Nota sobre interpretação:** a matriz é uma ferramenta de **priorização**, não de previsão. Um risco classificado como Baixo não é um risco inexistente, e um risco Crítico não é um evento que necessariamente ocorrerá. A classificação serve para alocar atenção e recursos de forma proporcional à exposição estimada.

## Como executar

### 1. Clone o repositório

```bash
git clone <repository-url>
cd risk_matrix_app
```

### 2. Crie um ambiente virtual

```bash
python -m venv venv
```

Windows:
```bash
venv\Scripts\activate
```

Linux / macOS:
```bash
source venv/bin/activate
```

### 3. Instale as dependências

```bash
pip install -r requirements.txt
```

### 4. Execute a aplicação

```bash
streamlit run app.py
```

O navegador abrirá automaticamente em `http://localhost:8501`.

### 5. Carregue os dados

Na barra lateral, envie seu arquivo CSV de riscos ou marque a opção **"Usar dados de exemplo"** para explorar a ferramenta imediatamente com a base de demonstração incluída.

## Melhorias Futuras

1. Adicionar persistência em banco de dados para manter histórico e comparar ciclos de avaliação
2. Implementar matriz de risco residual (após aplicação dos controles de mitigação)
3. Permitir configuração da escala (3×3, 4×4, 5×5) e dos pesos de cada dimensão
4. Incluir campo de plano de ação com prazo e status de tratamento por risco
5. Gerar exportação do relatório em PDF para distribuição executiva
6. Criar filtros por categoria e responsável diretamente na interface
7. Adicionar autenticação para uso multiusuário em ambiente corporativo

