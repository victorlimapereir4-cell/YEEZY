import csv
import time
import glob
import os
import sys
from concurrent.futures import ProcessPoolExecutor, as_completed
from collections import defaultdict

# =============================================================
# TEMPO SERIAL DE REFERÊNCIA (coletado empiricamente no lab)
# Usado para calcular Speedup e Eficiência automaticamente
# =============================================================
TEMPO_SERIAL_REFERENCIA = 175.21  # segundos


def processar_arquivo_puro(caminho_arquivo):
    """
    Processa um único arquivo CSV de forma isolada (roda em processo filho).
    Filtra metadados, valida colunas essenciais e deduplica BOs localmente.
    Retorna lista de tuplas (id_del, ano_bo, num_bo, seccional, rubrica).
    """
    if "description" in caminho_arquivo.lower() or "methodology" in caminho_arquivo.lower():
        return []

    registros_validos = []
    vistos_local = set()

    try:
        with open(caminho_arquivo, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                id_del   = row.get('ID_DELEGACIA')
                ano_bo   = row.get('ANO_BO')
                num_bo   = row.get('NUM_BO')
                seccional = row.get('NOME_SECCIONAL_CIRC')
                rubrica  = row.get('RUBRICA')

                # RN002 – descartar linhas com campos essenciais nulos
                if not (id_del and ano_bo and num_bo and seccional and rubrica):
                    continue

                # RF002 – desduplicação local (múltiplas vítimas no mesmo BO)
                chave_bo = (id_del, ano_bo, num_bo)
                if chave_bo in vistos_local:
                    continue
                vistos_local.add(chave_bo)

                registros_validos.append((id_del, ano_bo, num_bo, seccional, rubrica))

    except Exception as e:
        print(f"  [ERRO] Falha ao ler '{caminho_arquivo}': {e}")

    return registros_validos


def exibir_progresso(atual, total, inicio):
    """Barra de progresso simples no terminal."""
    pct = atual / total * 100
    elapsed = time.time() - inicio
    barra = "█" * int(pct // 5) + "░" * (20 - int(pct // 5))
    print(f"\r  [{barra}] {pct:5.1f}%  ({atual}/{total} arquivos)  {elapsed:.1f}s", end="", flush=True)


def main():
    # ----------------------------------------------------------
    # 1. DESCOBERTA DE ARQUIVOS
    # ----------------------------------------------------------
    arquivos_csv = glob.glob(os.path.join('dados', '*.csv'))
    if not arquivos_csv:
        print("[ERRO] Nenhum arquivo CSV encontrado na pasta 'dados/'.")
        sys.exit(1)

    # Filtra metadados logo na descoberta (RN001)
    arquivos_csv = [
        a for a in arquivos_csv
        if "description" not in a.lower() and "methodology" not in a.lower()
    ]

    total_arquivos = len(arquivos_csv)

    # ----------------------------------------------------------
    # 2. NÚMERO DE NÚCLEOS (CLI ou máximo disponível)
    # ----------------------------------------------------------
    if len(sys.argv) > 1:
        try:
            nucleos = int(sys.argv[1])
        except ValueError:
            print("[AVISO] Argumento inválido. Usando máximo de núcleos disponíveis.")
            nucleos = None
    else:
        nucleos = None

    nucleos_display = nucleos if nucleos else os.cpu_count()

    # ----------------------------------------------------------
    # 3. CABEÇALHO
    # ----------------------------------------------------------
    print()
    print("=" * 65)
    print("  INTELIGÊNCIA CRIMINAL — PROCESSAMENTO CONCORRENTE")
    print("=" * 65)
    print(f"  Arquivos encontrados : {total_arquivos}")
    print(f"  Núcleos solicitados  : {nucleos_display}")
    print(f"  CPU disponível       : {os.cpu_count()} núcleos lógicos")
    print("=" * 65)
    print()

    # ----------------------------------------------------------
    # 4. PROCESSAMENTO PARALELO COM PROGRESSO
    # ----------------------------------------------------------
    print("  [1/4] Distribuindo arquivos entre os processos filhos...")
    print()

    inicio_total = time.time()
    vistos_global = set()
    contagem_global = defaultdict(int)
    concluidos = 0

    with ProcessPoolExecutor(max_workers=nucleos) as executor:
        # Submete todos os arquivos de uma vez (assíncrono)
        futuros = {executor.submit(processar_arquivo_puro, arq): arq for arq in arquivos_csv}

        exibir_progresso(0, total_arquivos, inicio_total)

        for futuro in as_completed(futuros):
            lista_parcial = futuro.result()
            concluidos += 1
            exibir_progresso(concluidos, total_arquivos, inicio_total)

            # RF003 – desduplicação global entre arquivos
            for reg in lista_parcial:
                chave_bo = (reg[0], reg[1], reg[2])
                if chave_bo not in vistos_global:
                    vistos_global.add(chave_bo)
                    contagem_global[(reg[3], reg[4])] += 1

    tempo_concorrente = time.time() - inicio_total
    print()  # nova linha após a barra
    print()

    # ----------------------------------------------------------
    # 5. RANKING TOP 5 POR SECCIONAL
    # ----------------------------------------------------------
    print("  [2/4] Calculando ranking criminal por Seccional...")

    ranking = defaultdict(list)
    for (sec, rub), qtd in contagem_global.items():
        ranking[sec].append((qtd, rub))

    for sec in ranking:
        ranking[sec].sort(reverse=True)

    print()
    print("=" * 65)
    print("  RESULTADO: TOP 5 CRIMES POR SECCIONAL")
    print("=" * 65)

    linhas_markdown = [
        "# Top 5 Crimes por Seccional — São Paulo (2010–2017)",
        "",
        "| # | NOME_SECCIONAL_CIRC | RUBRICA | CONTAGEM |",
        "| :- | :--- | :--- | ---: |",
    ]

    for sec in sorted(ranking.keys()):
        top5 = ranking[sec][:5]
        print(f"\n  📍 {sec}")
        print(f"  {'#':<4} {'RUBRICA':<52} {'QTD':>8}")
        print(f"  {'-'*4} {'-'*52} {'-'*8}")
        for pos, (qtd, rub) in enumerate(top5, start=1):
            rub_trunc = rub[:50] if len(rub) > 50 else rub
            print(f"  {pos:<4} {rub_trunc:<52} {qtd:>8,}")
            linhas_markdown.append(f"| {pos} | {sec} | {rub} | {qtd:,} |")

    # ----------------------------------------------------------
    # 6. EXPORTAÇÃO MARKDOWN
    # ----------------------------------------------------------
    print()
    print("  [3/4] Salvando tabela_crimes_completa.md...")

    caminho_md = 'tabela_crimes_completa.md'
    with open(caminho_md, 'w', encoding='utf-8') as f:
        f.write("\n".join(linhas_markdown))

    print(f"  ✔  Arquivo salvo em: {os.path.abspath(caminho_md)}")

    # ----------------------------------------------------------
    # 7. MÉTRICAS DE PERFORMANCE (Speedup & Eficiência)
    # ----------------------------------------------------------
    print()
    print("  [4/4] Calculando métricas de performance...")

    speedup    = TEMPO_SERIAL_REFERENCIA / tempo_concorrente
    eficiencia = (speedup / nucleos_display) * 100

    print()
    print("=" * 65)
    print("  MÉTRICAS DE PERFORMANCE (Lei de Amdahl)")
    print("=" * 65)
    print(f"  Tempo serial   (T1)  : {TEMPO_SERIAL_REFERENCIA:.2f}s  [referência empírica]")
    print(f"  Tempo paralelo (Tp)  : {tempo_concorrente:.2f}s  [{nucleos_display} núcleos]")
    print(f"  Speedup  S(p)        : {speedup:.2f}x")
    print(f"  Eficiência E(p)      : {eficiencia:.1f}%")
    print("=" * 65)
    print()

    # Tabela completa de referência com todos os dados do benchmark
    dados_benchmark = [
        (1,  175.21),
        (2,   88.93),
        (4,   55.14),
        (8,   51.69),
        (12,  52.84),
    ]

    print("  Tabela completa de benchmark (dados empíricos do laboratório):")
    print()
    print(f"  {'Núcleos':>8}  {'Tempo(s)':>10}  {'Speedup':>9}  {'Eficiência':>11}")
    print(f"  {'-'*8}  {'-'*10}  {'-'*9}  {'-'*11}")
    for p, t in dados_benchmark:
        s = TEMPO_SERIAL_REFERENCIA / t
        e = (s / p) * 100
        destaque = " ◄" if p == nucleos_display else ""
        print(f"  {p:>8}  {t:>10.2f}  {s:>9.2f}x  {e:>10.1f}%{destaque}")

    print()
    print("=" * 65)
    print(f"  Processamento finalizado em {tempo_concorrente:.2f} segundos.")
    print("=" * 65)
    print()


if __name__ == '__main__':
    import multiprocessing
    multiprocessing.freeze_support()
    main()