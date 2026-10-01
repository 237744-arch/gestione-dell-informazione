import json
import matplotlib.pyplot as plt
import numpy as np

# 1. CARICAMENTO DATI
with open("golden_list.json", "r", encoding="utf-8") as f:
    gold_standard = json.load(f)

with open("bench_save.json", "r", encoding="utf-8") as f:
    bench_results = json.load(f)

engines = ["PostgreSQL", "Whoosh_TFIDF", "Whoosh_Weighted"]
k = 5
metrics = {engine: {"P@5": [], "R@5": [], "F1@5": [], "AP": []} for engine in engines}

# 2. CALCOLO DELLE METRICHE
for uin, gold_docs in gold_standard.items():
    # Normalizzazione Gold Standard
    gold_docs_norm = [str(doc).lower().strip() for doc in gold_docs]
    total_relevant = len(gold_docs_norm)
    
    for engine in engines:
        retrieved = bench_results.get(uin, {}).get(engine, [])
        retrieved_norm = [str(doc).lower().strip() for doc in retrieved]
        
        # FIX: Rimuoviamo i duplicati mantenendo l'ordine di ranking originale
        retrieved_unique = []
        for doc in retrieved_norm:
            if doc not in retrieved_unique:
                retrieved_unique.append(doc)
                
        # Taglio ai top K sui risultati "puliti" dai duplicati
        retrieved_k_norm = retrieved_unique[:k]
        
        relevant_retrieved = [doc for doc in retrieved_k_norm if doc in gold_docs_norm]
        
        # Calcolo metriche
        p_k = len(relevant_retrieved) / k
        r_k = len(relevant_retrieved) / total_relevant if total_relevant > 0 else 0
        f1_k = (2 * p_k * r_k) / (p_k + r_k) if (p_k + r_k) > 0 else 0
        
        sum_precision = 0
        hits = 0
        for i, doc in enumerate(retrieved_k_norm):
            if doc in gold_docs_norm:
                hits += 1
                sum_precision += hits / (i + 1) 
                
        ap = sum_precision / total_relevant if total_relevant > 0 else 0
        
        metrics[engine]["P@5"].append(p_k)
        metrics[engine]["R@5"].append(r_k)
        metrics[engine]["F1@5"].append(f1_k)
        metrics[engine]["AP"].append(ap)

# 3. STAMPA RISULTATI E GRAFICO
print("="*50)
print("RISULTATI FINALI BENCHMARK (k=5)")
print("="*50)

mean_metrics = {}

for engine in engines:
    mean_p = np.mean(metrics[engine]["P@5"])
    mean_r = np.mean(metrics[engine]["R@5"])
    mean_f1 = np.mean(metrics[engine]["F1@5"])
    map_score = np.mean(metrics[engine]["AP"]) 
    
    mean_metrics[engine] = [mean_p, mean_r, mean_f1, map_score]
    
    print(f"\nMotore: {engine}")
    print(f"  Mean Precision@5 : {mean_p:.4f}")
    print(f"  Mean Recall@5    : {mean_r:.4f}")
    print(f"  Mean F1@5        : {mean_f1:.4f}")
    print(f"  MAP (Mean Avg P) : {map_score:.4f}")

labels = ['Precision@5', 'Recall@5', 'F1@5', 'MAP']
x = np.arange(len(labels))
width = 0.25 

fig, ax = plt.subplots(figsize=(10, 6))

rects1 = ax.bar(x - width, mean_metrics["PostgreSQL"], width, label='PostgreSQL (ts_rank_cd)', color='#3366cc')
rects2 = ax.bar(x, mean_metrics["Whoosh_TFIDF"], width, label='Whoosh (TF-IDF)', color='#dc3912')
rects3 = ax.bar(x + width, mean_metrics["Whoosh_Weighted"], width, label='Whoosh (BM25)', color='#ff9900')

ax.set_ylabel('Punteggio (0.0 - 1.0)')
ax.set_title('Confronto Prestazioni Motori di Ricerca (k=5)')
ax.set_xticks(x)
ax.set_xticklabels(labels)
ax.set_ylim(0, 1.1)
ax.legend()
ax.grid(axis='y', linestyle='--', alpha=0.7)

plt.tight_layout()
plt.savefig("confronto_motori.png", dpi=300)
print("\n" + "="*50)
print("Grafico salvato con successo come 'confronto_motori.png'!")
plt.show()