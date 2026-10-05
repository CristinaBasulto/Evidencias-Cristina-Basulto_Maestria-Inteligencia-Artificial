#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import streamlit as st
import requests

# URL de tu servidor FastAPI
API_URL = "http://localhost:8000"

st.set_page_config(page_title="RAG App", page_icon="📚")
st.title("📚 Sistema RAG con Gemini y ChromaDB")

# --- BARRA LATERAL: CARGA DE DOCUMENTOS ---
with st.sidebar:
    st.header("1. Subir Documentos")
    uploaded_file = st.file_uploader("Sube un archivo de texto (.txt o .md)", type=["txt", "md"])

    if st.button("Indexar Documento"):
        if uploaded_file is not None:
            with st.spinner("Indexando en ChromaDB..."):
                # Preparamos el archivo para enviarlo por POST
                files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "text/plain")}
                try:
                    response = requests.post(f"{API_URL}/ingest", files=files)
                    if response.status_code == 200:
                        data = response.json()
                        st.success(f"¡Éxito! Se indexaron {data['chunks_indexados']} fragmentos del archivo {data['archivo']}.")
                    else:
                        st.error(f"Error de la API: {response.text}")
                except Exception as e:
                    st.error(f"No se pudo conectar a la API: {e}. Verifica que Uvicorn esté corriendo.")
        else:
            st.warning("Por favor, sube un archivo primero.")

# --- ÁREA PRINCIPAL: CONSULTAS ---
st.header("2. Consultar al Sistema")
pregunta = st.text_input("Escribe tu pregunta sobre los documentos indexados:")

if st.button("Preguntar"):
    if pregunta:
        with st.spinner("Buscando evidencia y generando respuesta..."):
            payload = {"question": pregunta, "top_k": 3}
            try:
                response = requests.post(f"{API_URL}/query", json=payload)
                if response.status_code == 200:
                    data = response.json()

                    st.subheader("Respuesta")
                    # Manejo visual si el modelo se abstuvo
                    if data.get("abstained"):
                        st.warning(f"⚠️️ {data['answer']}")
                    else:
                        st.info(data['answer'])

                    # Mostrar las citas obligatorias (Texto, origen y score)
                    if data.get("citations"):
                        st.subheader("Fuentes recuperadas (Citas)")
                        for i, cita in enumerate(data["citations"]):
                            # Usamos un expander para no saturar la pantalla
                            with st.expander(f"Cita [{i+1}] - Origen: {cita['source']} (Score: {cita['score']:.4f})"):
                                st.write(cita["text"])
                else:
                    st.error(f"Error de la API: {response.text}")
            except Exception as e:
                st.error(f"No se pudo conectar a la API: {e}. Verifica que Uvicorn esté corriendo.")
    else:
        st.warning("Escribe una pregunta antes de consultar.")

