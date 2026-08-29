# Relatório técnico — apoio à classificação de câncer de mama

## 1. Visão geral do projeto

Este projeto apresenta uma solução inicial de Machine Learning para apoiar a
classificação de exames em dois grupos:

- **Benigno (B):** amostra sem indicação de malignidade no rótulo da base;
- **Maligno (M):** amostra com indicação de malignidade no rótulo da base.

O objetivo não é substituir o diagnóstico médico. O sistema funciona como uma
ferramenta de **apoio à triagem**, capaz de fornecer uma estimativa baseada nos
dados de entrada. A decisão clínica deve continuar sendo tomada por um
profissional de saúde, com base no histórico da paciente, exames, imagens,
biópsias e protocolos clínicos.

O fluxo completo está implementado no notebook
`notebooks/01_eda.ipynb`, nas seções de EDA e de modelagem.

## 2. Problema de saúde escolhido

O câncer de mama é um problema relevante para a saúde da mulher, e a detecção
precoce pode apoiar decisões de encaminhamento e investigação. Neste projeto,
o problema é formulado como uma **classificação binária supervisionada**:

| Pergunta | Resposta |
| --- | --- |
| O que o modelo recebe? | Medidas numéricas de características de uma massa mamária. |
| O que o modelo prevê? | Probabilidade de a amostra pertencer à classe maligna. |
| Quais são as classes? | `B` (benigno) e `M` (maligno). |
| Qual é o principal risco? | Um falso negativo pode atrasar uma investigação necessária. |

Os dados utilizados não são imagens de mamografia. Eles são atributos já
extraídos de imagens digitalizadas de massas mamárias. Portanto, este projeto
não implementa o item extra de Visão Computacional/CNN.

## 3. Fonte de dados

Foi selecionado o dataset público **Breast Cancer Wisconsin (Diagnostic)**,
disponibilizado no Kaggle:

<https://www.kaggle.com/datasets/uciml/breast-cancer-wisconsin-data/data>

O arquivo deve ser obtido pela pessoa que executa o projeto e salvo em
`data/breast_cancer_data.csv`. Ele não é versionado no repositório para evitar distribuir
dados sem necessidade. As instruções de download estão em `data/README.md`.

A base contém uma coluna `diagnosis` e atributos como:

- `radius_mean`: medida média do raio;
- `texture_mean`: medida média de textura;
- `perimeter_mean`: medida média de perímetro;
- `area_mean`: medida média de área;
- atributos de suavidade, compacidade, concavidade, simetria e dimensão
  fractal;
- medidas do erro padrão (`*_se`) e dos valores extremos (`*_worst`).

Essas variáveis descrevem características morfológicas. Elas não representam o
contexto clínico completo de uma paciente.

## 4. Exploração dos dados (EDA)

A primeira parte do notebook realiza a Análise Exploratória de Dados (EDA) para
entender a base antes do treinamento.

### 4.1 Verificação inicial

São verificados:

1. quantidade de linhas e colunas;
2. tipos de dados;
3. distribuição do diagnóstico;
4. valores ausentes;
5. colunas que não devem ser usadas como preditores.

A coluna `id` é removida porque é apenas um identificador e não possui
significado clínico para a previsão. Colunas completamente vazias, como
`Unnamed: 32` quando presente no CSV original, também são removidas.

### 4.2 Distribuição das classes

O notebook apresenta um gráfico com a quantidade de exemplos benignos e
malignos. Essa análise é importante porque uma base desbalanceada pode levar um
modelo a favorecer a classe mais frequente.

Em saúde, analisar somente a acurácia pode ser enganoso. Por exemplo, um modelo
que classifica a maioria dos casos como benignos pode obter uma acurácia
aparentemente boa e, ainda assim, deixar de sinalizar casos malignos.

### 4.3 Análise de correlação

O projeto calcula a correlação de Pearson entre as variáveis numéricas e o
desfecho codificado (`0` para benigno, `1` para maligno). Também é exibido um
mapa de calor com os atributos mais associados ao alvo.

Essa análise ajuda a:

- encontrar atributos potencialmente relevantes;
- identificar variáveis muito parecidas entre si;
- orientar a interpretação dos resultados.

Correlação não demonstra causalidade. Uma variável correlacionada ao diagnóstico
não é, isoladamente, a causa da doença.

## 5. Pré-processamento

O pré-processamento prepara os dados para que os modelos possam utilizá-los de
forma consistente e sem vazamento de informação.

### 5.1 Limpeza e tratamento de ausências

O pipeline trata dados ausentes da seguinte maneira:

- colunas numéricas: imputação pela **mediana**;
- colunas categóricas: imputação pelo valor **mais frequente**.

Embora esta base específica seja predominantemente numérica, o pipeline também
suporta dados categóricos. Isso torna o fluxo mais reutilizável caso novas
variáveis sejam adicionadas no futuro.

### 5.2 Conversão e escala

As variáveis numéricas são padronizadas com `StandardScaler`. Esse processo
centraliza e escala os valores, o que é particularmente importante para a
Regressão Logística, pois as medidas possuem escalas muito diferentes.

Caso existam colunas categóricas, elas são convertidas com `OneHotEncoder`.

### 5.3 Separação entre treino e teste

Os dados são separados em:

- **80% para treinamento:** utilizados para ajustar os transformadores e os
  modelos;
- **20% para teste:** reservados para a avaliação final.

