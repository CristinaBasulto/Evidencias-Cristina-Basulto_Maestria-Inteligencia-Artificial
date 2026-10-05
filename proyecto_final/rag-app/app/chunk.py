#!/usr/bin/env python
# coding: utf-8

# In[ ]:


def particionar_texto(texto: str, chunk_words: int = 250, overlap: int = 50) -> list[str]:
    """
    Divide un texto en fragmentos (chunks) basándose en la cantidad de palabras,
    manteniendo un solape (overlap) para no perder el contexto.
    """
    palabras = texto.split()
    chunks = []

    if not palabras:
        return chunks

    paso = chunk_words - overlap
    if paso <= 0:
        raise ValueError("El overlap debe ser menor que el chunk_words.")

    for i in range(0, len(palabras), paso):
        fragmento = " ".join(palabras[i:i + chunk_words])
        chunks.append(fragmento)

        if i + chunk_words >= len(palabras):
            break

    return chunks

