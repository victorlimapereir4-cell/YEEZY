# Roteiro de Apresentação
**Inteligência Criminal em Larga Escala: Serial vs. Concorrente**
Arthur Dias & Victor Hugo — ~8 minutos no total

---

## SLIDE 1 — Capa | Arthur | ~30s

> "Boa tarde. Nosso trabalho analisa quanto a programação concorrente acelera o processamento de milhões de registros criminais de São Paulo. Eu vou apresentar o problema e a arquitetura, e o Victor traz os resultados e a análise."

---

## SLIDE 2 — O Problema | Arthur | ~1min

> "Trabalhamos com 22 arquivos CSV do sistema R.D.O. da SSP-SP, cobrindo 2010 a 2017. O desafio tem duas camadas: primeiro, o dado bruto vem duplicado — um mesmo boletim aparece várias vezes quando há múltiplas vítimas. Segundo, processar milhões de linhas sequencialmente é lento. Nosso objetivo foi extrair o Top 5 de crimes por região com precisão total e medir o ganho real da concorrência."

---

## SLIDE 3 — Arquitetura | Arthur | ~1min

> "A restrição do professor foi clara: Python Puro, sem pandas, sem banco de dados. Isso foi intencional — com pandas o motor interno roda em C e mascara o ganho da concorrência. Na versão serial, um loop simples lê um arquivo por vez. Na concorrente, o ProcessPoolExecutor distribui os arquivos entre processos reais, contornando o GIL do Python. Cada processo limpa e deduplica sua parte. O processo mestre faz o merge final."

---

## SLIDE 4 — Resultados | Victor | ~1min30s

> "Aqui estão os dados coletados. A versão serial levou 175 segundos. Com 2 núcleos, já caímos para 63 — quase três vezes mais rápido. Com 4, chegamos a 38 segundos. O gráfico mostra a curva de queda: o ganho é expressivo no início e vai desacelerando conforme adicionamos mais núcleos. Com 12, atingimos 27 segundos — uma redução de 84% em relação ao serial."

---

## SLIDE 5 — Lei de Amdahl | Victor | ~1min30s

> "O gráfico aqui compara nosso speedup real com o ideal linear. Se tudo fosse paralelizável, 12 núcleos dariam 12× de aceleração. Obtivemos 6,46×. A diferença existe porque uma parte do código é intrinsecamente serial: a etapa de deduplicação global e construção do ranking roda em processo único. Calculamos pela Lei de Amdahl que cerca de 92% do processamento é paralelizável — e esses ~8% seriais são o teto que nos impede de escalar indefinidamente."

---

## SLIDE 6 — Resultado Criminal | Victor | ~1min

> "Além do benchmark, o sistema gerou o resultado criminal real. Em todas as 17 seccionais analisadas, o padrão é consistente: Furto e Roubo dominam o Top 2. O maior volume está no 1º Centro, com 462 mil registros únicos de furto em 7 anos. Dois casos validam o algoritmo: DECAP-Sede com 2 ocorrências e DEMACRO-Sede com 1 — são sedes administrativas que não realizam atendimento de rua, então faz todo sentido terem quase zero registros."

---

## SLIDE 7 — Conclusão | Arthur | ~45s

> "Pra fechar: a concorrência em Python exige processos reais, não threads, por causa do GIL. Com isso reduzimos 175 segundos para 27 — 84% de melhora. Mas a Lei de Amdahl é implacável: a parte serial do código impede escalar além de 6,46×. O projeto validou empiricamente o que a teoria prevê. Ficamos à disposição para perguntas."

---

## Possíveis Perguntas

**"Por que não usaram threads em vez de processos?"**
> O GIL do Python impede que threads executem código Python em paralelo real para tarefas de CPU. Processos separados têm cada um seu próprio interpretador, contornando isso.

**"Por que a eficiência passou de 100% com 2 e 4 núcleos?"**
> Na versão serial, os arquivos são lidos um a um — o processo aguarda cada leitura terminar antes de começar a próxima. Com múltiplos processos, o sistema operacional solapou a latência de leitura entre eles, eliminando esse overhead.

**"O que limitaria ainda mais o speedup se usassem mais núcleos?"**
> A fração serial do merge global. Por mais núcleos que adicionemos na leitura, o processo mestre ainda precisa rodar a deduplicação e o ranking em processo único. A Lei de Amdahl prevê que com ~8% serial, o speedup máximo teórico absoluto é de 12,5×, independentemente do número de núcleos.
