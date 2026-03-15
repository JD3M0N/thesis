import asyncio

import httpx

from app.services.gemini import GeminiClient, GeminiRateLimitError, clean_json_payload


def test_gemini_429_message_is_sanitized() -> None:
    def handler(request):
        return httpx.Response(
            429,
            json={
                "error": {
                    "message": "Quota exceeded for free tier",
                    "status": "RESOURCE_EXHAUSTED",
                }
            },
            request=request,
        )

    client = GeminiClient(
        api_key="secret-key-should-not-leak",
        model="gemini-2.0-flash",
        max_retries=2,
        retry_base_seconds=0.01,
        transport=httpx.MockTransport(handler),
    )

    try:
        asyncio.run(client.generate_json("test"))
        raise AssertionError("Expected GeminiRateLimitError")
    except GeminiRateLimitError as exc:
        message = str(exc)
        assert "quota" in message.lower() or "rate limit" in message.lower()
        assert "secret-key-should-not-leak" not in message


def test_clean_json_payload_removes_markdown_fences() -> None:
    payload = clean_json_payload("```json\n{\"title\":\"Hola\"}\n```")
    assert payload == "{\"title\":\"Hola\"}"
