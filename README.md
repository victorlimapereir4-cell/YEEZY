# Relatório da Atividade: Extração de Estatísticas Criminais

**Disciplina:** Programação Concorrente
**Aluno:** Arthur Dias e Victor Hugo
**Instituição:** Centro Universitário Unieuro
**Curso:** Análise e Desenvolvimento de Sistemas (ADS)
**Data:** 22 de Maio de 2026

---

# 1. Descrição do Problema

O problema computacional resolvido neste projeto consiste no processamento massivo de microdados de segurança pública para extrair inteligência tática. O objetivo é ler o dataset "Crime Data in Brazil" (baseado no SINESP), mapear as tipificações criminais (`RUBRICA`) por município (`CIDADE`), filtrar registros inválidos através da coluna `FLAG_STATUS` e retornar o "Top 5" dos crimes mais frequentes para cada localidade.

A extração dessa métrica é custosa computacionalmente devido ao alto volume de linhas, exigindo varredura completa do arquivo, validação, agrupamento e ordenação. A paralelização foi aplicada visando fragmentar o banco de dados em lotes (*chunks*), permitindo que múltiplos núcleos do processador realizem o filtro e a contagem parcial simultaneamente, mitigando o gargalo de I/O e processamento. O algoritmo possui complexidade assintótica aproximada de $O(N \log N)$ na fase de ordenação do agrupamento final, onde $N$ representa o volume total de ocorrências válidas.

---

# 2. Ambiente Experimental

Os testes foram conduzidos na seguinte arquitetura:

| Item                        | Descrição |
| --------------------------- | --------- |
| Processador                 | 6-Core Processor |
| Número de núcleos           | [Ex: 8 núcleos físicos / 16 lógicos] |
| Memória RAM                 | 32,0 GB |
| Sistema Operacional         | Windows  |
| Linguagem utilizada         | Python 3.13.7 |
| Biblioteca de paralelização | `concurrent.futures` (ProcessPoolExecutor) e `pandas` |
| Compilador / Versão         | -CPython 3.10]- |

---

# 3. Metodologia de Testes

O tempo de execução foi aferido via software utilizando a biblioteca nativa `time`, capturando o *timestamp* imediatamente antes da alocação do arquivo em memória e logo após a obtenção do dataframe final já ordenado com o Top 5.

O arquivo original possui mais de [Inserir total de linhas, aprox. milhões] de registros. Para otimização de memória, a leitura foi particionada em lotes de 100.000 linhas.

### Configurações testadas

Os experimentos foram padronizados nas seguintes configurações:

* 1 thread/processo (versão serial)
* 2 threads/processos
* 4 threads/processos
* 8 threads/processos
* 12 threads/processos *(Testado via limitação de workers no executor)*

### Procedimento experimental

Foram realizadas [Ex: 5] execuções completas para cada configuração de concorrência. O tempo documentado nos resultados consiste na média aritmética simples dessas execuções, descartando anomalias causadas por picos de interferência do SO. A máquina operou em ambiente isolado, com encerramento prévio de aplicações em segundo plano para reduzir a disputa de uso de disco e CPU.

---

# 4. Resultados Experimentais

| Nº Threads/Processos | Tempo de Execução (s) |
| -------------------- | --------------------- |
| 1                    | [Preencher]           |
| 2                    | [Preencher]           |
| 4                    | [Preencher]           |
| 8                    | [Preencher]           |
| 12                   | [Preencher]           |

---

# 5. Cálculo de Speedup e Eficiência

## Fórmulas Utilizadas

### Speedup
Speedup(p) = T(1) / T(p)
Onde:
* **T(1)** = tempo da execução serial
* **T(p)** = tempo com p processos

### Eficiência
Eficiência(p) = Speedup(p) / p
Onde:
* **p** = número de processos

---

# 6. Tabela de Resultados

| Threads/Processos | Tempo (s) | Speedup     | Eficiência |
| ----------------- | --------- | ----------- | ---------- |
| 1                 | [Preencher]| 1.0        | 1.0        |
| 2                 | [Preencher]| [Calcular] | [Calcular] |
| 4                 | [Preencher]| [Calcular] | [Calcular] |
| 8                 | [Preencher]| [Calcular] | [Calcular] |
| 12                | [Preencher]| [Calcular] | [Calcular] |

---

# 7. Gráfico de Tempo de Execução
*(Substituir pelo seu gráfico gerado nas planilhas)*

![Gráfico Tempo Execução](graficos/tempo_execucao.png)

---

# 8. Gráfico de Speedup
*(Substituir pelo seu gráfico gerado nas planilhas)*

![Gráfico Speedup](graficos/speedup.png)

---

# 9. Gráfico de Eficiência
*(Substituir pelo seu gráfico gerado nas planilhas)*

![Gráfico Eficiência](graficos/eficiencia.png)

---

# 10. Análise dos Resultados

[**Nota:** *Abaixo estão os guias para você preencher após rodar os testes*]

* **Speedup e Escalabilidade:** [Discutir se o tempo diminuiu pela metade ao dobrar os processos, ou se houve um platô].
* **Eficiência:** [Comentar em qual número de processos a eficiência começou a cair drasticamente].
* **Overhead:** A criação de processos na linguagem Python possui um custo computacional considerável (overhead) devido à necessidade de serializar (Pickle) os blocos de dados entre a memória do processo principal e os trabalhadores.
* **Gargalos:** O principal gargalo da aplicação demonstrou ser o I/O (leitura do disco rígido). Mesmo que múltiplos processadores estejam agrupando os dados rapidamente, eles ainda dependem da velocidade de leitura mecânica/sólida do armazenamento local para extrair os arquivos do CSV.

O algoritmo foi modelado para contornar uma falha estrutural do sistema R.D.O. (Registro Digital de Ocorrências), onde boletins com múltiplas vítimas geram linhas duplicadas. A concorrência atua na limpeza pesada (data cleansing) intra-lotes de milhares de linhas simultaneamente, enquanto a thread principal realiza a consolidação final das chaves únicas (ID_DELEGACIA, ANO_BO e NUM_BO), garantindo a integridade da estatística sem comprometer o tempo de execução.

---

# 11. Conclusão

[**Nota:** *Preencher com sua visão final*]

A aplicação do paralelismo em nível de dados (SIMD/SPMD) mostrou-se extremamente pertinente para a extração de inteligência em ocorrências criminais. A divisão do trabalho permitiu agrupar a dinâmica de milhares de municípios de forma muito mais célere do que o gargalo de processamento único.

Como melhoria futura de implementação e aplicação de arquitetura para pronto-resposta, os dados brutos poderiam ser alocados em bancos estruturados distribuídos e consultados paralelamente, eliminando o custo de I/O de um arquivo CSV pesado na máquina local.
