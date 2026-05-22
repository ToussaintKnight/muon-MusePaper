"""LLM client for article distillation."""

from __future__ import annotations

import httpx


SYSTEM_PROMPT = (
    "You are a research assistant helping a solopreneur / technical founder "
    "stay on top of trends. Summarize the article concisely.\n\n"
    "Output format (Markdown):\n"
    "## Key Points\n"
    "- 3-5 bullets\n\n"
    "## Why It Matters\n"
    "1-2 sentences on business/technical relevance\n\n"
    "## Actionable Takeaways\n"
    "- 2-3 specific actions or follow-ups\n\n"
    "Keep the entire response under 300 words. Be direct."
)


async def distill_article(
    title: str,
    content: str,
    api_key: str,
    base_url: str = "https://api.openai.com/v1",
    model: str = "gpt-4o-mini",
    timeout: float = 30.0,
) -> str:
    """Distill an article into a structured summary via OpenAI-compatible API."""
    # Truncate content to stay within token limits (~8k chars ≈ 2k tokens)
    truncated = content[:8_000]
    user_message = f"Title: {title}\n\nContent:\n{truncated}"

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ],
        "temperature": 0.3,
        "max_tokens": 600,
    }

    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            r = await client.post(f"{base_url}/chat/completions", headers=headers, json=payload)
            r.raise_for_status()
            data = r.json()
            return data["choices"][0]["message"]["content"]
    except httpx.HTTPStatusError as exc:
        return f"*LLM API error ({exc.response.status_code}): {exc.response.text[:200]}*"
    except Exception as exc:
        return f"*LLM call failed: {exc}*"
