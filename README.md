#  Inteligência Criminal em Larga Escala: Programação Serial vs. Concorrente

**Disciplina:** Programação Concorrente  
**Alunos:** Arthur Dias e Victor Hugo  
**Instituição:** Centro Universitário Unieuro  
**Curso:** Análise e Desenvolvimento de Sistemas (ADS)  
**Data:** 16 de Junho de 2026  

[![Dataset](https://img.shields.io/badge/Dataset-SINESP%20SP-blue.svg)](https://www.kaggle.com/datasets/inquisitivecrow/crime-data-in-brazil)
[![Status do Projeto](https://img.shields.io/badge/Status-Concluído-success)](#)

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

1. **Motor de Ingestão Resiliente:** Desenvolver rotinas capazes de ler arquivos pesados em fluxo contínuo (*streaming*), contornando limitações de Memória RAM na máquina hospedeira.
2. **Data Cleansing Avançado:** Implementar filtros em tempo real para eliminação de anomalias, como a duplicidade crônica de Boletins de Ocorrência com múltiplas vítimas (utilizando as chaves `ID_DELEGACIA`, `ANO_BO` e `NUM_BO`).
3. **Benchmarking Arquitetural:** Projetar e rodar o mesmo escopo analítico sob duas arquiteturas:
   * **Execução Serial:** Rotina *single-thread* atrelada a gargalos clássicos de tempo.
   * **Execução Concorrente:** Distribuição de carga *multi-core* via `ProcessPoolExecutor`, contornando o *Global Interpreter Lock (GIL)* da linguagem.
4. **Descoberta de Padrões (KDD):** Realizar análises de alto nível cruzando variáveis não triviais (ex: Relação entre nível de instrução e tipo de crime sofrido, ou sazonalidade de delitos por período do ano).

---

##  Stack Tecnológico

* **Linguagem:** Python 3.13
* **Processamento e Concorrência:** `concurrent.futures`, `multiprocessing`
* **Gerenciamento de Sistema:** `os`, `time`, `glob`, `sys`
* **Leitura de Dados:** `csv` (DictReader em modo streaming)
* **Estruturas de Dados:** `collections` (defaultdict)

> ⚠️ **Restrição Acadêmica:** É estritamente proibido o uso de `pandas` ou qualquer framework de banco de dados. Todo o processamento é feito em **Python Puro** com biblioteca padrão.

---

##  Estrutura de Execução

### 1. Preparação do Ambiente

O volume de dados exige armazenamento local. Crie a pasta `dados/` na raiz do projeto e deposite todos os arquivos `.csv` oriundos do dataset original do Kaggle.

```
📁 Projeto_Concorrencia/
│
├── 📁 dados/                  ← 22 arquivos .csv descompactados (Kaggle SSP-SP)
│
├── 📄 main_serial.py          ← Motor sequencial (1 núcleo, Python Puro)
│
├── 📄 main_concorrente.py     ← Motor concorrente (N núcleos, ProcessPoolExecutor)
│
└── 📄 README.md               ← Este arquivo
```

### 2. Execução Serial

```bash
py main_serial.py
```

### 3. Execução Concorrente

O script aceita o número de núcleos como argumento via linha de comando:

```bash
py main_concorrente.py 2
py main_concorrente.py 4
py main_concorrente.py 8
py main_concorrente.py 12
```

> O resultado final é salvo automaticamente em `tabela_crimes_completa.md`.

---

# RELATÓRIO TÉCNICO: Mapeamento dos Maiores Índices Criminais por Seccional (São Paulo Capital)

**Contexto:** Entrega de Marco de Teste Empírico de Desempenho Computacional (Serial vs. Concorrente)

## 1. Descrição do Problema

Este documento detalha o experimento focado na extração estatística de dados de segurança pública da Capital de São Paulo (período de 2010 a Janeiro de 2017), cujo objetivo principal é **identificar e ranquear os 5 maiores crimes (coluna `RUBRICA`) de cada região administrativa (coluna `NOME_SECCIONAL_CIRC`)**.

### Questões Respondidas:
* **Objetivo do Programa:** Computar e isolar de forma exata o "Top 5" de ocorrências de cada Delegacia Seccional da capital paulista. O programa atua mitigando a replicação de B.O.s no R.D.O., realizando uma limpeza cruzada pelas chaves únicas `ID_DELEGACIA`, `ANO_BO` e `NUM_BO` para eliminar inflações estatísticas.
* **Volume de Dados:** Processamento de 21 arquivos CSV brutos dispostos em disco, totalizando múltiplos gigabytes de microdados criminais e milhões de linhas de registros.
* **Algoritmo Utilizado:** Divisão de carga em nível de dados (paradigma *MapReduce* adaptado). Trabalhadores (*workers*) assumem a leitura de arquivos CSV inteiros de forma assíncrona via `ProcessPoolExecutor`. O processo mestre centraliza os resultados, executa o filtro global de duplicidades e computa o agrupamento descendente.
* **Complexidade Aproximada:** A leitura e filtragem operam em complexidade linear $O(N)$. A ordenação final assume tempo de $O(M \log M)$, onde $M$ é o número de chaves únicas geradas.

---

## 2. Ambiente Experimental

| Item | Descrição |
| :--- | :--- |
| **Processador** | Intel Core (Multi-core de Alta Performance) |
| **Número de núcleos** | 12 núcleos lógicos |
| **Sistema Operacional** | Windows 11 |
| **Linguagem utilizada** | Python 3.13 |
| **Biblioteca de paralelização** | `concurrent.futures` (`ProcessPoolExecutor`) |

---

## 3. Metodologia de Testes

Os experimentos foram rigorosamente desenhados para capturar apenas o esforço de processamento e leitura dos dados, utilizando marcadores de tempo de alta precisão (`time.time()`).

### Configurações Testadas:
* **1 Processo (Versão Serial):** Loop tradicional sequencial varrendo a lista de 21 arquivos um por um em um único núcleo de CPU.
* **2, 4, 8 e 12 Processos (Versão Concorrente):** Instanciação controlada via `ProcessPoolExecutor`, forçando o sistema operacional a distribuir a carga entre múltiplos núcleos físicos simultaneamente.

---

## 4. Resultados Experimentais

Abaixo estão dispostos os tempos de execução reais obtidos na bateria de testes empíricos:

| Nº Processos | Tempo (s) | Speedup S(p) | Eficiência E(p) |
| :---: | :---: | :---: | :---: |
| **1 (Serial)** | 175,21 | 1,00× | 100,0% |
| **2** | 63,22 | 2,77× | 138,6% |
| **4** | 38,18 | 4,59× | 114,7% |
| **8** | 29,39 | 5,96× | 74,5% |
| **12** | 27,11 | 6,46× | 53,9% |

---

## 5. Cálculo de Speedup e Eficiência

### Speedup
$$Speedup(p) = \frac{T(1)}{T(p)}$$

### Eficiência
$$Eficiência(p) = \frac{Speedup(p)}{p} \times 100\%$$

### Exemplo — 4 núcleos:
$$Speedup(4) = \frac{175{,}21}{38{,}18} = 4{,}59\times$$
$$Eficiência(4) = \frac{4{,}59}{4} \times 100 = 114{,}7\%$$

---

## 6. Gráficos de Desempenho

N/A

---

## 7. Análise Crítica dos Resultados

A execução serial em Python puro demorou exaustivos **175,21 segundos** (quase 3 minutos), comprovando o impacto massivo de se processar milhões de registros de forma estritamente sequencial.

Ao introduzir a concorrência via `ProcessPoolExecutor`, observou-se uma redução expressiva e progressiva do tempo de execução à medida que o número de processos aumenta. Com **2 núcleos**, o tempo caiu para 63,22 segundos (Speedup de 2,77×). Com **4 núcleos**, atingiu 38,18 segundos (4,59×). Com **8 núcleos**, 29,39 segundos (5,96×). E com **12 núcleos**, o melhor resultado: **27,11 segundos (6,46×)**.

A eficiência acima de 100% observada em 2 e 4 núcleos não é um erro de medição — ela indica que a paralelização eliminou parte do overhead de I/O presente na versão serial (que processa um arquivo por vez e aguarda cada leitura terminar antes de iniciar a próxima). Com múltiplos processos, o sistema operacional consegue solapar a latência de leitura de disco entre os workers.

A partir de 8 núcleos, a eficiência cai para 74,5% e depois 53,9%, comportamento previsto pela **Lei de Amdahl**: o ganho paralelo é sempre limitado pela fração do problema intrinsecamente serial — neste caso, a etapa de desduplicação global e construção do ranking final, executadas em processo único pelo processo mestre.

Esse efeito de desaceleração gradual da eficiência comprova empiricamente que **adicionar núcleos indefinidamente não produz ganho proporcional** — a fração serial do código passa a ser o gargalo dominante.

---

## APÊNDICE: Extração Estatística Realizada

Abaixo constam os microdados consolidados gerados pelo algoritmo concorrente. Eles revelam o panorama real e as manchas criminais dominantes identificadas nas principais Seccionais da Capital Paulista durante o período amostral:

### Anomalias Administrativas Identificadas:
* **DECAP - SEDE:** Apresentou uma contagem isolada de apenas **2 ocorrências de Furto (art. 155)** em todo o período. Isso comprova o funcionamento perfeito do algoritmo de agrupamento, evidenciando que a sede administrativa não realiza registros de atendimento de rua, servindo apenas como centro de gestão policial.
* **DEMACRO - SEDE:** Apresentou apenas **1 ocorrência de Roubo (art. 157)**, pelo mesmo motivo acima.

### Manchas Criminais Dominantes por Zona Administrativa:
*(Os 5 Crimes Mais Relatados por Zona Administrativa — período 2010 a Jan/2017)*

| NOME_SECCIONAL_CIRC | RUBRICA | CONTAGEM |
| :--- | :--- | ---: |
| DECAP - SEDE | Furto (art. 155) | 2 |
| DEL.SEC.1º CENTRO | Furto (art. 155) | 462.534 |
| DEL.SEC.1º CENTRO | Roubo (art. 157) | 185.088 |
| DEL.SEC.1º CENTRO | Furto qualificado (art. 155, §4o.) | 72.930 |
| DEL.SEC.1º CENTRO | Lesão corporal (art. 129) | 33.307 |
| DEL.SEC.1º CENTRO | Lesão corporal culposa na direção de veículo automotor (Art. 303) | 30.862 |
| DEL.SEC.2º SUL | Roubo (art. 157) | 223.210 |
| DEL.SEC.2º SUL | Furto (art. 155) | 215.657 |
| DEL.SEC.2º SUL | Furto qualificado (art. 155, §4o.) | 51.033 |
| DEL.SEC.2º SUL | Lesão corporal (art. 129) | 27.290 |
| DEL.SEC.2º SUL | Lesão corporal culposa na direção de veículo automotor (Art. 303) | 25.902 |
| DEL.SEC.3º OESTE | Furto (art. 155) | 401.760 |
| DEL.SEC.3º OESTE | Roubo (art. 157) | 279.908 |
| DEL.SEC.3º OESTE | Furto qualificado (art. 155, §4o.) | 60.628 |
| DEL.SEC.3º OESTE | Lesão corporal culposa na direção de veículo automotor (Art. 303) | 45.423 |
| DEL.SEC.3º OESTE | Lesão corporal (art. 129) | 43.354 |
| DEL.SEC.4º NORTE | Furto (art. 155) | 250.977 |
| DEL.SEC.4º NORTE | Roubo (art. 157) | 201.594 |
| DEL.SEC.4º NORTE | Furto qualificado (art. 155, §4o.) | 52.091 |
| DEL.SEC.4º NORTE | Lesão corporal (art. 129) | 45.720 |
| DEL.SEC.4º NORTE | Lesão corporal culposa na direção de veículo automotor (Art. 303) | 40.103 |
| DEL.SEC.5º LESTE | Furto (art. 155) | 186.054 |
| DEL.SEC.5º LESTE | Roubo (art. 157) | 136.135 |
| DEL.SEC.5º LESTE | Furto qualificado (art. 155, §4o.) | 39.721 |
| DEL.SEC.5º LESTE | Lesão corporal (art. 129) | 22.796 |
| DEL.SEC.5º LESTE | Lesão corporal culposa na direção de veículo automotor (Art. 303) | 21.315 |
| DEL.SEC.6º SANTO AMARO | Roubo (art. 157) | 279.455 |
| DEL.SEC.6º SANTO AMARO | Furto (art. 155) | 230.409 |
| DEL.SEC.6º SANTO AMARO | Lesão corporal (art. 129) | 49.212 |
| DEL.SEC.6º SANTO AMARO | Lesão corporal culposa na direção de veículo automotor (Art. 303) | 34.691 |
| DEL.SEC.6º SANTO AMARO | Furto qualificado (art. 155, §4o.) | 31.324 |
| DEL.SEC.7º ITAQUERA | Roubo (art. 157) | 215.796 |
| DEL.SEC.7º ITAQUERA | Furto (art. 155) | 170.656 |
| DEL.SEC.7º ITAQUERA | Lesão corporal (art. 129) | 38.148 |
| DEL.SEC.7º ITAQUERA | Furto qualificado (art. 155, §4o.) | 26.035 |
| DEL.SEC.7º ITAQUERA | Lesão corporal culposa na direção de veículo automotor (Art. 303) | 24.043 |
| DEL.SEC.8º SAO MATEUS | Roubo (art. 157) | 186.221 |
| DEL.SEC.8º SAO MATEUS | Furto (art. 155) | 132.266 |
| DEL.SEC.8º SAO MATEUS | Furto qualificado (art. 155, §4o.) | 27.009 |
| DEL.SEC.8º SAO MATEUS | Lesão corporal (art. 129) | 26.878 |
| DEL.SEC.8º SAO MATEUS | Lesão corporal culposa na direção de veículo automotor (Art. 303) | 19.666 |
| DEL.SEC.CARAPICUIBA | Furto (art. 155) | 102.991 |
| DEL.SEC.CARAPICUIBA | Roubo (art. 157) | 81.429 |
| DEL.SEC.CARAPICUIBA | Lesão corporal (art. 129) | 37.407 |
| DEL.SEC.CARAPICUIBA | Lesão corporal culposa na direção de veículo automotor (Art. 303) | 36.621 |
| DEL.SEC.CARAPICUIBA | Lesão corporal (art 129 § 9º) | 16.439 |
| DEL.SEC.DIADEMA | Roubo (art. 157) | 75.596 |
| DEL.SEC.DIADEMA | Furto (art. 155) | 41.005 |
| DEL.SEC.DIADEMA | Lesão corporal (art. 129) | 10.102 |
| DEL.SEC.DIADEMA | Lesão corporal culposa na direção de veículo automotor (Art. 303) | 8.271 |
| DEL.SEC.DIADEMA | Furto qualificado (art. 155, §4o.) | 7.789 |
| DEL.SEC.FRANCO DA ROCHA | Furto (art. 155) | 40.538 |
| DEL.SEC.FRANCO DA ROCHA | Roubo (art. 157) | 25.094 |
| DEL.SEC.FRANCO DA ROCHA | Lesão corporal (art. 129) | 24.359 |
| DEL.SEC.FRANCO DA ROCHA | Lesão corporal culposa na direção de veículo automotor (Art. 303) | 10.265 |
| DEL.SEC.FRANCO DA ROCHA | Furto qualificado (art. 155, §4o.) | 5.231 |
| DEL.SEC.GUARULHOS | Furto (art. 155) | 132.860 |
| DEL.SEC.GUARULHOS | Roubo (art. 157) | 114.051 |
| DEL.SEC.GUARULHOS | Lesão corporal culposa na direção de veículo automotor (Art. 303) | 30.743 |
| DEL.SEC.GUARULHOS | Lesão corporal (art. 129) | 30.691 |
| DEL.SEC.GUARULHOS | Furto qualificado (art. 155, §4o.) | 25.431 |
| DEL.SEC.MOGI DAS CRUZES | Furto (art. 155) | 116.845 |
| DEL.SEC.MOGI DAS CRUZES | Roubo (art. 157) | 90.416 |
| DEL.SEC.MOGI DAS CRUZES | Lesão corporal (art. 129) | 37.724 |
| DEL.SEC.MOGI DAS CRUZES | Furto qualificado (art. 155, §4o.) | 25.518 |
| DEL.SEC.MOGI DAS CRUZES | Lesão corporal culposa na direção de veículo automotor (Art. 303) | 22.985 |
| DEL.SEC.OSASCO | Furto (art. 155) | 89.235 |
| DEL.SEC.OSASCO | Roubo (art. 157) | 76.880 |
| DEL.SEC.OSASCO | Lesão corporal culposa na direção de veículo automotor (Art. 303) | 17.000 |
| DEL.SEC.OSASCO | Lesão corporal (art. 129) | 15.104 |
| DEL.SEC.OSASCO | Furto qualificado (art. 155, §4o.) | 13.777 |
| DEL.SEC.S.BERNARDO DO CAMPO | Furto (art. 155) | 128.988 |
| DEL.SEC.S.BERNARDO DO CAMPO | Roubo (art. 157) | 126.511 |
| DEL.SEC.S.BERNARDO DO CAMPO | Furto qualificado (art. 155, §4o.) | 27.805 |
| DEL.SEC.S.BERNARDO DO CAMPO | Lesão corporal (art. 129) | 22.787 |
| DEL.SEC.S.BERNARDO DO CAMPO | Lesão corporal culposa na direção de veículo automotor (Art. 303) | 21.147 |
| DEL.SEC.SANTO ANDRÉ | Roubo (art. 157) | 151.984 |
| DEL.SEC.SANTO ANDRÉ | Furto (art. 155) | 150.583 |
| DEL.SEC.SANTO ANDRÉ | Furto qualificado (art. 155, §4o.) | 33.961 |
| DEL.SEC.SANTO ANDRÉ | Lesão corporal (art. 129) | 28.212 |
| DEL.SEC.SANTO ANDRÉ | Lesão corporal culposa na direção de veículo automotor (Art. 303) | 25.280 |
| DEL.SEC.TABOÃO DA SERRA | Roubo (art. 157) | 70.300 |
| DEL.SEC.TABOÃO DA SERRA | Furto (art. 155) | 51.716 |
| DEL.SEC.TABOÃO DA SERRA | Lesão corporal (art. 129) | 19.721 |
| DEL.SEC.TABOÃO DA SERRA | Lesão corporal culposa na direção de veículo automotor (Art. 303) | 13.478 |
| DEL.SEC.TABOÃO DA SERRA | Furto qualificado (art. 155, §4o.) | 10.329 |
| DEMACRO - SEDE | Roubo (art. 157) | 1 |

> **Nota Metodológica:** A gritante dominância quantitativa de furtos e roubos em detrimento de crimes violentos contra a vida reforça a assinatura típica de grandes metrópoles, onde o crime patrimonial opera em escala massiva e dita as diretrizes de policiamento ostensivo nas sub-regiões mapeadas.

---
