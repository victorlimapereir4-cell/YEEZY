# 📊 Capítulo: Mapeamento dos Maiores Índices Criminais por Seccional (São Paulo Capital)
## Relatório Técnico de Desempenho Computacional (Serial vs. Concorrente)

**Disciplina:** Programação Concorrente  
**Aluno:** Arthur Dias e Victor Hugo  
**Curso:** Análise e Desenvolvimento de Sistemas (ADS)  
**Contexto:** Entrega de Marco de Teste Empírico  

---

# 1. Descrição do Problema

Este documento detalha o experimento focado na extração estatística de dados de segurança pública da Capital de São Paulo (período de 2010 a Janeiro de 2017), cujo objetivo principal é **identificar e ranquear os 5 maiores crimes (coluna `RUBRICA`) de cada região administrativa (coluna `NOME_SECCIONAL_CIRC`)**.

### Questões Respondidas:
* **Objetivo do Programa:** Computar e isolar de forma exata o "Top 5" de ocorrências de cada Delegacia Seccional da capital paulista. O programa atua mitigando uma característica do sistema R.D.O. (Registro Digital de Ocorrências): boletins com múltiplas vítimas geram linhas replicadas no banco de dados. O algoritmo realiza uma limpeza pesada (*data cleansing*) cruzando as chaves únicas `ID_DELEGACIA`, `ANO_BO` e `NUM_BO` para eliminar inflações estatísticas antes de computar o ranking.
* **Volume de Dados:** Processamento de 22 arquivos CSV brutos dispostos em disco, totalizando múltiplos gigabytes de microdados criminais e milhões de linhas de registros históricos.
* **Algoritmo Utilizado:** Divisão de carga em nível de dados (paradigma *MapReduce* adaptado). Cada trabalhador (*worker*) assume a leitura e higienização de arquivos CSV inteiros em lotes de memória (*chunks* de 150.000 linhas) de forma assíncrona. A thread mestre centraliza os dataframes limpos, executa um filtro global de duplicidades remanescentes inter-arquivos, computa o agrupamento ponderado (`groupby`) e aplica uma ordenação descendente seccionada (`head(5)`).
* **Complexidade Aproximada:** A leitura e filtragem operam em complexidade linear $O(N)$ em relação ao número total de registros válidos. A etapa de ordenação final dos subgrupos regionais assume complexidade de tempo de $O(M \log M)$, onde $M$ é o número de chaves únicas geradas após o agrupamento de cidades e rubricas.

---

# 2. Ambiente Experimental

As características do ecossistema computacional utilizado para a execução das baterias de testes seriais e paralelos estão descritas abaixo:

| Item | Descrição |
| :--- | :--- |
| **Processador** | Intel Core i7 / AMD Ryzen (Multi-core de Alta Performance) |
| **Número de núcleos** | Múltiplos núcleos físicos com suporte a threads lógicas simultâneas |
| **Memória RAM** | 32 GB |
| **Sistema Operacional** | Windows 11 |
| **Linguagem utilizada** | Python 3.13.7  |
| **Biblioteca de paralelização** | `concurrent.futures` (`ProcessPoolExecutor`) |
| **Manipulação de Dados** | `pandas` (com gerenciamento de tipos otimizado em nível de I/O) |

---

# 3. Metodologia de Testes

Os experimentos foram rigorosamente desenhados para capturar apenas o esforço de processamento e leitura dos dados, utilizando marcadores de tempo de alta precisão (`time.time()`) posicionados imediatamente antes do mapeamento de arquivos e parados logo após a consolidação final do Top 5 em memória.

### Configurações Testadas:
* **1 Processo (Versão Serial):** Loop tradicional sequencial varrendo a lista de 22 arquivos um por um em um único núcleo de CPU.
* **2, 4, 8 e 12 Processos (Versão Concorrente):** Instanciação controlada através do parâmetro `max_workers`, forçando o sistema operacional a gerenciar a concorrência e a distribuição de arquivos de forma simultânea entre os núcleos.

### Procedimento Experimental:
Cada configuração passou por execuções repetidas para extração da média aritmética simples dos tempos. A pasta de dados continha o acervo bruto de microdados criminais descompactados, garantindo que o tempo mensurado refletisse o mundo real do processamento de dados massivos de segurança de forma justa.

---

# 4. Resultados Experimentais

Abaixo estão dispostos os **tempos médios de execução** obtidos na bateria de testes empíricos do projeto:

| Nº Threads/Processos | Tempo de Execução (s) |
| :---: | :---: |
| **1 (Serial)** | 59.47 |
| **2** | 34.86 |
| **4** | 22.29 |
| **8** | 18.50 |
| **12** | 17.20 |

---

# 5. Cálculo de Speedup e Eficiência

As métricas de ganho de desempenho foram extraídas com base nas formulações matemáticas clássicas da computação paralela:

### Speedup
$$Speedup(p) = \frac{T(1)}{T(p)}$$
Onde $T(1)$ representa o tempo gasto pelo algoritmo puramente sequencial e $T(p)$ o tempo gasto com $p$ processos em execução paralela.

### Eficiência
$$Eficiência(p) = \frac{Speedup(p)}{p}$$
Métrica que indica a taxa de aproveitamento real de cada núcleo adicionado ao problema computacional. Os valores variam em escala de 0 a 1.

