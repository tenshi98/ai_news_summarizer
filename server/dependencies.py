"""Dependencias reutilizables para inyección en las rutas HTTP.

FastAPI resuelve estas funciones automáticamente. En las pruebas se pueden
sustituir mediante ``app.dependency_overrides``.
"""
from typing import Annotated

from fastapi import Depends

from server.config import Settings, get_settings
from server.services.ollama import OllamaClient
from server.services.news import NewsClient

SettingsDep = Annotated[Settings, Depends(get_settings)]
"""Alias de tipo para inyectar la configuración del servicio."""


def get_ollama_client(settings: SettingsDep) -> OllamaClient:
    """Construye un cliente de Ollama con la configuración actual.

    :param settings: Configuración inyectada por FastAPI.
    :type settings: server.config.Settings
    :returns: Cliente listo para generar texto.
    :rtype: server.services.ollama.OllamaClient
    """
    return OllamaClient(settings)


OllamaClientDep = Annotated[OllamaClient, Depends(get_ollama_client)]
"""Alias de tipo para inyectar el cliente de Ollama en una ruta."""


def get_news_client(settings: SettingsDep) -> NewsClient:
    """Construye un cliente de NewsAPI con la configuración actual.

    :param settings: Configuración inyectada por FastAPI.
    :type settings: server.config.Settings
    :returns: Cliente listo para consultar titulares.
    :rtype: server.services.news.NewsClient
    """
    return NewsClient(settings)


NewsClientDep = Annotated[NewsClient, Depends(get_news_client)]
"""Alias de tipo para inyectar el cliente de NewsAPI en una ruta."""
