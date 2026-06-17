import csv
import time
import glob
import os
from collections import defaultdict

# ====
# 1. FUNÇÃO DE PROCESSAMENTO (Sem Pandas)
# ====
def processar_arquivo_serial(caminho_arquivo):
    # Ignora arquivos de documentação
    if "description" in caminho_arquivo.lower() or "methodology" in caminho_arquivo.lower():
        return []

    registros_validos = []
    vistos_local = set()

    try:
        # Abre o arquivo e lê linha por linha com o leitor nativo do Python
        with open(caminho_arquivo, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                id_del = row.get('ID_DELEGACIA')
                ano_bo = row.get('ANO_BO')
                num_bo = row.get('NUM_BO')
                seccional = row.get('NOME_SECCIONAL_CIRC')
                rubrica = row.get('RUBRICA')

                # Filtra linhas vazias nas colunas que importam
                if not (id_del and ano_bo and num_bo and seccional and rubrica):
                    continue

                chave_bo = (id_del, ano_bo, num_bo)
                
                # Remove B.O.s duplicados 
                if chave_bo in vistos_local:
                    continue

                vistos_local.add(chave_bo)
                registros_validos.append((id_del, ano_bo, num_bo, seccional, rubrica))

        return registros_validos
        
    except Exception as e:
        print(f"Erro ao ler {caminho_arquivo}: {e}")
        return []

# ======
# 2. FUNÇÃO PRINCIPAL (Execução Serial)
# ======
def main():
    arquivos_csv = glob.glob(os.path.join('dados', '*.csv'))
    
    if not arquivos_csv:
        print("Nenhum arquivo CSV encontrado na pasta 'dados/'.")
        return

    print("="*60)
    print(f"processamento SERIAL de {len(arquivos_csv)} arquivos...")
    print("="*60)
    
    start_serial = time.time()
    
    vistos_global = set()
    contagem_global = defaultdict(int)

    # === LOOP SERIAL ===
    # Lê um arquivo por vez, linha por linha
    for arquivo in arquivos_csv:
        print(f"Processando {arquivo}...")
        lista_parcial = processar_arquivo_serial(arquivo)
        
        # Junta na memória principal e garante que não há duplicidade entre os arquivos
        for reg in lista_parcial:
            chave_bo = (reg[0], reg[1], reg[2])
            if chave_bo not in vistos_global:
                vistos_global.add(chave_bo)
                seccional = reg[3]
                rubrica = reg[4]
                contagem_global[(seccional, rubrica)] += 1

    print("\nCalculando o ranking criminal por Seccional...")
    
    # Agrupa por seccional para extrair o Top 5
    ranking = defaultdict(list)
    for (sec, rub), qtd in contagem_global.items():
        ranking[sec].append((qtd, rub))

    print("\n=== RESULTADO COMPLETO: TOP 5 CRIMES POR ZONA ===")
    
    # Prepara o conteúdo do arquivo Markdown
    linhas_markdown = ["| NOME_SECCIONAL_CIRC | RUBRICA | CONTAGEM |", "| :--- | :--- | :--- |"]
    
    for sec in sorted(ranking.keys()):
        # Ordena as contagens de forma decrescente
        ranking[sec].sort(reverse=True)
        top5 = ranking[sec][:5]
        
        for qtd, rub in top5:
            # Imprime no terminal de forma legível
            print(f"{sec.ljust(30)} | {rub.ljust(50)} | {qtd}")
            # Adiciona na lista do arquivo .md
            linhas_markdown.append(f"| {sec} | {rub} | {qtd} |")

    tempo_serial = time.time() - start_serial
    print("\n" + "="*60)
    print(f"TEMPO TOTAL SERIAL: {tempo_serial:.2f} segundos")
    print("="*60 + "\n")

    # Salva o arquivo final
    with open('tabela_crimes_completa.md', 'w', encoding='utf-8') as f:
        f.write("\n".join(linhas_markdown))
    print("[+] Tabela salva em 'tabela_crimes_completa.md'.")


if __name__ == '__main__':
    main()