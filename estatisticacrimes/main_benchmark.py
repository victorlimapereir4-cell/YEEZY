import pandas as pd
import time
from concurrent.futures import ProcessPoolExecutor
import glob
import os

# ==========================================
# 1. FUNÇÃO DA THREAD (Idêntica para o teste ser justo)
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
# 2. FUNÇÃO DE BENCHMARK AUTOMATIZADO
# ==========================================
def main():
    arquivos_csv = glob.glob(os.path.join('dados', '*.csv'))
    
    if not arquivos_csv:
        print("Arquivos não encontrados. Verifique a pasta 'dados/'.")
        return

    # Essa é a exata configuração exigida no seu relatório
    bateria_de_testes = [2, 4, 8, 12]
    
    print("="*60)
    print("INICIANDO BATERIA DE TESTES DE ESCALABILIDADE")
    print("Isso vai demorar, vá treinar ou tomar um café!")
    print("="*60)

    for num_processos in bateria_de_testes:
        print(f"\n[!] Rodando teste com {num_processos} processos simultâneos...")
        start_time = time.time()
        
        lista_resultados = []
        
        # Aqui a mágica acontece: limitamos a quantidade exata de motores
        with ProcessPoolExecutor(max_workers=num_processos) as executor:
            resultados_threads = executor.map(processar_arquivo, arquivos_csv)
            
            for parcial in resultados_threads:
                if not parcial.empty:
                    lista_resultados.append(parcial)

        # Processamento final para o cronômetro ser fiel à tarefa completa
        dados_consolidados = pd.concat(lista_resultados, ignore_index=True)
        dados_consolidados = dados_consolidados.drop_duplicates(subset=['ID_DELEGACIA', 'ANO_BO', 'NUM_BO'])
        contagem_final = dados_consolidados.groupby(['NOME_SECCIONAL_CIRC', 'RUBRICA']).size().reset_index(name='CONTAGEM')
        top5_concorrente = contagem_final.sort_values(['NOME_SECCIONAL_CIRC', 'CONTAGEM'], ascending=[True, False]).groupby('NOME_SECCIONAL_CIRC').head(5)

        tempo_final = time.time() - start_time
        print(f"--> RESULTADO: {num_processos} processos = {tempo_final:.2f} segundos")

if __name__ == '__main__':
    import multiprocessing
    multiprocessing.freeze_support()
    main()