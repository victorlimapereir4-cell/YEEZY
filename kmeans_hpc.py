import numpy as np
import pandas as pd
import time
import multiprocessing as mp
import argparse
import os

# ---------------------------------------------------------
# WORKER: Onde a carga pesada de CPU acontece (Data Parallelism)
# ---------------------------------------------------------
def worker_k_means(chunk_data, centroids):
    # Calcula as distâncias euclidianas (Matemática pesada)
    distances = np.linalg.norm(chunk_data[:, np.newaxis] - centroids, axis=2)
    labels = np.argmin(distances, axis=1)
    
    k = centroids.shape[0]
    new_centroids_sum = np.zeros_like(centroids)
    counts = np.zeros(k)
    
    for i in range(k):
        cluster_points = chunk_data[labels == i]
        if len(cluster_points) > 0:
            new_centroids_sum[i] = np.sum(cluster_points, axis=0)
            counts[i] = len(cluster_points)
            
    return new_centroids_sum, counts

# ---------------------------------------------------------
# MASTER: Coordenação e Sincronização
# ---------------------------------------------------------
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--processos', type=int, default=1, help='Número de processos')
    parser.add_argument('-f', '--file', type=str, default='dataset.csv', help='Arquivo CSV limpo')
    args = parser.parse_args()

    n_processes = args.processos
    
    print(f"\n[INFO] Iniciando Experimento HPC com {n_processes} processo(s)...")
    
    # ---------------------------------------------------------
    # FASE 1: I/O BOUND (Leitura do Disco - NÃO CONTA NO BENCHMARK)
    # ---------------------------------------------------------
    print(f"[INFO] Lendo dataset massivo ({args.file}) para a RAM...")
    io_start = time.time()
    
    if not os.path.exists(args.file):
        print(f"[ERRO] Arquivo {args.file} não encontrado na pasta!")
        return

    # Lê o CSV pré-processado inteiro para a memória
    df = pd.read_csv(args.file)
    # Pega só os números para o cálculo matemático
    data = df.select_dtypes(include=[np.number]).values
    
    io_end = time.time()
    print(f"[INFO] I/O Concluído em {io_end - io_start:.2f}s. Matriz de dados: {data.shape[0]} linhas x {data.shape[1]} colunas.")
    print("[INFO] =====================================================")
    
    # ---------------------------------------------------------
    # FASE 2: CPU BOUND (Processamento Paralelo - CRONÔMETRO VALENDO)
    # ---------------------------------------------------------
    k = 5 # Clusters
    max_iters = 10 # Iterações de cálculo
    
    np.random.seed(42)
    centroids = data[np.random.choice(data.shape[0], k, replace=False)]
    chunks = np.array_split(data, n_processes)

    print("[INFO] Disparando cronômetro de CPU e iniciando cálculos paralelos...")
    cpu_start = time.time()
    
    with mp.Pool(processes=n_processes) as pool:
        for iteration in range(max_iters):
            # Envia os blocos para os núcleos do processador
            results = pool.starmap(worker_k_means, [(chunk, centroids) for chunk in chunks])
            
            # Barreira de Sincronização
            new_centroids = np.zeros_like(centroids)
            total_counts = np.zeros(k)
            
            for sums, counts in results:
                new_centroids += sums
                total_counts += counts
                
            for i in range(k):
                if total_counts[i] > 0:
                    new_centroids[i] = new_centroids[i] / total_counts[i]
            
            centroids = new_centroids
            print(f"  -> Iteração global {iteration + 1}/{max_iters} finalizada.")

    cpu_end = time.time()
    
    print("\n" + "=" * 50)
    print(f" RELATÓRIO DO EXPERIMENTO: {n_processes} PROCESSO(S)")
    print(f" TEMPO TOTAL DE CPU (Speedup Baseline): {cpu_end - cpu_start:.4f} segundos")
    print("=" * 50 + "\n")

if __name__ == '__main__':
    # Proteção nativa do Windows para multiprocessing
    mp.freeze_support() 
    main()