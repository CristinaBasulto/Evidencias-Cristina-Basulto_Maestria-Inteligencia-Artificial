#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import chromadb
from app.embed import gemini_ef

# Inicializar cliente persistente
client = chromadb.PersistentClient(path="chroma")

def get_collection():
    """Recupera o crea la colección inyectando el modelo de embeddings de Google."""
    return client.get_or_create_collection(
        name="proyecto_rag",
        embedding_function=gemini_ef
    )

def agregar_documentos(chunks: list[str], source: str) -> int:
    """Guarda los fragmentos de texto y sus vectores en ChromaDB."""
    coleccion = get_collection()

    # Generar IDs basados en el conteo actual para evitar sobreescrituras
    conteo_actual = coleccion.count()
    ids = [f"chunk_{conteo_actual + i}" for i in range(len(chunks))]

    # El proyecto requiere guardar el origen (source) en los metadatos
    metadatos = [{"source": source} for _ in chunks]

    coleccion.add(documents=chunks, ids=ids, metadatas=metadatos)
    return len(chunks)

def buscar_documentos(pregunta: str, top_k: int = 3) -> list:
    """Busca en ChromaDB los chunks más similares a la pregunta."""
    coleccion = get_collection()
    resultados = coleccion.query(query_texts=[pregunta], n_results=top_k)
    
    citas = []
    if resultados and 'documents' in resultados and resultados['documents']:
        for i in range(len(resultados['documents'][0])):
            citas.append({
                "id": resultados['ids'][0][i],
                "text": resultados['documents'][0][i],
                "source": resultados['metadatas'][0][i]['source'],
                "score": float(resultados['distances'][0][i])
            })
    return citas