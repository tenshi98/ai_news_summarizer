"""Pruebas de integración del servicio AI News Summarizer.

Se sustituyen los clientes externos por dobles de prueba para no depender de
un servidor Ollama ni de conexión a internet.
"""
import pytest
from fastapi.testclient import TestClient

from server.application import app
from server.dependencies import get_ollama_client, get_news_client
from server.services.news import NewsError
from server.services.ollama import OllamaRequestError


class FakeOllamaClient:
    """Doble del cliente de Ollama con respuesta o error configurables."""

    def __init__(self, reply: str = "texto simulado", error: Exception | None = None) -> None:
        """Configura la respuesta que devolverá el doble.

        :param reply: Texto simulado que se devolverá.
        :type reply: str
        :param error: Excepción que se lanzará al generar.
        :type error: Exception | None
        :returns: No devuelve ningún valor.
        :rtype: None
        """
        self._reply = reply
        self._error = error

    def generate(self, prompt: str, fallback: str) -> str:
        """Devuelve el texto simulado o lanza el error configurado.

        :param prompt: Prompt recibido (no se utiliza en el doble).
        :type prompt: str
        :param fallback: Texto de reserva (no se utiliza en el doble).
        :type fallback: str
        :returns: Texto simulado.
        :rtype: str
        :raises Exception: El error configurado, si existe.
        """
        if self._error is not None:
            raise self._error
        return self._reply


class FakeNewsClient:
    """Doble del cliente de NewsAPI."""

    def __init__(
        self,
        articles: list[dict] | None = None,
        error: Exception | None = None,
    ) -> None:
        """Configura los artículos o el error que devolverá el doble.

        :param articles: Artículos simulados que se devolverán.
        :type articles: list[dict] | None
        :param error: Excepción que se lanzará al consultar.
        :type error: Exception | None
        :returns: No devuelve ningún valor.
        :rtype: None
        """
        self._articles = articles or []
        self._error = error

    def fetch_top_headlines(self, category: str, limit: int = 3) -> list[dict]:
        """Devuelve los artículos simulados o lanza el error configurado.

        :param category: Categoría solicitada.
        :type category: str
        :param limit: Número máximo de artículos.
        :type limit: int
        :returns: Lista de artículos simulados.
        :rtype: list[dict]
        :raises Exception: El error configurado, si existe.
        """
        if self._error is not None:
            raise self._error
        return self._articles[:limit]


@pytest.fixture(autouse=True)
def _clear_dependency_overrides():
    """Limpia las sustituciones de dependencias después de cada prueba."""
    yield
    app.dependency_overrides.clear()


def build_client(ollama: FakeOllamaClient, news: FakeNewsClient) -> TestClient:
    """Crea un cliente HTTP con las dependencias externas sustituidas.

    :returns: Cliente de pruebas de FastAPI.
    :rtype: fastapi.testclient.TestClient
    """
    app.dependency_overrides[get_ollama_client] = lambda: ollama
    app.dependency_overrides[get_news_client] = lambda: news
    return TestClient(app)


def test_homepage_returns_html() -> None:
    """La raíz debe servir la interfaz web."""
    with build_client(FakeOllamaClient(), FakeNewsClient()) as client:
        response = client.get("/")

    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]


def test_static_assets_are_served() -> None:
    """El CSS y el JS extraídos deben servirse desde ``/static``."""
    with build_client(FakeOllamaClient(), FakeNewsClient()) as client:
        css_response = client.get("/static/style.css")
        js_response = client.get("/static/script.js")

    assert css_response.status_code == 200
    assert js_response.status_code == 200


def test_fetch_news_returns_summary_and_articles() -> None:
    """La respuesta debe incluir el resumen y los titulares originales."""
    articles = [
        {
            "title": "Titular de prueba",
            "source": {"name": "Medio de prueba"},
            "url": "https://example.com/noticia",
        }
    ]
    with build_client(
        FakeOllamaClient(reply="Resumen simulado de titulares tecnológicos."),
        FakeNewsClient(articles=articles),
    ) as client:
        response = client.get("/fetch_news", params={"category": "technology"})

    assert response.status_code == 200
    body = response.json()
    assert body["summary"] == "Resumen simulado de titulares tecnológicos."
    assert body["articles"] == articles


def test_fetch_news_handles_news_api_failure() -> None:
    """Un fallo de NewsAPI debe responder 500 con el mensaje original."""
    news = FakeNewsClient(error=NewsError("clave inválida"))
    with build_client(FakeOllamaClient(), news) as client:
        response = client.get("/fetch_news")

    assert response.status_code == 500
    assert response.json()["detail"] == "Failed to fetch news articles"


def test_fetch_news_returns_empty_articles_when_none_found() -> None:
    """Sin artículos no se debe llamar al modelo y se devuelve lista vacía."""
    with build_client(FakeOllamaClient(), FakeNewsClient(articles=[])) as client:
        response = client.get("/fetch_news")

    assert response.status_code == 200
    assert response.json() == {
        "summary": "No news articles found for this category.",
        "articles": [],
    }
