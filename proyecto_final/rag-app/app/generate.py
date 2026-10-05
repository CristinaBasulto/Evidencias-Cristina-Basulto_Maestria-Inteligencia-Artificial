#!/usr/bin/env python
# coding: utf-8

# In[ ]:


from app.embed import client_genai

def generar_respuesta(pregunta: str, citas: list) -> dict:
    """Envía el contexto recuperado a Gemini para generar la respuesta final."""
    if not citas:
        return {"answer": "No tengo evidencia suficiente.", "abstained": True}

    # Armar contexto numerado para las citas [1], [2]...
    contexto = ""
    for i, cita in enumerate(citas):
        contexto += f"[{i+1}] {cita['text']}\n"

    prompt = f"""Usa SOLO el siguiente contexto para responder a la pregunta.
    Debes responder en español.
    Al final de cada afirmación, debes citar el número del fragmento exacto de donde sacaste la información usando corchetes, por ejemplo: [1].
    Si la respuesta no se encuentra en el contexto proporcionado, NO inventes datos. Debes abstenerte explícitamente diciendo: "no tengo evidencia suficiente".

    Contexto recuperado:
    {contexto}

    Pregunta del usuario: {pregunta}
    """

    try:
        respuesta = client_genai.models.generate_content(
            model="gemini-3.6-flash", # Usamos el modelo estable[cite: 7]
            contents=prompt
        )
        texto_respuesta = "".join(
            part.text
            for part in respuesta.candidates[0].content.parts
            if getattr(part, "text", None)
        )
        # Determinamos si el modelo se abstuvo basándonos en la frase clave
        abstained = "no tengo evidencia suficiente" in texto_respuesta.lower()

        return {"answer": texto_respuesta, "abstained": abstained}
    except Exception as e:
        return {"answer": f"Error de generación: {str(e)}", "abstained": True}

