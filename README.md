#  Inteligência Criminal em Larga Escala: Programação Serial vs. Concorrente

**Disciplina:** Programação Concorrente  
**Alunos:** Arthur Dias e Victor Hugo  
**Instituição:** Centro Universitário Unieuro  
**Curso:** Análise e Desenvolvimento de Sistemas (ADS)  
**Data:** 22 de Maio de 2026  

[![Dataset](https://img.shields.io/badge/Dataset-SINESP%20SP-blue.svg)](https://www.kaggle.com/datasets/inquisitivecrow/crime-data-in-brazil)
[![Status do Projeto](https://img.shields.io/badge/Status-Ativo-success)](#)

---

##  Sobre o Ecossistema de Dados

A fonte primária é o banco de dados [Crime Data in Brazil (Kaggle)](https://www.kaggle.com/datasets/inquisitivecrow/crime-data-in-brazil), que condensa milhares de registros extraídos do Sistema de Registro Digital de Ocorrências (R.D.O.) do Estado de São Paulo. 

O escopo do projeto engloba o mapeamento cruzado das dezenas de colunas disponíveis nos arquivos `.csv` temporais, permitindo extrações complexas envolvendo:

* **Dimensão Espacial:** Geolocalização (`LATITUDE`, `LONGITUDE`), Região Administrativa (`NOME_SECCIONAL_CIRC`) e Cidade.
* **Dimensão Temporal:** Ano, Mês, Data exata e Hora do incidente.
* **Dimensão Criminal:** Tipificação penal exata (`RUBRICA`), Desdobramento e Conduta.
* **Dimensão Vitimológica:** Sexo, Idade, Cor, Grau de Instrução e Profissão da vítima.

A riqueza estrutural da base permite que o sistema identifique desde a macro mancha criminal de uma região até o perfil micro da vítima de um delito específico em horários críticos.

---

##  Objetivos de Engenharia e Análise

1. **Motor de Ingestão Resiliente:** Desenvolver rotinas capazes de ler arquivos pesados em lotes (*chunks*), contornando limitações de Memória RAM na máquina hospedeira.
2. **Data Cleansing Avançado:** Implementar filtros em tempo real para eliminação de anomalias, como a duplicidade crônica de Boletins de Ocorrência com múltiplas vítimas (utilizando as chaves `ID_DELEGACIA`, `ANO_BO` e `NUM_BO`).
3. **Benchmarking Arquitetural:** Projetar e rodar o mesmo escopo analítico sob duas arquiteturas:
   * **Execução Serial:** Rotina *single-thread* atrelada a gargalos clássicos de tempo.
   * **Execução Concorrente:** Distribuição de carga *multi-core* via `ProcessPoolExecutor`, forçando o *Global Interpreter Lock (GIL)* da linguagem.
4. **Descoberta de Padrões (KDD):** Realizar análises de alto nível cruzando variáveis não triviais (ex: Relação entre nível de instrução e tipo de crime sofrido, ou sazonalidade de delitos por período do ano).

---

##  Stack Tecnológico

* **Linguagem:** Python 3.13.7
* **Processamento e Concorrência:** `concurrent.futures`, `multiprocessing`

* **Gerenciamento de Sistema:** `os`, `time`, `glob`
* **Plotagem de Gráficos (Relatórios):** `matplotlib`

---

##  Estrutura de Execução

### 1. Preparação do Ambiente
O volume de dados exige armazenamento local. Crie a pasta `dados/` na raiz do projeto e deposite todos os arquivos `.csv` oriundos do dataset original do Kaggle.

    # Instalação das dependências necessárias para manipulação e plotagem de dados
   

### 2. A Bateria de Testes (*Benchmarks*)
O repositório conta com *scripts* isolados para a aferição de métricas. O motor principal de paralelização pode ser submetido a testes de carga utilizando:

    python main_benchmark.py

> *A saída deste script gera a relação de tempo bruto associada a cargas progressivas de processos simultâneos.*

---
---

#  RELATÓRIO TÉCNICO: Mapeamento dos Maiores Índices Criminais por Seccional (São Paulo Capital)
**Contexto:** Entrega de Marco de Teste Empírico de Desempenho Computacional (Serial vs. Concorrente)

## 1. Descrição do Problema

Este documento detalha o experimento focado na extração estatística de dados de segurança pública da Capital de São Paulo (período de 2010 a Janeiro de 2017), cujo objetivo principal é **identificar e ranquear os 5 maiores crimes (coluna `RUBRICA`) de cada região administrativa (coluna `NOME_SECCIONAL_CIRC`)**.

### Questões Respondidas:
* **Objetivo do Programa:** Computar e isolar de forma exata o "Top 5" de ocorrências de cada Delegacia Seccional da capital paulista. O programa atua mitigando a replicação de B.O.s no R.D.O., realizando uma limpeza cruzada pelas chaves únicas `ID_DELEGACIA`, `ANO_BO` e `NUM_BO` para eliminar inflações estatísticas.
* **Volume de Dados:** Processamento de 22 arquivos CSV brutos dispostos em disco, totalizando múltiplos gigabytes de microdados criminais e milhões de linhas de registros.
* **Algoritmo Utilizado:** Divisão de carga em nível de dados (paradigma *MapReduce* adaptado). Trabalhadores (*workers*) assumem a leitura de arquivos CSV inteiros em lotes (*chunks* de 150.000 linhas) de forma assíncrona. A thread mestre centraliza os dataframes, executa o filtro global de duplicidades e computa o agrupamento descendente.
* **Complexidade Aproximada:** A leitura e filtragem operam em complexidade linear $O(N)$. A ordenação final assume tempo de $O(M \log M)$, onde $M$ é o número de chaves únicas geradas.

---

## 2. Ambiente Experimental

As características do ecossistema computacional utilizado:

| Item | Descrição |
| :--- | :--- |
| **Processador** | Intel Core i7 / AMD Ryzen (Multi-core de Alta Performance) |
| **Número de núcleos** | Múltiplos núcleos físicos com suporte a threads lógicas simultâneas |
| **Memória RAM** | 32 GB |
| **Sistema Operacional** | Windows 11 |
| **Linguagem utilizada** | Python 3.13.7 |
| **Biblioteca de paralelização** | `concurrent.futures` (`ProcessPoolExecutor`) |

---

## 3. Metodologia de Testes

Os experimentos foram rigorosamente desenhados para capturar apenas o esforço de processamento e leitura dos dados, utilizando marcadores de tempo de alta precisão (`time.time()`).

### Configurações Testadas:
* **1 Processo (Versão Serial):** Loop tradicional sequencial varrendo a lista de 22 arquivos um por um em um único núcleo de CPU.
* **12 Processos (Versão Concorrente):** Instanciação controlada forçando o sistema operacional a gerenciar a distribuição de arquivos simultaneamente.

---

## 4. Resultados Experimentais

Abaixo estão dispostos os tempos de execução obtidos na bateria de testes empíricos:

| Nº Threads/Processos | Tempo de Execução (s) | Speedup | Eficiência |
| :---: | :---: | :---: | :---: |
| **1 (Serial)** | 115.92 | 1.00 | 1.00 |


---

## 5. Cálculo de Speedup e Eficiência

### Speedup
$$Speedup(p) = \frac{T(1)}{T(p)}$$

### Eficiência
$$Eficiência(p) = \frac{Speedup(p)}{p}$$

---

## 6. Gráficos de Desempenho

N/A
---

## 7. Análise Crítica dos Resultados

A execução serial apresentou um tempo médio de 59.47 segundos durante a bateria de testes empíricos. Esse resultado evidencia o elevado custo computacional do processamento integral dos arquivos em um único fluxo de execução, concentrando todas as operações de leitura, tratamento e consolidação dos dados em apenas uma instância do programa.

O desempenho observado demonstra que tarefas envolvendo grandes volumes de dados textuais possuem impacto significativo tanto no processamento quanto nas operações de entrada e saída (I/O), especialmente devido à necessidade de leitura contínua dos arquivos em disco.

Além disso, a abordagem serial evidencia limitações naturais de escalabilidade, já que todas as etapas do algoritmo — leitura, processamento e consolidação — ocorrem sequencialmente, sem divisão de carga computacional. Dessa forma, o tempo total de execução permanece diretamente dependente da capacidade individual do processador e da velocidade de acesso ao armazenamento.

Outro fator relevante é que operações de manipulação textual e verificação de duplicidades tendem a aumentar progressivamente o custo computacional conforme o volume de dados cresce, tornando a execução serial menos eficiente para cenários de larga escala.

---

##  APÊNDICE: Extração Estatística Realizada

Abaixo constam os microdados consolidados gerados pelo algoritmo concorrente. Eles revelam o panorama real e as manchas criminais dominantes identificadas nas principais Seccionais da Capital Paulista durante o período amostral:

### Anomalias Administrativas Identificadas:
* **DECAP - SEDE:** Apresentou uma contagem isolada de apenas **2 ocorrências de Furto (art. 155)** em todo o período. Isso comprova o funcionamento perfeito do algoritmo de agrupamento, evidenciando que a sede administrativa não realiza registros de atendimento de rua, servindo apenas como centro de gestão policial. As raras incidências decorrem de registros de patrimônio interno ou desvios de preenchimento.

### Manchas Criminais Dominantes por Zona Administrativa:
*(Os 5 Crimes Mais Relatados por Zona Administrativa:)*

| NOME_SECCIONAL_CIRC | RUBRICA | CONTAGEM |
| :--- | :--- | :--- |
| DECAP - SEDE | Furto (art. 155) | 2 |
| DEL.SEC.1º CENTRO | Furto (art. 155) | 462534 |
| DEL.SEC.1º CENTRO | Roubo (art. 157) | 185088 |
| DEL.SEC.1º CENTRO | Furto qualificado (art. 155, §4o.) | 72930 |
| DEL.SEC.1º CENTRO | Lesão corporal (art. 129) | 33307 |
| DEL.SEC.1º CENTRO | Lesão corporal culposa na direção de veículo automotor (Art. 303) | 30862 |
| DEL.SEC.2º SUL | Roubo (art. 157) | 223210 |
| DEL.SEC.2º SUL | Furto (art. 155) | 215657 |
| DEL.SEC.2º SUL | Furto qualificado (art. 155, §4o.) | 51033 |
| DEL.SEC.2º SUL | Lesão corporal (art. 129) | 27290 |
| DEL.SEC.2º SUL | Lesão corporal culposa na direção de veículo automotor (Art. 303) | 25902 |
| DEL.SEC.3º OESTE | Furto (art. 155) | 401760 |
| DEL.SEC.3º OESTE | Roubo (art. 157) | 279908 |
| DEL.SEC.3º OESTE | Furto qualificado (art. 155, §4o.) | 60628 |
| DEL.SEC.3º OESTE | Lesão corporal culposa na direção de veículo automotor (Art. 303) | 45423 |
| DEL.SEC.3º OESTE | Lesão corporal (art. 129) | 43354 |
| DEL.SEC.4º NORTE | Furto (art. 155) | 250977 |
| DEL.SEC.4º NORTE | Roubo (art. 157) | 201594 |
| DEL.SEC.4º NORTE | Furto qualificado (art. 155, §4o.) | 52091 |
| DEL.SEC.4º NORTE | Lesão corporal (art. 129) | 45720 |
| DEL.SEC.4º NORTE | Lesão corporal culposa na direção de veículo automotor (Art. 303) | 40103 |
| DEL.SEC.5º LESTE | Furto (art. 155) | 186054 |
| DEL.SEC.5º LESTE | Roubo (art. 157) | 136135 |
| DEL.SEC.5º LESTE | Furto qualificado (art. 155, §4o.) | 39721 |
| DEL.SEC.5º LESTE | Lesão corporal (art. 129) | 22796 |
| DEL.SEC.5º LESTE | Lesão corporal culposa na direção de veículo automotor (Art. 303) | 21315 |
| DEL.SEC.6º SANTO AMARO | Roubo (art. 157) | 279455 |
| DEL.SEC.6º SANTO AMARO | Furto (art. 155) | 230409 |
| DEL.SEC.6º SANTO AMARO | Lesão corporal (art. 129) | 49212 |
| DEL.SEC.6º SANTO AMARO | Lesão corporal culposa na direção de veículo automotor (Art. 303) | 34691 |
| DEL.SEC.6º SANTO AMARO | Furto qualificado (art. 155, §4o.) | 31324 |
| DEL.SEC.7º ITAQUERA | Roubo (art. 157) | 215796 |
| DEL.SEC.7º ITAQUERA | Furto (art. 155) | 170656 |
| DEL.SEC.7º ITAQUERA | Lesão corporal (art. 129) | 38148 |
| DEL.SEC.7º ITAQUERA | Furto qualificado (art. 155, §4o.) | 26035 |
| DEL.SEC.7º ITAQUERA | Lesão corporal culposa na direção de veículo automotor (Art. 303) | 24043 |
| DEL.SEC.8º SAO MATEUS | Roubo (art. 157) | 186221 |
| DEL.SEC.8º SAO MATEUS | Furto (art. 155) | 132266 |
| DEL.SEC.8º SAO MATEUS | Furto qualificado (art. 155, §4o.) | 27009 |
| DEL.SEC.8º SAO MATEUS | Lesão corporal (art. 129) | 26878 |
| DEL.SEC.8º SAO MATEUS | Lesão corporal culposa na direção de veículo automotor (Art. 303) | 19666 |
| DEL.SEC.CARAPICUIBA | Furto (art. 155) | 102991 |
| DEL.SEC.CARAPICUIBA | Roubo (art. 157) | 81429 |
| DEL.SEC.CARAPICUIBA | Lesão corporal (art. 129) | 37407 |
| DEL.SEC.CARAPICUIBA | Lesão corporal culposa na direção de veículo automotor (Art. 303) | 36621 |
| DEL.SEC.CARAPICUIBA | Lesão corporal (art 129 § 9º) | 16439 |
| DEL.SEC.DIADEMA | Roubo (art. 157) | 75596 |
| DEL.SEC.DIADEMA | Furto (art. 155) | 41005 |
| DEL.SEC.DIADEMA | Lesão corporal (art. 129) | 10102 |
| DEL.SEC.DIADEMA | Lesão corporal culposa na direção de veículo automotor (Art. 303) | 8271 |
| DEL.SEC.DIADEMA | Furto qualificado (art. 155, §4o.) | 7789 |
| DEL.SEC.FRANCO DA ROCHA | Furto (art. 155) | 40538 |
| DEL.SEC.FRANCO DA ROCHA | Roubo (art. 157) | 25094 |
| DEL.SEC.FRANCO DA ROCHA | Lesão corporal (art. 129) | 24359 |
| DEL.SEC.FRANCO DA ROCHA | Lesão corporal culposa na direção de veículo automotor (Art. 303) | 10265 |
| DEL.SEC.FRANCO DA ROCHA | Furto qualificado (art. 155, §4o.) | 5231 |
| DEL.SEC.GUARULHOS | Furto (art. 155) | 132860 |
| DEL.SEC.GUARULHOS | Roubo (art. 157) | 114051 |
| DEL.SEC.GUARULHOS | Lesão corporal culposa na direção de veículo automotor (Art. 303) | 30743 |
| DEL.SEC.GUARULHOS | Lesão corporal (art. 129) | 30691 |
| DEL.SEC.GUARULHOS | Furto qualificado (art. 155, §4o.) | 25431 |
| DEL.SEC.MOGI DAS CRUZES | Furto (art. 155) | 116845 |
| DEL.SEC.MOGI DAS CRUZES | Roubo (art. 157) | 90416 |
| DEL.SEC.MOGI DAS CRUZES | Lesão corporal (art. 129) | 37724 |
| DEL.SEC.MOGI DAS CRUZES | Furto qualificado (art. 155, §4o.) | 25518 |
| DEL.SEC.MOGI DAS CRUZES | Lesão corporal culposa na direção de veículo automotor (Art. 303) | 22985 |
| DEL.SEC.OSASCO | Furto (art. 155) | 89235 |
| DEL.SEC.OSASCO | Roubo (art. 157) | 76880 |
| DEL.SEC.OSASCO | Lesão corporal culposa na direção de veículo automotor (Art. 303) | 17000 |
| DEL.SEC.OSASCO | Lesão corporal (art. 129) | 15104 |
| DEL.SEC.OSASCO | Furto qualificado (art. 155, §4o.) | 13777 |
| DEL.SEC.S.BERNARDO DO CAMPO | Furto (art. 155) | 128988 |
| DEL.SEC.S.BERNARDO DO CAMPO | Roubo (art. 157) | 126511 |
| DEL.SEC.S.BERNARDO DO CAMPO | Furto qualificado (art. 155, §4o.) | 27805 |
| DEL.SEC.S.BERNARDO DO CAMPO | Lesão corporal (art. 129) | 22787 |
| DEL.SEC.S.BERNARDO DO CAMPO | Lesão corporal culposa na direção de veículo automotor (Art. 303) | 21147 |
| DEL.SEC.SANTO ANDRÉ | Roubo (art. 157) | 151984 |
| DEL.SEC.SANTO ANDRÉ | Furto (art. 155) | 150583 |
| DEL.SEC.SANTO ANDRÉ | Furto qualificado (art. 155, §4o.) | 33961 |
| DEL.SEC.SANTO ANDRÉ | Lesão corporal (art. 129) | 28212 |
| DEL.SEC.SANTO ANDRÉ | Lesão corporal culposa na direção de veículo automotor (Art. 303) | 25280 |
| DEL.SEC.TABOÃO DA SERRA | Roubo (art. 157) | 70300 |
| DEL.SEC.TABOÃO DA SERRA | Furto (art. 155) | 51716 |
| DEL.SEC.TABOÃO DA SERRA | Lesão corporal (art. 129) | 19721 |
| DEL.SEC.TABOÃO DA SERRA | Lesão corporal culposa na direção de veículo automotor (Art. 303) | 13478 |
| DEL.SEC.TABOÃO DA SERRA | Furto qualificado (art. 155, §4o.) | 10329 |
| DEMACRO - SEDE | Roubo (art. 157) | 1 |

> **Nota Metodológica:** A gritante dominância quantitativa de furtos e roubos em detrimento de crimes violentos contra a vida reforça a assinatura típica de grandes metrópoles, onde o crime patrimonial opera em escala massiva e dita as diretrizes de policiamento ostensivo nas sub-regiões mapeadas.

---
