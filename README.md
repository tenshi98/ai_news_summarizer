# AI News Summarizer

Resumidor de titulares de NewsAPI con Qwen 2.5.

Aplicación web construida con **FastAPI** que se comunica con un modelo local
servido por [Ollama](https://ollama.com/). El frontend es HTML, CSS y
JavaScript sin frameworks.

---

## Tabla de Contenidos

- [Tecnologías utilizadas](#tecnologías-utilizadas)
- [Características](#características)
- [Requisitos](#requisitos)
- [Instalación](#instalación)
- [Configuración](#configuración)
- [Cómo ejecutar el proyecto](#cómo-ejecutar-el-proyecto)
- [Ejemplos de uso](#ejemplos-de-uso)
- [Estructura de carpetas completa del proyecto (backend + frontend)](#estructura-de-carpetas-completa-del-proyecto-backend--frontend)
- [Explicaciones breves de cada módulo](#explicaciones-breves-de-cada-módulo)
- [Solución de Problemas](#solución-de-problemas)
- [Notas Adicionales](#notas-adicionales)

---

## Tecnologías utilizadas

| Tecnología | Uso en el proyecto |
|---|---|
| Python 3.10+ | Lenguaje del backend. |
| FastAPI | Framework HTTP, validación e inyección de dependencias. |
| Uvicorn | Servidor ASGI para ejecutar la aplicación. |
| Pydantic v2 | Esquemas de respuesta y validación de datos. |
| pydantic-settings | Lectura de configuración desde entorno y `.env`. |
| Requests | Cliente HTTP hacia Ollama y NewsAPI. |
| Ollama | Ejecución local del modelo `qwen2.5`. |
| HTML5, CSS3 y JavaScript | Interfaz sin frameworks ni compilación. |
| pytest + httpx | Pruebas automatizadas y cliente de pruebas. |

## Características

- Consulta los titulares más recientes de NewsAPI por categoría.
- Resume los tres primeros titulares con el modelo local.
- Muestra el resumen y los enlaces a las noticias originales.
- Valida que los enlaces usen `http` o `https` antes de renderizarlos.
- Devuelve `articles: []` cuando no hay noticias, sin romper el frontend.
- Lee `NEWS_API_KEY` desde el entorno, nunca desde el código.
- Interfaz web servida por el propio backend, sin frameworks de frontend.
- Documentación interactiva de la API en `/docs` y `/redoc`.
- Configuración por variables de entorno o archivo `.env`.
- Registro de eventos con el módulo `logging` de Python.
- Pruebas automatizadas con Ollama simulado (no requieren red).

## Requisitos

- Python **3.10 o superior**.
- [Ollama](https://ollama.com/download) instalado y en ejecución.
- Modelo `qwen2.5` descargado (`ollama pull qwen2.5`).
- Navegador moderno con soporte para `fetch`.
- Cuenta y clave de [NewsAPI](https://newsapi.org/) con cuota disponible.
- Opcional: `curl` para probar la API desde la terminal.

## Instalación

```bash
cd ai_news_summarizer
python3 -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt
cp .env.example .env
```

Edita `.env` si necesitas cambiar el puerto, la URL de Ollama o el modelo.
El archivo `.env` no debe subirse al repositorio (ya está en `.gitignore`).

## Configuración

Todas las variables se leen de `.env` o del entorno del proceso. Las variables
de entorno tienen prioridad sobre el archivo.

| Variable | Valor por defecto | Descripción |
|---|---|---|
| `APP_HOST` | `0.0.0.0` | Interfaz de escucha del servidor. |
| `APP_PORT` | `8000` | Puerto HTTP del servidor. |
| `OLLAMA_URL` | `http://localhost:11434/api/generate` | Endpoint de generación de Ollama. |
| `OLLAMA_MODEL` | `qwen2.5` | Modelo usado en las peticiones. |
| `OLLAMA_TIMEOUT` | `120` | Tiempo máximo de espera de Ollama, en segundos. |
| `NEWS_API_URL` | `https://newsapi.org/v2/top-headlines` | Endpoint de NewsAPI. |
| `NEWS_API_KEY` | — (obligatoria) | Clave de acceso a NewsAPI. |
| `NEWS_TIMEOUT` | `30` | Tiempo máximo de espera de NewsAPI, en segundos. |

> `NEWS_API_KEY` es obligatoria para este servicio. Si falta, el endpoint responde `500` con `Failed to fetch news articles`.

## Cómo ejecutar el proyecto

1. Asegúrate de que Ollama esté en ejecución y el modelo descargado:

   ```bash
   ollama serve
   ollama pull qwen2.5
   ```

2. Activa el entorno virtual (si aún no lo hiciste):

   ```bash
   source .venv/bin/activate      # Windows: .venv\Scripts\activate
   ```

3. Arranca el servidor:

   ```bash
   python app.py
   ```

   Alternativa equivalente:

   ```bash
   uvicorn app:app --reload --host 0.0.0.0 --port 8000
   ```

4. Abre la interfaz en <http://localhost:8000>.
   La documentación automática de la API está en <http://localhost:8000/docs>.

5. Detén el servidor con `Ctrl+C`.

### Pruebas automatizadas

```bash
pip install -r requirements-dev.txt
pytest
```

Las pruebas sustituyen los clientes externos con `dependency_overrides`, por lo
que no requieren un servidor Ollama ni conexión a internet.

## Ejemplos de uso

### Desde la interfaz web

1. Elige una categoría (tecnología, negocios, deportes, etc.).
2. Pulsa **Obtener noticias**.
3. Revisa **Noticias resumidas** y los enlaces de **Titulares originales**.

### Desde la API con `curl`

```bash
curl 'http://localhost:8000/fetch_news?category=technology'
```

Respuesta esperada (los textos varían según el modelo):

```json
{
  "summary": "Los titulares destacan avances en inteligencia artificial...",
  "articles": [
    {
      "title": "Titular de ejemplo",
      "source": {"name": "Medio de ejemplo"},
      "url": "https://example.com/noticia"
    }
  ]
}
```

También puedes explorar y probar el endpoint desde Swagger UI en
<http://localhost:8000/docs>.

## Estructura de carpetas completa del proyecto (backend + frontend)

```text
ai_news_summarizer/
├── app.py
├── pytest.ini
├── requirements.txt
├── requirements-dev.txt
├── .env.example
├── .gitignore
├── README.md
├── server/
│   ├── __init__.py
│   ├── application.py
│   ├── config.py
│   ├── dependencies.py
│   ├── logging_config.py
│   ├── api/
│   │   ├── __init__.py
│   │   └── routes.py
│   ├── schemas/
│   │   ├── __init__.py
│   │   └── responses.py
│   └── services/
│       ├── __init__.py
│       ├── ollama.py
│       └── news.py
├── static/
│   ├── index.html
│   ├── style.css
│   └── script.js
└── tests/
    ├── __init__.py
    └── test_api.py
```

## Explicaciones breves de cada módulo

| Archivo | Responsabilidad |
|---|---|
| `app.py` | Punto de entrada. Conserva `python app.py` y `uvicorn app:app`; delega la creación de la app en `server/application.py`. |
| `server/application.py` | Crea la instancia de FastAPI, configura el logging, monta `/static` y registra el enrutador. |
| `server/config.py` | Define `Settings` con `pydantic-settings`, lee `.env` y calcula la ruta absoluta de `static/`. |
| `server/dependencies.py` | Funciones `get_*` usadas con `Depends` para inyectar configuración y clientes; se pueden sustituir en pruebas. |
| `server/logging_config.py` | Configura el formato y el nivel de los logs una sola vez por proceso. |
| `server/api/routes.py` | Expone `GET /` y `GET /fetch_news`; traduce los errores de los servicios a respuestas HTTP claras. |
| `server/schemas/responses.py` | Modelos Pydantic que validan y documentan la forma exacta de la respuesta. |
| `server/services/ollama.py` | Cliente de Ollama: arma el payload, aplica timeout, valida el estado HTTP, parsea el JSON y lanza errores propios. |
| `server/services/news.py` | Cliente de NewsAPI: lee la clave desde la configuración, consulta titulares y limita la cantidad de artículos. |
| `static/index.html` | Estructura de la interfaz; no contiene CSS ni JavaScript inline. |
| `static/style.css` | Estilos de la interfaz, incluida la clase `.error-message`. |
| `static/script.js` | Lógica del navegador: `fetch`, validación de respuesta, render seguro con `textContent` y manejo de errores. |
| `tests/test_api.py` | Pruebas de integración con `TestClient` y clientes simulados; cubren éxito, fallo del servicio y archivos estáticos. |

## Solución de Problemas

| Síntoma | Causa probable | Solución |
|---|---|---|
| `Request to Ollama failed: ... Connection refused` | Ollama no está en ejecución. | Ejecuta `ollama serve` y comprueba `OLLAMA_URL`. |
| `model "..." not found` | El modelo no está descargado. | Ejecuta `ollama pull qwen2.5`. |
| `Invalid JSON response from Ollama: ...` | La URL no apunta a Ollama o un proxy devuelve HTML. | Verifica `OLLAMA_URL` con `curl` y usa el endpoint `/api/generate`. |
| La petición tarda demasiado o termina en `500` | El modelo es grande y el equipo no tiene recursos suficientes. | Aumenta `OLLAMA_TIMEOUT` o usa un modelo más pequeño. |
| `address already in use` | El puerto 8000 está ocupado. | Detén el otro proceso o cambia `APP_PORT` en `.env`. |
| `ModuleNotFoundError: No module named 'server'` | El servidor se lanzó desde otra carpeta. | Entra en `ai_news_summarizer` y ejecuta `python app.py` o `uvicorn app:app` desde ahí. |
| `ModuleNotFoundError: No module named 'multipart'` | Faltan dependencias de ejecución. | Activa el entorno virtual y ejecuta `pip install -r requirements.txt`. |
| `404` en `/static/...` | La carpeta `static/` no existe junto a `app.py`. | Conserva la estructura del proyecto o revisa `settings.static_dir`. |
| `422 Unprocessable Entity` | Falta un campo obligatorio del formulario o de la query. | Envía todos los campos indicados en la sección de ejemplos. |
| `500` con un mensaje genérico | El servicio externo falló; el detalle está en los registros. | Revisa la terminal donde corre Uvicorn para ver el error completo. |
| `NEWS_API_KEY` no configurada | El archivo `.env` no existe o la variable está vacía. | Copia `.env.example` a `.env` y define una clave válida de NewsAPI. |
| Error `401` de NewsAPI | Clave inválida, caducada o sin permisos. | Verifica la clave en el panel de NewsAPI y reinicia el servidor. |
| `429` o límite de peticiones | Se superó la cuota del plan gratuito. | Espera al reinicio de la cuota o usa otro plan. |
| La lista de titulares aparece vacía | La categoría no tiene noticias en ese momento. | Prueba otra categoría o vuelve a intentarlo más tarde. |

## Notas Adicionales

- La configuración se lee al arrancar: reinicia el servidor tras cambiar `.env`.
- Las pruebas usan dobles de prueba y no necesitan Ollama ni conexión a internet.
- La interfaz y la API se sirven desde el mismo origen, por lo que no hay CORS configurado.
- Los contratos de respuesta (`code`, `summary`, `response`, etc.) se mantienen estables respecto a la versión original.
- `NEWS_API_KEY` ya no está escrita directamente en el código: se lee de `.env` o del entorno.
- Si no hay artículos, se devuelve `articles: []` para que el frontend no falle.
- Los enlaces solo se renderizan si la URL usa `http` o `https`.
- La API gratuita de NewsAPI tiene límites de peticiones y puede no incluir todos los medios.
- La clave se envía tanto en cabecera como en el parámetro `apiKey`, igual que en la versión original.
- El backend no sirve la carpeta `static/` desde una ruta relativa: usa una ruta absoluta calculada desde `server/config.py`.
- Los registros incluyen fecha, nivel, módulo y mensaje; el detalle de los errores de Ollama aparece en la terminal de Uvicorn.
- Para producción se recomienda desactivar `reload`, usar un proxy inverso y limitar el acceso a la red local.