A separação é estratificada, preservando aproximadamente a proporção de casos
benignos e malignos em ambos os conjuntos. O `Pipeline` do scikit-learn garante
que imputação, escala e codificação sejam ajustadas somente com dados de treino,
evitando vazamento de dados do conjunto de teste.

## 6. Modelos preditivos

São treinados e comparados dois modelos.

### 6.1 Regressão Logística

A Regressão Logística é um modelo linear de classificação. Ela é usada como
baseline por ser eficiente, interpretável e adequada para prever probabilidades
em problemas binários.

### 6.2 Random Forest

O Random Forest combina várias árvores de decisão. Ele pode capturar relações
não lineares entre os atributos e costuma ser robusto para dados tabulares.

Nos dois modelos é utilizado `class_weight="balanced"`, que aumenta a atenção
dada à classe menos frequente durante o treinamento.

## 7. Treinamento e avaliação

Para cada modelo, o notebook calcula as métricas no conjunto de teste:

| Métrica | O que mede | Por que importa neste problema |
| --- | --- | --- |
| Accuracy | Proporção total de acertos | Resume o desempenho geral, mas não deve ser usada sozinha. |
| Recall de malignidade | Casos malignos corretamente identificados entre todos os malignos | É prioritário porque falsos negativos podem atrasar investigação clínica. |
| F1-score de malignidade | Equilíbrio entre precisão e recall | Ajuda a avaliar se o ganho de recall não veio com excesso de alertas incorretos. |
| ROC-AUC | Capacidade de ordenar casos malignos acima de benignos em diferentes limiares | Permite comparar a discriminação dos modelos sem fixar um único limiar. |

Também são gerados:

- relatório de classificação;
- matriz de confusão;
- curva ROC.

O modelo é selecionado inicialmente pelo maior **recall da classe maligna**,
considerando F1-score e ROC-AUC como critérios complementares. Os valores
numéricos devem ser obtidos ao executar o notebook com a base de dados; este
relatório não apresenta métricas inventadas sem uma execução reprodutível.

## 8. Explicabilidade

Modelos em saúde precisam ser interpretados com cautela. O notebook inclui duas
formas de explicabilidade:

1. **Importância por permutação:** embaralha uma variável por vez e mede a queda
   de desempenho. Uma queda maior sugere que o modelo dependia mais daquela
   variável;
2. **SHAP (opcional):** mostra a contribuição de cada atributo para as
   previsões. É executado quando a biblioteca `shap` está instalada.

As explicações descrevem o comportamento do modelo, não uma relação causal ou
uma justificativa clínica suficiente para diagnóstico.

## 9. Como realizar uma previsão com novos dados

Depois de executar todas as células do notebook, a função
`prever_risco_cancer_mama()` fica disponível.

Para testar exemplos já separados para teste:

```python
prever_risco_cancer_mama(X_test.head(1))
```

Para inserir novos dados, crie o arquivo `data/nova_amostra.csv` com as mesmas
colunas de atributos da base de treinamento e sem `id`, `diagnosis` ou
`Unnamed: 32`. Em seguida, execute:

```python
nova_amostra = pd.read_csv("../data/nova_amostra.csv")
nova_amostra = nova_amostra.drop(
    columns=["id", "diagnosis", "Unnamed: 32"],
    errors="ignore",
)

resultado = prever_risco_cancer_mama(nova_amostra)
display(resultado)
```

O resultado contém:

- `probabilidade_malignidade`: estimativa numérica entre 0 e 1;
- `limiar`: valor usado para sinalizar a triagem, inicialmente `0.50`;
- `orientacao`: mensagem de encaminhamento para avaliação médica quando o
  limiar é atingido;
- `aviso`: lembrete de que o resultado não é um diagnóstico definitivo.

O modelo treinado é salvo localmente em
`models/modelo_cancer_mama.joblib`. Esse arquivo é ignorado pelo Git porque é
um artefato gerado pela execução e deve ser versionado apenas em uma estratégia
controlada de MLOps.

## 10. Limitações, ética e uso responsável

Esta solução não pode ser usada diretamente em atendimento clínico. Antes de
qualquer uso real, seriam necessários:

- validação externa em diferentes hospitais, equipamentos e populações;
- avaliação prospectiva e revisão por especialistas;
- análise de desempenho por subgrupos, como idade, raça/etnia e região;
- definição clínica do limiar de decisão;
- governança, segurança e rastreabilidade dos dados;
- conformidade com a LGPD e demais exigências éticas e regulatórias;
- monitoramento contínuo de qualidade e deriva do modelo.

Além disso, uma probabilidade baixa não exclui câncer e uma probabilidade alta
não confirma a doença. O resultado deve sempre ser combinado com a avaliação
médica.

## 11. Como reproduzir o projeto

```bash
cd tech-challenge-fase1
python3.12 -m venv .venv
source .venv/bin/activate  # Linux/macOS
pip install -r requirements.txt
```

Depois:

1. baixe `data.csv` conforme `data/README.md`;
2. coloque-o em `data/breast_cancer_data.csv`;
3. abra `notebooks/01_eda.ipynb`;
4. execute as células de cima para baixo.

## 12. Conclusão

O projeto atende à proposta de criar uma solução inicial de IA para
classificação de risco/diagnóstico de câncer de mama com dados estruturados. O
notebook cobre exploração, limpeza, correlação, pré-processamento, treinamento,
comparação de modelos, avaliação, explicabilidade e uma função de inferência.

O principal resultado do projeto é demonstrar um fluxo técnico reprodutível de
Machine Learning. A aplicação prática em saúde, contudo, depende de validação
clínica e de supervisão humana rigorosa.
