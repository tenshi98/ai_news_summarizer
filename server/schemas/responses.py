"""Modelos de respuesta del resumidor de noticias."""
from typing import Any

from pydantic import BaseModel, Field


class NewsResponse(BaseModel):
    """Resumen generado y titulares originales de NewsAPI."""

    summary: str = Field(..., description="Resumen generado por el modelo.")
    articles: list[dict[str, Any]] = Field(
        default_factory=list,
        description="Titulares originales devueltos por NewsAPI.",
    )
