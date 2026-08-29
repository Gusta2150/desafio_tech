# Roteiro — Vídeo de Apresentação (Tech Challenge Fase 1)

**Duração alvo: até 15 minutos.** Tempos entre colchetes são sugestões — ajustem no ensaio.
**Ferramenta:** VS Code, notebook `notebooks/01_eda.ipynb`, célula por célula ("Run All" desligado — rodem uma de cada vez conforme falam).

## Antes de gravar (checklist rápido)

- [ ] Reiniciar o kernel do notebook (`Restart Kernel`) pra gravar uma execução limpa, do zero.
- [ ] Confirmar que a célula **2.1** está apontando para `data/data.csv` (dataset completo, 569 amostras) — é o arquivo principal da apresentação.
- [ ] Ter os outros CSVs já visíveis na pasta `data/` pra trocar rápido na parte de validações: `cancer_mama_1_diagnostico.csv`, `animais_data.csv`, `breast_cancer_sample.csv`.
- [ ] Tela cheia do VS Code, fonte grande o suficiente pra gravação.
- [ ] Decidir quem fala em qual bloco (sugestão de divisão abaixo — ajustem como preferirem).

**Divisão sugerida entre os 3 integrantes:**
- **Bloco A — Gabriel:** Abertura, Validação (2.1/2.2), EDA (3.x)
- **Bloco B — Gustavo:** Modelagem completa (4.1 a 4.7)
- **Bloco C — Luiz:** Inferência, testes manuais, PDF (4.8 a 5.2), Validações extras, Encerramento

---

## Abertura — [30s]

> "Oi, somos [nomes], e esse é o projeto do Tech Challenge Fase 1 da FIAP: um sistema de apoio ao diagnóstico de câncer de mama, usando Machine Learning sobre dados estruturados do dataset Breast Cancer Wisconsin. Vamos apresentar o notebook do início ao fim — validação, análise exploratória, modelagem, avaliação, explicabilidade e geração de relatório — e no final mostramos como o sistema reage a arquivos que **não** são compatíveis, pra provar que a validação funciona de verdade."

---

## 2.1 — Carregamento, escopo e validação da base — [1 min]

**Célula 2 (imports):** "Aqui importamos pandas, numpy, matplotlib e seaborn — as bibliotecas básicas de dados e visualização."

**Rodar célula 2.1 (carregamento):**
> "Essa célula lê o `data.csv`, remove colunas totalmente vazias e o identificador `id`, que não tem valor preditivo. Ela também normaliza a coluna `diagnosis`: aceitamos `M`/`B`, `malignant`/`benign` e `maligno`/`benigno` — em qualquer combinação de maiúsculas ou minúsculas — e padronizamos tudo pra `M` e `B`. Se a coluna `diagnosis` não existir, o notebook já para aqui com uma mensagem clara."

*(mostrar o output: 569 amostras, 30 atributos, distribuição 357 benignos / 212 malignos, zero valores ausentes)*

## 2.2 — Status de compatibilidade — [45s]

**Rodar célula 2.2:**
> "Antes de qualquer treinamento, o notebook confere se o arquivo realmente tem as medidas esperadas de um exame de câncer de mama — raio, textura, perímetro, área, concavidade. Se faltar alguma, ele mostra 'CSV incompatível' e para ali, sem tentar treinar em cima de dado errado. Aqui, como é o nosso dataset, aparece 'CSV compatível — domínio identificado: câncer de mama'."

---

## 3. Análise Exploratória de Dados (EDA) — [2 min]

**Célula `df.info()`:**
> "Aqui vemos os tipos de cada coluna e confirmamos que não há valores nulos — 569 registros completos."

**Célula `df.describe()` (3.2):**
> "As estatísticas descritivas mostram a escala de cada atributo — por exemplo, a área média varia de 143 a mais de 2500, bem diferente da escala da textura. Isso já indica que vamos precisar normalizar os dados antes de treinar."

**Gráfico de distribuição (3.3):**
> "Esse gráfico mostra o desbalanceamento entre as classes: mais casos benignos que malignos. Isso é importante porque vai guiar a escolha da métrica de avaliação mais pra frente — accuracy sozinha esconderia esse desbalanceamento."

**Matriz de correlação (3.4):**
> "O mapa de calor mostra a correlação entre todos os atributos numéricos. Correlação mostra associação, não causa — mas já dá pra ver famílias de atributos (tamanho, textura, concavidade) que se movem juntas."

---

## 4.1 a 4.3 — Preparação para modelagem — [1 min]

**Célula de imports de ML:**
> "Aqui entram os dois algoritmos que vamos comparar — Regressão Logística e Random Forest —, as métricas de avaliação, o pipeline de pré-processamento e o SHAP pra explicabilidade."

**4.2 — Preparação do alvo:**
> "Convertendo o diagnóstico pra número: maligno vira 1, benigno vira 0. Essa é a variável que o modelo vai aprender a prever."

**4.3 — Padrões relevantes:**
> "Aqui reforçamos por que o recall da classe maligna importa tanto: em triagem, deixar passar um caso maligno — um falso negativo — é bem mais grave do que encaminhar por engano um caso benigno pra investigação. O gráfico mostra os 10 atributos mais correlacionados com malignidade."

## 4.4 — Pré-processamento e separação treino/teste — [1 min]

