# Sistema RAG (FastAPI + Streamlit + ChromaDB + Google AI)

Este proyecto implementa una arquitectura desacoplada de Generación Aumentada por Recuperación (RAG). El sistema ingesta documentos locales, genera representaciones vectoriales utilizando modelos de Google AI, persiste los índices en disco con ChromaDB y genera respuestas ancladas a evidencia con Gemini, aplicando citas numeradas y abstención estricta.

---

## Arquitectura del Sistema

La interfaz de usuario interactúa exclusivamente con la API mediante peticiones HTTP en formato JSON, manteniendo la capa visual desacoplada de la base vectorial y de los modelos:

```text
Usuario
  └── Streamlit (puerto 8501)
        └── HTTP JSON
              └── FastAPI (puerto 8000)
                    ├── Google AI (gemini-embedding-001) → Embeddings
                    ├── ChromaDB (directorio local /chroma) → Persistencia y k-NN
                    └── Google AI (gemini-3.6-flash) → Generación anclada con citas
```

---

## Estructura del Proyecto

```text
proyecto_final/rag-app/
│
├── .env.example            # Plantilla para variables de entorno
├── .gitignore              # Debe ignorar .env, chroma/ y los entornos virtuales
├── requirements.txt        # Dependencias del proyecto
├── README.md               # Instrucciones de configuración y ejecución
│
├── data/                   # Corpus documental (.txt o .md)
├── chroma/                 # Persistencia de ChromaDB (ignorado en git)
│
├── app/                    # Código fuente del backend (FastAPI)
│   ├── __init__.py
│   ├── main.py             # Endpoints: /health, /ingest, /query
│   ├── chunk.py            # Partición de texto con solape configurable
│   ├── embed.py            # Cliente e integración de embeddings con Google AI
│   ├── store.py            # Conexión persistente e indexación en ChromaDB
│   └── generate.py         # Generación de respuestas y abstención con Gemini
│
└── ui/                     # Código fuente del frontend (Streamlit)
    └── streamlit_app.py    # Interfaz para carga de archivos, chat, citas y scores
```

---

## Requisitos Previos

- **Python:** versión 3.X o superior. 
- **Una API Key de Google AI** (ver paso 1 de la instalación).
- Dos terminales disponibles (una para la API y otra para la UI).

---

## Instalación

### 1. Obtener el proyecto

Clona o descarga el repositorio y entra a la carpeta raíz del proyecto. **Todos los comandos siguientes se ejecutan desde `rag-app/`**, porque las rutas `app.main:app` y `ui/streamlit_app.py` dependen de ello.

```bash
git clone <URL_DEL_REPOSITORIO>
cd rag-app
```

### 2. Obtener la API Key

1. Accede a [Google AI Studio](https://aistudio.google.com/apikey).
2. Inicia sesión y genera una nueva clave (API Key).

### 3. Crear el entorno virtual e instalar dependencias

**Windows (PowerShell)**

Con `uv`:

```powershell
uv venv
.\.venv\Scripts\activate
uv pip install -r requirements.txt
```

Con `venv` estándar:

```powershell
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
```

**macOS / Linux (Terminal)**

Con `uv`:

```bash
uv venv
source .venv/bin/activate
uv pip install -r requirements.txt
```

Con `venv` estándar:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 4. Configurar la clave (`GOOGLE_API_KEY`)

**Opción A: archivo `.env` (recomendada)**

Copia la plantilla y renómbrala a `.env`:

```powershell
# Windows (PowerShell)
copy .env.example .env
```

```bash
# macOS / Linux
cp .env.example .env
```

Abre `.env` y coloca tu clave:

```env
GOOGLE_API_KEY=tu_clave_de_google_ai_aqui
```
---

## Ejecución del Sistema

El sistema requiere **dos terminales activas simultáneamente**, ambas en la carpeta raíz del proyecto y con el entorno virtual activado. La API debe estar corriendo antes de abrir la interfaz.

### Paso 1: Iniciar el Backend (FastAPI)

En la primera terminal:

```bash
uvicorn app.main:app --reload --port 8000
```

- Documentación interactiva (Swagger UI): <http://localhost:8000/docs>
- Verificación de estado: <http://localhost:8000/health>

### Paso 2: Iniciar el Frontend (Streamlit)

En la segunda terminal:

```bash
streamlit run ui/streamlit_app.py
```

- Interfaz web: <http://localhost:8501>

---

## Verificación y Casos de Prueba

Los ejemplos de abajo usan el corpus de prueba incluido en `data/` (5 documentos sobre las Normas Globales de Auditoría Interna del IIA). Si usas otro corpus, adapta las preguntas.

### 1. Ingesta de documentos

Sube los archivos del corpus (`.txt` o `.md`) desde la barra lateral de Streamlit.

La API procesa el texto en *chunks* de 250 palabras con solape de 50 palabras, genera los vectores con `gemini-embedding-001` y los almacena en `chroma/`.

### 2. Consulta dentro de dominio

Escribe en el chat, por ejemplo:

> *Según la Norma 5.2, ¿cuáles son las tres consideraciones especialmente relevantes sobre la confidencialidad, privacidad y seguridad de la información, y bajo qué condición pueden divulgar información confidencial a partes no autorizadas?*

**Comportamiento esperado:** la respuesta se genera en español con citas explícitas en formato `[n]`, y se despliegan los fragmentos recuperados, su origen (`source`) y la métrica de distancia/score calculada por ChromaDB. La respuesta debe mencionar:

1. La custodia, retención y disposición de los registros de los trabajos.
2. La posibilidad de dar a conocer los registros de los trabajos a terceras partes, internas o externas.
3. El tratamiento del acceso a la información confidencial, o copias de ella, cuando ya no la necesiten.

Y la condición para divulgar: solo si existe una responsabilidad legal o profesional.

### 3. Consulta fuera de dominio (abstención)

Escribe una pregunta ajena al corpus, por ejemplo:

> *¿Cómo se prepara una paella valenciana?*

Para una prueba más exigente, usa una pregunta cercana al tema pero sin respuesta en los documentos:

> *¿Qué sanción económica establece el IIA para un auditor interno que divulgue información confidencial sin autorización, y en cuántos días debe notificarse el incidente al Consejo?*

**Comportamiento esperado:** el sistema no inventa datos y responde explícitamente *"no tengo evidencia suficiente"*, activando la bandera `"abstained": true` en el endpoint `/query`.

---
