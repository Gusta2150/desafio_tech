# Análise diagnóstica — câncer de mama

## Identificação da base analisada

Este documento apresenta a análise gerada a partir do arquivo processado pelo
sistema. O resultado de compatibilidade, a distribuição dos diagnósticos e as
métricas do modelo são inseridos automaticamente na primeira seção do PDF.

O identificador de compatibilidade verifica se o CSV contém a coluna
`diagnosis` e medidas morfológicas esperadas para o domínio de câncer de mama,
como raio, textura, perímetro e área. Um CSV incompatível não deve ser usado
para treinamento ou previsão.

## Escopo da classificação

Quando a base é compatível e contém as duas classes, o classificador estima se
as características de uma amostra são mais semelhantes a registros benignos ou
malignos presentes na base de treinamento.

- **Benigno:** rótulo `B` ou `benign` na fonte de dados;
- **Maligno:** rótulo `M` ou `malignant` na fonte de dados.

A análise usa medidas estruturadas de características de massas mamárias. Ela
não processa mamografias brutas, histórico clínico completo, exames físicos ou
resultados de biópsia.

## Leitura dos resultados

O PDF apresenta as seguintes informações quando a execução completa do notebook
foi realizada:

- status de compatibilidade do CSV com o domínio de câncer de mama;
- quantidade de registros benignos e malignos;
- modelo selecionado para a classificação;
- accuracy, recall de malignidade, F1-score e ROC-AUC;
- origem dos testes manuais realizados no notebook.

O **recall de malignidade** recebe atenção especial porque mede a proporção de
casos malignos identificados pelo modelo. Mesmo assim, nenhuma métrica isolada
é suficiente: precisão, F1-score, curva ROC e matriz de confusão devem ser
interpretadas em conjunto.

## Fatores associados à classificação

O notebook analisa correlações entre os atributos e o desfecho, além de
importância por permutação e SHAP. Essas técnicas indicam quais variáveis mais
influenciaram o comportamento do modelo naquela execução.

Elas não demonstram causalidade clínica. Uma variável importante para a
previsão não confirma que ela seja a causa de uma doença.

## Limites da análise

Este resultado é exclusivamente de apoio educacional à triagem:

- uma probabilidade baixa não exclui câncer;
- uma probabilidade alta não confirma câncer;
- um CSV incompatível não permite concluir que a pessoa não tem câncer de
  mama;
- a decisão final deve ser tomada por profissionais de saúde, considerando
  exames, contexto clínico e protocolos aplicáveis.

Qualquer uso em ambiente real exigiria validação clínica externa, avaliação de
vieses, proteção de dados pessoais e acompanhamento contínuo do desempenho.
