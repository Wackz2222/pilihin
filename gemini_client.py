"""Thin wrapper around the Gemini API with streaming and a search fallback."""

from dataclasses import dataclass, field
from typing import Callable, Iterator

from google import genai
from google.genai import errors, types

MAX_HISTORY = 20


class ChatError(Exception):
    """Error with a message that is safe to show to the user."""


@dataclass
class StreamResult:
    text: str = ""
    sources: list = field(default_factory=list)


def friendly_error(exc: Exception) -> str:
    if isinstance(exc, errors.APIError):
        code = exc.code or 0
        message = str(exc)
        if code in (401, 403) or (code == 400 and "API key" in message):
            return "API key Gemini tidak valid atau tidak punya akses. Periksa GEMINI_API_KEY."
        if code == 429:
            return "Kuota Gemini habis atau permintaan terlalu sering. Tunggu sebentar lalu coba lagi."
        if code == 404:
            return "Model Gemini tidak ditemukan. Periksa pengaturan GEMINI_MODEL."
        if code >= 500:
            return "Layanan Gemini sedang bermasalah. Silakan coba beberapa saat lagi."
        return f"Gemini menolak permintaan ({code}). Coba ubah pertanyaan Anda."
    return "Gagal terhubung ke Gemini. Periksa koneksi internet lalu coba lagi."


def to_contents(history: list) -> list:
    contents = []
    for msg in history[-MAX_HISTORY:]:
        if not msg.get("content"):
            continue
        role = "model" if msg["role"] == "assistant" else "user"
        if not contents and role == "model":
            continue  # conversation must start with a user turn
        contents.append(types.Content(role=role, parts=[types.Part(text=msg["content"])]))
    return contents


def collect_sources(chunk, result: StreamResult) -> None:
    for candidate in chunk.candidates or []:
        metadata = candidate.grounding_metadata
        for item in (metadata.grounding_chunks if metadata else None) or []:
            web = item.web
            if web and web.uri and all(s["uri"] != web.uri for s in result.sources):
                result.sources.append({"title": web.title or web.uri, "uri": web.uri})


class Advisor:
    def __init__(self, api_key: str, model: str, search: bool = True):
        self.client = genai.Client(api_key=api_key)
        self.model = model
        self.search = search

    def stream(
        self,
        history: list,
        system_instruction: Callable[[bool], str],
        result: StreamResult,
    ) -> Iterator[str]:
        """Yield response text chunks. Falls back to no search if grounding fails."""
        contents = to_contents(history)
        attempts = [True, False] if self.search else [False]

        for i, use_search in enumerate(attempts):
            config = types.GenerateContentConfig(
                system_instruction=system_instruction(use_search),
                temperature=0.6,
                tools=[types.Tool(google_search=types.GoogleSearch())] if use_search else None,
            )
            try:
                for chunk in self.client.models.generate_content_stream(
                    model=self.model, contents=contents, config=config
                ):
                    if chunk.text:
                        result.text += chunk.text
                        yield chunk.text
                    collect_sources(chunk, result)
                return
            except Exception as exc:
                is_last = i == len(attempts) - 1
                if result.text or is_last:
                    raise ChatError(friendly_error(exc)) from exc
