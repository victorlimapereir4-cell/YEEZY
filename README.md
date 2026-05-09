# Relatório de Atividade: Programação Concorrente

**Disciplina:** Programação Concorrente
**Aluno:** Arthur Dias e Victor Hugo
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
| Processador                 | 6-Core Processor |
| Memória RAM                 | 32,0 GB |
| Sistema Operacional         | Windows  |
| Linguagem utilizada         | Python 3.13.7 |
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

A aplicação demonstrou um comportamento clássico de paralelização de carga de matrizes pesadas, com pontos altos e restrições de arquitetura visíveis:

1) **A Escalabilidade:** O sistema escalou bem inicialmente, reduzindo o tempo de execução de 82.98s (Serial) para 37.15s (8 Processos). O Speedup máximo obtido (2.23x) esteve abaixo do ideal teórico linear, o que é esperado em algoritmos iterativos (como o K-Means), pois a etapa de Redução Global e a Sincronização por Barreira criam gargalos seriais impossíveis de paralelizar (Lei de Amdahl).

2) **O Declínio da Eficiência:** A eficiência começou a cair drasticamente logo na transição para 4 processos (atingindo 39%). Esse fenômeno é causado diretamente pelo Overhead de IPC (Inter-Process Communication). A biblioteca do Python necessita realizar a cópia e serialização das matrizes entre os trabalhadores, consumindo tempo valioso do sistema operacional.

3) **A Saturação de Hardware:** O ponto mais importante do experimento reside na transição de 8 para 12 processos, onde o tempo foi estritamente igual (~37.1 segundos), zerando o ganho de Speedup e afundando a eficiência para 18.6%. A principal causa técnica para este platô é o estrangulamento da largura de banda da memória (Memory Bandwidth Bottleneck). Os núcleos da CPU passaram a computar a matemática mais rápido do que a memória RAM conseguia entregar as fatias da matriz de 52 dimensões. Ademais, o chaveamento de contexto no agendador do SO para gerenciar 12 processos gerou uma contenção que anulou a adição dos novos núcleos.
---

# 7. Conclusão

O paralelismo trouxe um ganho real de **2.23x** de velocidade. O "ponto ideal" para este hardware foi de **8 processos**. Acima disso, o custo de gerenciar novos processos anula o ganho computacional.

