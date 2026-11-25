"""Cliente para la API de titulares de NewsAPI.

La clave se lee de la configuración (``NEWS_API_KEY``) y nunca se escribe en
el código fuente.
"""
import logging
from typing import Any

import requests

from server.config import Settings

logger = logging.getLogger(__name__)


class NewsError(Exception):
    """Error al consultar la API de noticias."""


class NewsClient:
    """Cliente de ``/v2/top-headlines`` de NewsAPI.

    :param settings: Configuración con URL, clave y timeout de NewsAPI.
    :type settings: server.config.Settings
    """

    def __init__(self, settings: Settings) -> None:
        """Guarda la configuración necesaria para las consultas.

        :param settings: Configuración del servicio.
        :type settings: server.config.Settings
        :returns: No devuelve ningún valor.
        :rtype: None
        """
        self._settings = settings

    def fetch_top_headlines(self, category: str, limit: int = 3) -> list[dict[str, Any]]:
        """Obtiene los titulares más recientes de una categoría.

        :param category: Categoría de NewsAPI (``technology``, ``business``...).
        :type category: str
        :param limit: Número máximo de artículos a devolver.
        :type limit: int
        :returns: Lista de artículos tal como los entrega NewsAPI.
        :rtype: list[dict[str, typing.Any]]
        :raises NewsError: Si falta la clave, la petición falla o el estado no
            es 200.
        """
        if not self._settings.news_api_key:
            raise NewsError("La variable NEWS_API_KEY no está configurada.")

        headers = {"Authorization": f"Bearer {self._settings.news_api_key}"}
        params = {
            "category": category,
            "language": "en",
            "apiKey": self._settings.news_api_key,
        }

        try:
            response = requests.get(
                self._settings.news_api_url,
                params=params,
                headers=headers,
                timeout=self._settings.news_timeout,
            )
        except requests.exceptions.RequestException as exc:
            logger.error("Fallo al consultar NewsAPI: %s", exc)
            raise NewsError(f"Failed to fetch news articles: {exc}") from exc

        if response.status_code != 200:
            logger.error("NewsAPI respondió con estado %s", response.status_code)
            raise NewsError(f"Failed to fetch news articles: HTTP {response.status_code}")

        try:
            data = response.json()
        except ValueError as exc:
            raise NewsError("Failed to fetch news articles: invalid JSON") from exc

        articles = data.get("articles")
        if not isinstance(articles, list):
            return []
        return articles[:limit]
