# Inteligência Criminal em Larga Escala: Programação Serial vs. Concorrente


**Disciplina:** Programação Concorrente
**Aluno:** Arthur Dias e Victor Hugo
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
* **Manipulação de Dados Massivos:** `pandas` (leitura em *chunks* otimizada via *low_memory*)
* **Gerenciamento de Sistema:** `os`, `time`, `glob`
* **Plotagem de Gráficos (Relatórios):** `matplotlib`

---

##  Estrutura de Execução

### 1. Preparação do Ambiente
O volume de dados exige armazenamento local. Crie a pasta `dados/` na raiz do projeto e deposite todos os arquivos `.csv` oriundos do dataset original do Kaggle.

    # Instalação das dependências necessárias para manipulação e plotagem de dados
    pip install pandas matplotlib tabulate

### 2. A Bateria de Testes (*Benchmarks*)
O repositório conta com *scripts* isolados para a aferição de métricas. O motor principal de paralelização pode ser submetido a testes de carga utilizando:

    python main_benchmark.py

> *A saída deste script gera a relação de tempo bruto associada a cargas progressivas de 1, 2, 4, 8 e 12 processos simultâneos.*

---

##  Entregáveis e Subprojetos

Este repositório principal subdivide as extrações de dados em relatórios técnicos específicos, que atuam como "capítulos" práticos do trabalho.

**Entregas Concluídas:**

* **[ Mapeamento dos Maiores Índices Criminais por Seccional](maiorescrimesreadme.md)** - Focado na validação do *speedup* da máquina e no cálculo de domínio dos 5 maiores delitos patrimoniais e contra a vida mapeados na infraestrutura do DECAP.

(**Próximos Passos (Backlog de Análises):**

* Implementação de rotinas para cruzamento vitimológico (Gênero vs. Rubrica de Risco).
* Mapeamento de Horários Críticos cruzados por Região.)
