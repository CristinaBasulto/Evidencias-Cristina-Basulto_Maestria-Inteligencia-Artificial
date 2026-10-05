#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import os
from dotenv import load_dotenv, find_dotenv
from google import genai
from chromadb import Documents, EmbeddingFunction, Embeddings

# Cargar variables de entorno
load_dotenv(find_dotenv())

# Inicializar cliente de Google
client_genai = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

class GeminiEmbeddingFunction(EmbeddingFunction):
    """Clase personalizada para que ChromaDB use Google AI para vectorizar."""
    def __call__(self, input: Documents) -> Embeddings:
        response = client_genai.models.embed_content(
            model="gemini-embedding-001",
            contents=input,
        )
        return [embedding.values for embedding in response.embeddings]

# Instancia lista para ser usada por ChromaDB
gemini_ef = GeminiEmbeddingFunction()