---

# 6. Tabela de Resultados Consolidados

Utilizando os tempos coletados durante as execuções, a tabela consolidada de desempenho apresenta o seguinte comportamento:

| Threads/Processos | Tempo (s) | Speedup | Eficiência |
| :---: | :---: | :---: | :---: |
| **1 (Serial)** | 59.47 | 1.00 | 1.00 |
| **2** | 34.86 | 1.71 | 0.85 |
| **4** | 22.29 | 2.67 | 0.67 |
| **8** | 18.50 | 3.21 | 0.40 |
| **12** | 17.20 | 3.46 | 0.29 |

---

# 7. Gráficos de Desempenho

### Gráfico 1: Tempo de Execução em Função do Número de Processos
*(Eixo X: Número de Processos | Eixo Y: Tempo de Execução em Segundos)* ![Gráfico Tempo Execução](graficos/tempo_execucao.png)

### Gráfico 2: Speedup Obtido vs. Speedup Ideal (Linear)
*(Eixo X: Número de Processos | Eixo Y: Fator de Aceleração Speedup)* ![Gráfico Speedup](graficos/speedup.png)

### Gráfico 3: Curva de Caimento da Eficiência da Paralelização
*(Eixo X: Número de Processos | Eixo Y: Eficiência entre 0 e 1)* ![Gráfico Eficiência](graficos/eficiencia.png)

---

# 10. Análise Crítica dos Resultados

* **Análise do Speedup:** O ganho de velocidade foi imediato e expressivo ao abandonar a arquitetura de processamento serial. Com 2 processos, o algoritmo reduziu o tempo para 34.86s. A melhor relação de escalabilidade ocorreu com **4 processos**, reduzindo o tempo original em mais da metade (22.29s) com uma aceleração real de 2.67x.
* **O Ponto de Inflexão da Eficiência:** A eficiência do sistema começou a sofrer uma degradação severa a partir de 8 processos. Embora o tempo absoluto tenha caído para 18.50s, a eficiência caiu para 40%. Ao testar o limite de 12 processos, o ganho de tempo foi insignificante (apenas 1.30 segundo mais rápido que o teste com 8), fazendo com que a eficiência despencasse para 29%.
* **Identificação de Gargalos Computacionais:** 1. **Saturação de I/O de Disco (Gargalo Principal):** Como estamos lidando com gigabytes de dados espalhados em dezenas de arquivos, o barramento de leitura física do armazenamento satura rapidamente. Adicionar mais processos de CPU a partir de um certo ponto não acelera a velocidade com que o disco local extrai as linhas textuais dos arquivos.
  2. **Overhead de Serialização (IPC no Python):** A arquitetura do Python requer o uso de múltiplos processos (e não threads puras) para contornar o *Global Interpreter Lock (GIL)*. Isso gera um custo (*overhead*) adaptativo alto, pois os blocos de dados gerados em cada núcleo precisam ser serializados via protocolo *Pickle* para trafegar na memória até o processo pai unificador.
  3. **Lei de Amdahl:** A fração puramente serial do programa (o agrupamento mestre final e a eliminação de duplicidades inter-arquivos na thread principal) limita o speedup máximo atingível, conforme previsto teoricamente na disciplina.

---

# 11. Conclusão

A aplicação do processamento paralelo provou ser uma solução robusta e indispensável para a manipulação de dados de segurança pública em larga escala. Sair de uma rotina sequencial engessada de quase um minuto para uma resposta consolidada de toda a malha criminal de São Paulo em apenas 17.20 segundos abre portas para o desenvolvimento de ferramentas ágeis voltadas ao planejamento estratégico de viaturas e otimização de prontas-respostas operacionais.

O ponto ótimo de operação computacional na máquina de testes localizou-se na faixa de **4 processos simultâneos**, equilibrando perfeitamente a aceleração temporal (2.67x) com o nível de eficiência energética e de hardware (67%). Como evolução direta da implementação, sugere-se a migração do armazenamento em arquivos CSV textuais para sistemas de bancos de dados relacionais indexados ou estruturas NoSQL com suporte nativo a consultas paralelas distribuídas, extinguindo o gargalo de leitura mecânica local.

---

# 📋 APÊNDICE: Extração Estatística Realizada

Abaixo constam os microdados consolidados gerados pelo algoritmo concorrente. Eles revelam o panorama real e as manchas criminais dominantes identificadas nas principais Seccionais da Capital Paulista durante o período amostral:

### Anomalias Administrativas Identificadas:
* **DECAP - SEDE:** Apresentou uma contagem isolada de apenas **2 ocorrências de Furto (art. 155)** em todo o período. Isso comprova o funcionamento perfeito do algoritmo de agrupamento, evidenciando que a sede administrativa não realiza registros de atendimento de rua, servindo apenas como centro de gestão policial. As raras incidências decorrem de registros de patrimônio interno ou desvios de preenchimento.

### Manchas Criminais Dominantes por Zona Administrativa:
    (Os 5 Crimes Mais Relatados por Zona Administrativa:)

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

Nota Metodológica: A gritante dominância quantitativa de furtos e roubos em detrimento de crimes violentos contra a vida reforça a assinatura típica de grandes metrópoles, onde o crime patrimonial opera em escala massiva e dita as diretrizes de policiamento ostensivo nas sub-regiões mapeadas.
