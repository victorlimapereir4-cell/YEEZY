# Relatório de Atividade: Programação Concorrente

**Disciplina:** Programação Concorrente
**Aluno:** Arthur Vitor Almeida Dias
**Instituição:** Centro Universitário Unieuro
**Curso:** Análise e Desenvolvimento de Sistemas (ADS)
**Data:** 09 de Maio de 2026

---

# 1. Descrição do Problema

Este trabalho aborda a paralelização do algoritmo **K-Means Clustering** aplicado ao dataset **CICIDS2017**. O problema consiste em agrupar milhões de fluxos de rede para identificar padrões de comportamento (anomalias e intrusões).

* **Algoritmo:** K-Means Iterativo com Redução Global.
* **Volume de Dados:** Matriz de **2.520.751 linhas x 52 colunas** (~2.5 GB em memória).
* **Objetivo:** Reduzir o tempo de processamento matemático utilizando o padrão de *Data Parallelism* e avaliar os limites de escalabilidade do hardware.

---

# 2. Ambiente Experimental

| Item                        | Descrição |
| --------------------------- | --------- |
| Processador                 | CPU Multicore (Capacidade de até 12 threads) |
| Memória RAM                 | 16 GB+ (Necessário para alocação do dataset CICIDS2017) |
| Sistema Operacional         | Windows / Linux |
| Linguagem utilizada         | Python 3.10+ |
| Biblioteca de paralelização | `multiprocessing` |

---

# 3. Metodologia de Testes

Os testes foram realizados isolando o tempo de **CPU (Processamento)** do tempo de **I/O (Leitura)**. O cronômetro foi acionado apenas após a carga completa dos dados na RAM.

* **Métricas:** Tempo de Execução (s), Speedup e Eficiência.
* **Cargas Testadas:** 1, 2, 4, 8 e 12 processos.
* **Iterações:** 10 iterações globais para cada teste.

---

# 4. Resultados Experimentais

| Nº Processos | Tempo de Execução (s) |
| :----------: | :-------------------: |
| 1 (Serial)   | 82.98                 |
| 2            | 61.79                 |
| 4            | 53.07                 |
| 8            | 37.16                 |
| 12           | 37.13                 |

---

# 5. Cálculo de Speedup e Eficiência

| Processos | Tempo (s) | Speedup | Eficiência |
| :-------: | :-------: | :-----: | :--------: |
| 1         | 82.98     | 1.00x   | 1.00       |
| 2         | 61.79     | 1.34x   | 0.67       |
| 4         | 53.07     | 1.56x   | 0.39       |
| 8         | 37.16     | 2.23x   | 0.28       |
| 12        | 37.13     | 2.23x   | 0.19       |

---

# 6. Análise dos Resultados

A análise dos dados revela três pontos críticos:

1.  **Gargalo de Comunicação (Overhead):** A eficiência cai de 100% para 67% ao dobrar os processos. Isso ocorre devido ao custo de serialização (Pickle) e comunicação entre processos em Python.
2.  **Saturação de Barramento:** O tempo entre 8 e 12 processos foi praticamente idêntico. Isso indica que o sistema atingiu o **limite de largura de banda de memória**, onde a RAM não consegue entregar dados mais rápido do que os núcleos processam.
3.  **Lei de Amdahl:** A parte serial do código (sincronização de centroides no fim de cada iteração) limita o speedup máximo possível, impedindo um ganho linear.

---

# 7. Conclusão

O paralelismo trouxe um ganho real de **2.23x** de velocidade. O "ponto ideal" para este hardware foi de **8 processos**. Acima disso, o custo de gerenciar novos processos anula o ganho computacional.

