"""Rutas HTTP del servicio AI News Summarizer.

Expone la página de inicio y el endpoint ``/fetch_news``. La comunicación con
Ollama se delega en :class:`server.services.ollama.OllamaClient`, inyectado
por FastAPI.
"""
import logging
from typing import Annotated

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import FileResponse

from server.config import get_settings
from server.dependencies import OllamaClientDep, NewsClientDep
from server.schemas.responses import NewsResponse
from server.services.news import NewsError
from server.services.ollama import (
    OllamaClient,
    OllamaRequestError,
    OllamaResponseError,
)

logger = logging.getLogger(__name__)

router = APIRouter()
"""Enrutador con los endpoints públicos del servicio."""


@router.get("/", response_class=FileResponse, summary="Sirve la interfaz web")
def serve_homepage() -> FileResponse:
    """Devuelve el archivo ``static/index.html``.

    :returns: Respuesta con el HTML de la aplicación.
    :rtype: fastapi.responses.FileResponse
    """
    settings = get_settings()
    return FileResponse(settings.static_dir / "index.html")


def _generate_text(client: OllamaClient, prompt: str, fallback: str) -> str:
    """Genera texto y traduce los errores de Ollama a errores HTTP 500.

    :param client: Cliente de Ollama inyectado por FastAPI.
    :type client: server.services.ollama.OllamaClient
    :param prompt: Instrucción completa para el modelo.
    :type prompt: str
    :param fallback: Texto de reserva si la respuesta no trae ``response``.
    :type fallback: str
    :returns: Texto generado por el modelo.
    :rtype: str
    :raises fastapi.HTTPException: Con estado 500 si Ollama no responde o
        devuelve un cuerpo inválido.
    """
    try:
        return client.generate(prompt, fallback)
    except OllamaRequestError as exc:
        logger.error("Fallo al contactar con Ollama: %s", exc)
        raise HTTPException(
            status_code=500,
            detail=f"Request to Ollama failed: {exc}",
        ) from exc
    except OllamaResponseError as exc:
        logger.error("Respuesta inválida de Ollama: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.get(
    "/fetch_news",
    response_model=NewsResponse,
    summary="Resume los titulares de una categoría",
)
def fetch_and_summarize_news(
    news_client: NewsClientDep,
    client: OllamaClientDep,
    category: Annotated[
        str,
        Query(description="Categoría de NewsAPI (por defecto 'technology')."),
    ] = "technology",
) -> NewsResponse:
    """Obtiene los titulares más recientes y los resume con el modelo.

    :param news_client: Cliente de NewsAPI inyectado por FastAPI.
    :type news_client: server.services.news.NewsClient
    :param client: Cliente de Ollama inyectado por FastAPI.
    :type client: server.services.ollama.OllamaClient
    :param category: Categoría de noticias solicitada.
    :type category: str
    :returns: Resumen del modelo y titulares originales.
    :rtype: server.schemas.responses.NewsResponse
    :raises fastapi.HTTPException: ``500`` si NewsAPI u Ollama fallan.
    """
    try:
        articles = news_client.fetch_top_headlines(category=category, limit=3)
    except NewsError as exc:
        logger.error("Fallo al consultar NewsAPI: %s", exc)
        raise HTTPException(
            status_code=500,
            detail="Failed to fetch news articles",
        ) from exc

    # Sin artículos no se llama al modelo: se devuelve una lista vacía para que
    # el frontend pueda iterar sin errores.
    if not articles:
        return NewsResponse(
            summary="No news articles found for this category.",
            articles=[],
        )

    news_text = "\n".join(
        f"- {article.get('title', '')} ({article.get('source', {}).get('name', '')})"
        for article in articles
    )
    summary = _generate_text(
        client,
        f"Summarize these news headlines:\n{news_text}",
        "No summary available.",
    )
    return NewsResponse(summary=summary, articles=articles)