**Rodar célula 4.4:**
> "Essa célula separa 80% dos dados pra treino e 20% pra teste, de forma estratificada — mantendo a mesma proporção de benignos e malignos nos dois grupos. O pipeline usa imputação de mediana pra valores ausentes e `StandardScaler` pra normalizar as escalas que vimos lá na EDA. E tem uma proteção extra: se a base tiver poucas amostras, o notebook adapta automaticamente o tamanho do teste pra garantir pelo menos um caso de cada classe — vamos mostrar isso funcionando na parte de validações, mais pro final."

## 4.5 — Modelagem — [1 min]

**Rodar célula de treino:**
> "Treinamos dois modelos com os mesmos dados: Regressão Logística, que é mais simples e interpretável, e Random Forest, que captura relações não lineares. A tabela compara accuracy, recall de malignidade, F1 e ROC-AUC, e o notebook escolhe automaticamente o modelo com melhor recall — porque é a métrica prioritária pro nosso problema."

## 4.6 — Avaliação — [1 min]

**Rodar célula de avaliação:**
> "Aqui está o relatório de classificação completo, a matriz de confusão e a curva ROC do modelo escolhido. Na matriz de confusão, a diagonal são os acertos; fora da diagonal estão os erros — e o número de falsos negativos, caso maligno classificado como benigno, é o dado mais crítico pra discussão clínica do projeto."

## 4.7 — Explicabilidade — [1 min]

**Rodar célula de importância/SHAP:**
> "Duas técnicas aqui: importância por permutação, que mede quanto a métrica cai quando embaralhamos um atributo, e SHAP, que explica a contribuição de cada atributo pra uma previsão específica. As duas ajudam a entender o comportamento do modelo, mas não provam causalidade clínica — atributo importante não é o mesmo que causa da doença."

---

## 4.8 — Serviço de inferência — [45s]

**Rodar célula da função:**
> "Essa função recebe novas amostras, confere se as colunas batem com o que o modelo espera, calcula a probabilidade de malignidade e devolve uma orientação de triagem — encaminhar ou não, com base num limiar técnico de 0,5. O modelo treinado é salvo em `models/modelo_cancer_mama.joblib` pra poder ser reaproveitado sem retreinar."

## 5.1 — Testes manuais — [30s]

**Rodar célula de teste:**
> "Por padrão, testamos três exemplos reservados do próprio conjunto de teste — dá pra ver a probabilidade e a orientação pra cada um. Pra testar um arquivo novo, é só trocar `USAR_CSV_NOVO` pra `True`."

## 5.2 — Geração do PDF — [30s]

**Rodar célula do PDF:**
> "Essa célula gera automaticamente um PDF de análise diagnóstica com tudo que vimos: status de compatibilidade, distribuição dos diagnósticos, métricas do modelo, os gráficos de EDA, matriz de confusão e importância dos atributos. Esse mesmo gerador é reaproveitado pela nossa aplicação web, então o relatório é idêntico não importa se roda pelo notebook ou pelo site."
*(opcional: abrir o PDF gerado rapidamente na tela)*

---

## Validações com outros arquivos — [3 min]

> "Pra provar que essas validações realmente funcionam, vamos trocar o arquivo de entrada e mostrar três cenários diferentes."

**1) Arquivo de outro domínio — `animais_data.csv`** *(trocar `data_path` na célula 2.1 e rodar de novo)*
> "Esse é um dataset de animais, sem nenhuma relação com câncer de mama. Rodando a célula 2.1 de novo... o notebook não encontra a coluna `diagnosis` e já interrompe com a mensagem: 'não identificado como câncer de mama'. Nenhum treinamento é feito em cima de dado errado."

**2) Arquivo com só uma classe — `cancer_mama_1_diagnostico.csv`** *(trocar o arquivo, rodar 2.1, 2.2 e a célula 4.4)*
> "Esse arquivo tem 212 registros reais de câncer de mama, mas só da classe maligna — nenhum caso benigno. Ele passa na validação de domínio, porque as colunas batem, mas quando chega na separação treino/teste, a célula 4.4 barra: 'não é possível treinar um classificador com apenas uma classe'. Isso evita treinar um modelo enviesado ou quebrado."

**3) Arquivo pequeno — `breast_cancer_sample.csv`** *(trocar o arquivo, rodar 2.1 até 4.4)*
> "Esse é só um recorte de 5 amostras. Diferente dos outros dois, esse **passa** — mas o notebook adapta automaticamente o tamanho do conjunto de teste pra garantir pelo menos uma amostra de cada classe nos dois grupos, em vez de simplesmente travar por falta de dado."

*(voltar `data_path` pra `data.csv` ao final, se for continuar usando o notebook depois)*

---

## Encerramento — [1 min]

> "Resumindo: construímos um pipeline completo — validação de domínio, EDA, pré-processamento, comparação de dois modelos, avaliação priorizando recall de malignidade, explicabilidade com SHAP e importância por permutação, um serviço de inferência e geração automática de relatório em PDF. E, como mostramos agora, o sistema também sabe dizer 'não' de forma clara quando o dado não serve pra esse problema.
>
> Importante reforçar: esse é um projeto educacional, de apoio à triagem. Ele não substitui exame clínico, mamografia, biópsia ou a decisão de um profissional de saúde — o médico sempre tem a palavra final. Obrigado!"

---

## Notas finais

- Se sobrar tempo, vale mostrar rapidamente a aplicação web (upload de CSV, abas de resultado, PDF pelo front) — mas isso é opcional e não estava no escopo pedido aqui; me avisem se quiserem um roteiro à parte pra essa parte.
- Se faltar tempo, o bloco de "Validações com outros arquivos" pode ser cortado pra só 2 exemplos (domínio errado + uma classe só) sem perder o essencial.
