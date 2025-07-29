# Ayudín: Tu Asistente Experto en la información comercial del Supermecado

Un chatbot inteligente que te permite "dialogar" con la información comercial de Econotodo, consultar productos, precios, promociones y más, de forma rápida y disponible 24/7.

Este proyecto utiliza un pipeline de RAG (Retrieval Augmented Generation) con LangChain y OpenAI para ofrecer una herramienta de Q&A potente sobre un corpus de documentos extenso.

## 🎯 Propósito y Problema que Resuelve

Econotodo busca mejorar la calidad y rapidez de su atención, ofreciendo comodidad a todos sus clientes 
a través de un canal virtual siempre disponible.

Este asistente resuelve el problema de tener que acudir físicamente al supermercado o esperar atención telefónica.
Con ayudin cualquier cliente podrá:  
- Asesorarse sobre productos y promociones  
- Conocer precios y stock en tiempo real  
- Armar un carrito de compra y estimar gastos

Todo desde la comodidad del hogar.

## 🚀 Características Clave

-   **Interfaz de Chat Intuitiva:** Construida con Streamlit para una experiencia de usuario limpia y sencilla.
-   **Q&A comercial:** Haz preguntas comerciales sobre Econotodo. Ayudín te ayudará a aclarar cualquier consulta.
-   **Respuestas basadas en la información comercial más reciente:** El bot está instruido para basar sus respuestas únicamente en la documentación proporcionada, evitando alucinaciones.
-   **Procesamiento de Documentos Robusto:** Utiliza `RecursiveCharacterTextSplitter` de LangChain para dividir de forma inteligente documentos PDF complejos, manteniendo el contexto de código y párrafos.
-   **Monitorización de Costes:** Una barra lateral muestra en tiempo real los tokens utilizados y el coste en USD de cada consulta y del total de la sesión.

## 💻 Stack Tecnológico

-   **Frontend:** Streamlit
-   **Backend y Orquestación:** Python, LangChain, Docker, Docker Compose
-   **Modelo de Lenguaje (LLM):** OpenAI GPT-3.5-turbo (o superior)
-   **Base de Datos de Vectores:** ChromaDB
-   **Embeddings:** OpenAI Embeddings
-   **Procesamiento de Documentos:** PDFPlumber

## 📁 Estructura del Proyecto

```
AI_Assistant/
│
├── app/
│   ├── app.py           # Lógica del Frontend (Streamlit)
│   ├── backend.py       # Lógica del Backend (LangChain RAG)
│   ├── data_loader.py   # Carga y procesa el PDF
│   ├── prompts.py       # Contiene el prompt del sistema para el bot
│   └── vector_store.py  # Gestiona la creación y carga de la BD de vectores
│
├── data/
│   └── catalogo_econotodo.pdf      # El documento fuente para el bot
│
├── vector_store/        # Directorio donde se guarda la BD de vectores (creado automáticamente)
│
├── config.yaml          # Tu fichero de configuración con la API key
├── requirements.txt     # Dependencias del proyecto
└── README.md            # Esta documentación
```

