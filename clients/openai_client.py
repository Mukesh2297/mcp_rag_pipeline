from openai import AsyncOpenAI
from dotenv import load_dotenv
from core.config import settings


LLM_LOCALHOST_URL = settings.LLM_LOCALHOST_URL
EMBEDDING_MODEL = settings.EMBEDDING_MODEL
CHAT_COMPLETIONS_MODEL = settings.CHAT_COMPLETIONS_MODEL

client = AsyncOpenAI(base_url=LLM_LOCALHOST_URL, api_key='not available')


async def encode_one(sentence: str) -> list[float]:
    response = await client.embeddings.create(
        input=sentence,
        model=EMBEDDING_MODEL
    )
    return response.data[0].embedding


async def get_llm_response(prompt):
    response = await client.chat.completions.create(messages = [{'role': 'system', 'content': prompt}], model=CHAT_COMPLETIONS_MODEL)
    return response.choices[0].message.content
