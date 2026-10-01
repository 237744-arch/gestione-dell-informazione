
"""
Script per creare il dataset smartphone da Wikipedia in formato JSONL.
"""
import os
import json
from tqdm import tqdm
import wikipedia

DIR = "data"

OUTPUT_FILE = os.path.join(DIR, "wiki_phones_dataset.jsonl")

def carica_modelli_da_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        return [line.strip() for line in f if line.strip()]

def create():
    os.makedirs(DIR, exist_ok=True)
    wikipedia.set_lang("it") 

   
    try:
        TOPICS = carica_modelli_da_file("lista_smartphone.txt")
    except FileNotFoundError:
        print("File 'lista_smartphone.txt' non trovato. Uso una lista di test.")
        TOPICS = ["iPhone 18", "Samsung Galaxy S26", "Google Pixel 11", "Vivo x300 Pro"]

    with open(OUTPUT_FILE, "w", encoding="utf-8") as out:
        for topic in tqdm(TOPICS, desc="Scaricamento Wikipedia"): 
            try:
                # Impostato auto_suggest=True per aiutare Wikipedia a trovare i modelli esatti
                page = wikipedia.page(topic, auto_suggest=True)
                doc = {
                    "title": page.title,
                    "text": page.content
                }
                out.write(json.dumps(doc, ensure_ascii=False) + "\n")
            except wikipedia.exceptions.DisambiguationError as e:
                choice = e.options[0]
                try:
                    page = wikipedia.page(choice, auto_suggest=False)
                    doc = {"title": page.title, "text": page.content}
                    out.write(json.dumps(doc, ensure_ascii=False) + "\n")
                except Exception:
                    pass # Ignora gli errori minori per non bloccare il loop
            except Exception as ex:
                pass # Salta se la pagina non esiste e passa al prossimo

    print(f"Dataset creato in {OUTPUT_FILE}")

if __name__ == '__main__':
    create()