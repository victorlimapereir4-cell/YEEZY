import pandas as pd
import time
import glob
import os

# ==========================================
# 1. FUNÇÃO DE PROCESSAMENTO (Exatamente igual à concorrente)
# ==========================================
def processar_arquivo(caminho_arquivo):
    if "description" in caminho_arquivo.lower() or "methodology" in caminho_arquivo.lower():
        return pd.DataFrame()

    colunas_uteis = ['ID_DELEGACIA', 'ANO_BO', 'NUM_BO', 'NOME_SECCIONAL_CIRC', 'RUBRICA']
    
    try:
        lista_parcial = []
        for chunk in pd.read_csv(caminho_arquivo, usecols=colunas_uteis, encoding='utf-8', low_memory=False, chunksize=150000):
            chunk = chunk.dropna(subset=['ID_DELEGACIA', 'ANO_BO', 'NUM_BO', 'RUBRICA', 'NOME_SECCIONAL_CIRC'])
            chunk = chunk.drop_duplicates(subset=['ID_DELEGACIA', 'ANO_BO', 'NUM_BO'])
            lista_parcial.append(chunk)
            
        if not lista_parcial:
            return pd.DataFrame()
            
        df_arquivo = pd.concat(lista_parcial, ignore_index=True)
        df_arquivo = df_arquivo.drop_duplicates(subset=['ID_DELEGACIA', 'ANO_BO', 'NUM_BO'])
        
        return df_arquivo
        
    except Exception as e:
        print(f"Erro ao ler {caminho_arquivo}: {e}")
        return pd.DataFrame()

# ==========================================
# 2. FUNÇÃO PRINCIPAL (Execução Serial)
# ==========================================
def main():
    arquivos_csv = glob.glob(os.path.join('dados', '*.csv'))
    
    if not arquivos_csv:
        print("Nenhum arquivo CSV encontrado na pasta 'dados/'.")
        return

    print("="*60)
    print(f"Iniciando processamento SERIAL de {len(arquivos_csv)} arquivos...")
    print("Prepara o café, porque isso vai demorar (apenas 1 núcleo trabalhando).")
    print("="*60)
    
    start_serial = time.time()
    lista_resultados = []
    
    # === A GRANDE MUDANÇA ESTÁ AQUI ===
    # Em vez de mandar para o executor paralelo, fazemos um loop comum.
    # O processador vai ler o Arquivo 1, depois o Arquivo 2, depois o Arquivo 3...
    for arquivo in arquivos_csv:
        print(f"Processando {arquivo}...")
        parcial = processar_arquivo(arquivo)
        if not parcial.empty:
            lista_resultados.append(parcial)

    print("\nUnificando dados processados...")
    dados_consolidados = pd.concat(lista_resultados, ignore_index=True)
    dados_consolidados = dados_consolidados.drop_duplicates(subset=['ID_DELEGACIA', 'ANO_BO', 'NUM_BO'])

    print("Calculando o ranking criminal por Seccional...")
    contagem_final = dados_consolidados.groupby(['NOME_SECCIONAL_CIRC', 'RUBRICA']).size().reset_index(name='CONTAGEM')
    top5_serial = contagem_final.sort_values(['NOME_SECCIONAL_CIRC', 'CONTAGEM'], ascending=[True, False]).groupby('NOME_SECCIONAL_CIRC').head(5)

    tempo_serial = time.time() - start_serial
    print("\n" + "="*60)
    print(f"TEMPO TOTAL SERIAL: {tempo_serial:.2f} segundos")
    print("="*60 + "\n")

if __name__ == '__main__':
    main()