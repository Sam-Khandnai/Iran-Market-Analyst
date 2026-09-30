from typing import Protocol

from market_analyst.config import get_settings


class ChatClient(Protocol):
    async def ainvoke(self, prompt: str) -> str: ...


class LangchainChatClient:
    def __init__(self, model):
        self._model = model

    async def ainvoke(self, prompt: str) -> str:
        resp = await self._model.ainvoke(prompt)
        return resp.content


def build_default_llm() -> ChatClient | None:
    """اولویت با provider سفارشی (مثل GapGPT) است؛ در نبود آن، OpenRouter امتحان می‌شود."""
    settings = get_settings()
    from langchain_openai import ChatOpenAI

    if settings.openai_api_key and settings.openai_base_url:
        model = ChatOpenAI(
            model=settings.model_name or "gpt-4o-mini",
            api_key=settings.openai_api_key,
            base_url=settings.openai_base_url,
            timeout=30,
        )
        return LangchainChatClient(model)

    if settings.openrouter_api_key:
        model = ChatOpenAI(
            model=settings.openrouter_model,
            api_key=settings.openrouter_api_key,
            base_url="https://openrouter.ai/api/v1",
            timeout=30,
        )
        return LangchainChatClient(model)

    return None