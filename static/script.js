/**
 * @file Lógica de la interfaz de AI News Summarizer.
 *
 * Toda la comunicación con el backend se realiza con `fetch`. Las respuestas
 * del modelo se insertan en el DOM mediante `textContent` o creando nodos,
 * nunca con `innerHTML`, para evitar inyección de HTML.
 */

"use strict";

/**
 * Muestra un mensaje de error dentro de un contenedor.
 *
 * @param {HTMLElement} container - Elemento donde se mostrará el mensaje.
 * @param {string} message - Texto del error.
 * @returns {void}
 */
function showError(container, message) {
    container.replaceChildren();
    const paragraph = document.createElement("p");
    paragraph.className = "error-message";
    paragraph.textContent = message;
    container.appendChild(paragraph);
}

/**
 * Sustituye el contenido de un contenedor por un párrafo de texto plano.
 *
 * @param {HTMLElement} container - Elemento que se actualizará.
 * @param {string} text - Texto a mostrar.
 * @returns {void}
 */
function setParagraph(container, text) {
    container.replaceChildren();
    const paragraph = document.createElement("p");
    paragraph.textContent = text;
    container.appendChild(paragraph);
}

/** Selector de la categoría de noticias. */
const categorySelect = document.getElementById("category");
/** Botón que solicita las noticias. */
const fetchButton = document.getElementById("fetch-button");
/** Contenedor del resumen generado. */
const summaryDiv = document.getElementById("summary");
/** Contenedor de los titulares originales. */
const articlesDiv = document.getElementById("articles");

/**
 * Comprueba que una cadena sea una URL HTTP o HTTPS segura.
 *
 * @param {string} value - URL recibida de NewsAPI.
 * @returns {boolean} `true` si el protocolo es `http:` o `https:`.
 */
function isSafeUrl(value) {
    if (typeof value !== "string") {
        return false;
    }

    try {
        const url = new URL(value);
        return url.protocol === "http:" || url.protocol === "https:";
    } catch (error) {
        return false;
    }
}

/**
 * Pinta los titulares como párrafos con un enlace seguro.
 *
 * @param {HTMLElement} container - Contenedor de los artículos.
 * @param {Array<Object>} articles - Artículos devueltos por NewsAPI.
 * @returns {void}
 */
function renderArticles(container, articles) {
    container.replaceChildren();

    articles.forEach((article) => {
        const paragraph = document.createElement("p");
        const title = document.createElement("strong");
        title.textContent = article.title || "";
        paragraph.appendChild(title);

        const sourceName = article.source && article.source.name ? article.source.name : "";
        paragraph.appendChild(document.createTextNode(` (${sourceName})`));
        paragraph.appendChild(document.createElement("br"));

        if (isSafeUrl(article.url)) {
            const link = document.createElement("a");
            link.href = article.url;
            link.target = "_blank";
            link.rel = "noopener noreferrer";
            link.textContent = "Read more";
            paragraph.appendChild(link);
        }

        container.appendChild(paragraph);
    });
}

/**
 * Obtiene y resume los titulares de la categoría seleccionada.
 *
 * @async
 * @function fetchNews
 * @param {Event} event - Evento de clic del botón.
 * @returns {Promise<void>} No devuelve valor; actualiza el DOM.
 */
async function fetchNews(event) {
    event.preventDefault();

    try {
        const response = await fetch(`/fetch_news?category=${encodeURIComponent(categorySelect.value)}`);

        if (!response.ok) {
            articlesDiv.replaceChildren();
            showError(summaryDiv, "Error: Failed to fetch news.");
            return;
        }

        const data = await response.json();
        setParagraph(summaryDiv, data.summary);
        renderArticles(articlesDiv, data.articles);
    } catch (error) {
        articlesDiv.replaceChildren();
        showError(summaryDiv, "Error: Failed to fetch news.");
    }
}

document.addEventListener("DOMContentLoaded", () => {
    fetchButton.addEventListener("click", fetchNews);
});
