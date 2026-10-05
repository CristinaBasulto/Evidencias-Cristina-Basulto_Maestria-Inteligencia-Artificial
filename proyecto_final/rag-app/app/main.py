#!/usr/bin/env python
# coding: utf-8

# In[ ]:


from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel
from app.chunk import particionar_texto
from app.store import agregar_documentos, buscar_documentos
from app.generate import generar_respuesta

app = FastAPI(title="API RAG")

# Modelo de datos para el JSON de entrada de /query
class QueryRequest(BaseModel):
    question: str
    top_k: int = 3

@app.get("/health")
def health_check():
    return {"status": "ok", "message": "API RAG funcionando"}

@app.post("/ingest")
async def ingest_document(file: UploadFile = File(...)):
    contenido = await file.read()
    try:
        texto = contenido.decode("utf-8")
    except Exception:
        raise HTTPException(status_code=400, detail="El archivo debe ser texto UTF-8.")
        
    chunks = particionar_texto(texto, chunk_words=250, overlap=50)
    if not chunks:
        raise HTTPException(status_code=400, detail="No se pudo extraer texto.")
        
    total_chunks = agregar_documentos(chunks, source=file.filename)
    
    return {
        "message": "Indexación completada",
        "archivo": file.filename,
        "documentos_indexados": 1,
        "chunks_indexados": total_chunks
    }

@app.post("/query")
def query_documents(req: QueryRequest):
    # 1. Recuperar contexto de ChromaDB
    citas = buscar_documentos(req.question, top_k=req.top_k)
    
    # 2. Generar respuesta con Gemini
    resultado = generar_respuesta(req.question, citas)
    
    # 3. Retornar el esquema exacto solicitado
    return {
        "answer": resultado["answer"],
        "citations": citas,
        "abstained": resultado["abstained"]
    }