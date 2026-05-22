import pandas as pd
import time
from concurrent.futures import ProcessPoolExecutor
import glob
import os

# ==========================================
# 1. FUNÇÃO DA THREAD (Processa um arquivo CSV inteiro)
# ==========================================
def processar_arquivo(caminho_arquivo):
    # Ignora os arquivos que não são de dados (como o description e methodology)
    if "description" in caminho_arquivo.lower() or "methodology" in caminho_arquivo.lower():
        return pd.DataFrame()

    colunas_uteis = ['ID_DELEGACIA', 'ANO_BO', 'NUM_BO', 'NOME_SECCIONAL_CIRC', 'RUBRICA']
    
    try:
        lista_parcial = []
        # Lê o arquivo em lotes para não estourar a memória RAM da máquina
        for chunk in pd.read_csv(caminho_arquivo, usecols=colunas_uteis, encoding='utf-8', low_memory=False, chunksize=150000):
            # Limpa linhas inválidas
            chunk = chunk.dropna(subset=['ID_DELEGACIA', 'ANO_BO', 'NUM_BO', 'RUBRICA', 'NOME_SECCIONAL_CIRC'])
            # Tira B.O.s duplicados dentro do lote
            chunk = chunk.drop_duplicates(subset=['ID_DELEGACIA', 'ANO_BO', 'NUM_BO'])
            lista_parcial.append(chunk)
            
        if not lista_parcial:
            return pd.DataFrame()
            
        # Junta os pedaços lidos deste arquivo
        df_arquivo = pd.concat(lista_parcial, ignore_index=True)
        # Limpeza dupla para garantir
        df_arquivo = df_arquivo.drop_duplicates(subset=['ID_DELEGACIA', 'ANO_BO', 'NUM_BO'])
        
        return df_arquivo
        
    except Exception as e:
        print(f"Erro ao ler {caminho_arquivo}: {e}")
        return pd.DataFrame()

# ==========================================
# 2. FUNÇÃO PRINCIPAL
# ==========================================
def main():
    # Busca todos os arquivos .csv dentro da pasta 'dados'
    arquivos_csv = glob.glob(os.path.join('dados', '*.csv'))
    
    if not arquivos_csv:
        print("Nenhum arquivo CSV encontrado na pasta 'dados/'. Verifique a estrutura das pastas.")
        return

    print("="*60)
    print(f"Iniciando processamento CONCORRENTE de {len(arquivos_csv)} arquivos...")
    print("Isso pode levar alguns minutos devido ao volume massivo de dados.")
    print("="*60)
    
    start_concorrente = time.time()
    lista_resultados = []
    
    # Processamento Paralelo: Joga os arquivos para os múltiplos núcleos do processador
    with ProcessPoolExecutor() as executor:
        # A função map distribui a lista de arquivos para os trabalhadores simultaneamente
        resultados_threads = executor.map(processar_arquivo, arquivos_csv)
        
        for parcial in resultados_threads:
            if not parcial.empty:
                lista_resultados.append(parcial)

    print("Unificando dados processados pelas threads...")
    # Junta todos os recortes limpos das threads em uma tabela matriz
    dados_consolidados = pd.concat(lista_resultados, ignore_index=True)
    
    # GARANTIA FINAL: Remove B.O.s duplicados que possam ter vazado entre arquivos de anos diferentes
    dados_consolidados = dados_consolidados.drop_duplicates(subset=['ID_DELEGACIA', 'ANO_BO', 'NUM_BO'])

    print("Calculando o ranking criminal por Seccional...")
    # Agrupa e conta os crimes
    contagem_final = dados_consolidados.groupby(['NOME_SECCIONAL_CIRC', 'RUBRICA']).size().reset_index(name='CONTAGEM')
    
    # Extrai o Top 5
    top5_concorrente = contagem_final.sort_values(['NOME_SECCIONAL_CIRC', 'CONTAGEM'], ascending=[True, False]).groupby('NOME_SECCIONAL_CIRC').head(5)

    tempo_concorrente = time.time() - start_concorrente
    # Mostra a tabela completa no terminal
    print("\n=== RESULTADO COMPLETO: TOP 5 CRIMES POR ZONA ===")
    print(top5_concorrente.to_string(index=False)) 

    # BÔNUS: Já salva a tabela inteira formatada em Markdown num arquivo de texto!
    with open('tabela_crimes_completa.md', 'w', encoding='utf-8') as f:
        f.write(top5_concorrente.to_markdown(index=False))
    print("\n[+] A tabela completa foi salva no arquivo 'tabela_crimes_completa.md' para você colar no README.")

if __name__ == '__main__':
    # Necessário para evitar bugs no Windows ao usar múltiplos processos
    import multiprocessing
    multiprocessing.freeze_support()
    main()