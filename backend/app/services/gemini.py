import asyncio
import json

import httpx

from app.logging_utils import get_logger


class GeminiConfigurationError(RuntimeError):
    """Raised when Gemini is not configured."""


class GeminiRateLimitError(RuntimeError):
    """Raised when Gemini rate limit or quota is exhausted."""


def clean_json_payload(raw_text: str) -> str:
    text = raw_text.strip()
    if text.startswith("```"):
        lines = text.splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].startswith("```"):
            lines = lines[:-1]
        text = "\n".join(lines).strip()
    return text


class GeminiClient:
    base_url = "https://generativelanguage.googleapis.com/v1beta/models"

    def __init__(
        self,
        api_key: str,
        model: str,
        max_retries: int = 3,
        retry_base_seconds: float = 2.0,
        transport=None,
    ) -> None:
        self.api_key = api_key
        self.model = model
        self.max_retries = max_retries
        self.retry_base_seconds = retry_base_seconds
        self.transport = transport
        self.logger = get_logger("gemini")

    def _build_url(self) -> str:
        if not self.api_key:
            raise GeminiConfigurationError("Missing GEMINI_API_KEY")
        return f"{self.base_url}/{self.model}:generateContent?key={self.api_key}"

    async def _generate(self, prompt: str, response_mime_type: str | None = None) -> str:
        payload: dict = {
            "contents": [
                {
                    "role": "user",
                    "parts": [{"text": prompt}],
                }
            ]
        }
        if response_mime_type:
            payload["generationConfig"] = {"responseMimeType": response_mime_type}

        for attempt in range(1, self.max_retries + 1):
            try:
                async with httpx.AsyncClient(timeout=120, transport=self.transport) as client:
                    response = await client.post(self._build_url(), json=payload)
            except httpx.RequestError as exc:
                message = f"Gemini request failed: {exc.__class__.__name__}"
                self.logger.warning("gemini_transport_error model=%s attempt=%s error=%s", self.model, attempt, message)
                if attempt >= self.max_retries:
                    raise RuntimeError(message) from exc
                await asyncio.sleep(self._retry_delay(attempt))
                continue

            if response.status_code == 429:
                detail = self._extract_error_message(response)
                self.logger.warning(
                    "gemini_rate_limited model=%s attempt=%s detail=%s",
                    self.model,
                    attempt,
                    detail,
                )
                if attempt >= self.max_retries:
                    raise GeminiRateLimitError(
                        "Gemini rate limit or quota reached. Wait a few minutes and try again, "
                        "or use another Gemini API key/model."
                    )
                await asyncio.sleep(self._retry_delay(attempt))
                continue

            if response.status_code >= 500:
                detail = self._extract_error_message(response)
                self.logger.warning(
                    "gemini_server_error model=%s attempt=%s status=%s detail=%s",
                    self.model,
                    attempt,
                    response.status_code,
                    detail,
                )
                if attempt >= self.max_retries:
                    raise RuntimeError(f"Gemini server error ({response.status_code}): {detail}")
                await asyncio.sleep(self._retry_delay(attempt))
                continue

            if response.status_code >= 400:
                detail = self._extract_error_message(response)
                raise RuntimeError(f"Gemini request failed ({response.status_code}): {detail}")

            break

        data = response.json()
        candidates = data.get("candidates", [])
        if not candidates:
            raise RuntimeError("Gemini returned no candidates")

        parts = candidates[0].get("content", {}).get("parts", [])
        text = "".join(part.get("text", "") for part in parts).strip()
        if not text:
            raise RuntimeError("Gemini returned an empty response")
        return text

    async def generate_json(self, prompt: str) -> dict:
        raw_text = await self._generate(prompt, response_mime_type="application/json")
        return json.loads(clean_json_payload(raw_text))

    async def generate_text(self, prompt: str) -> str:
        return await self._generate(prompt)

    def _retry_delay(self, attempt: int) -> float:
        return min(self.retry_base_seconds * (2 ** (attempt - 1)), 20.0)

    def _extract_error_message(self, response: httpx.Response) -> str:
        try:
            payload = response.json()
        except ValueError:
            return response.text.strip() or "Unknown Gemini error"

        error_payload = payload.get("error", {})
        return (
            error_payload.get("message")
            or error_payload.get("status")
            or response.text.strip()
            or "Unknown Gemini error"
        )
