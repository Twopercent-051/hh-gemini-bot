import httpx

from config import config
from src.notifications import send_error_notification


async def generate_respond(prompt: str):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={config.gemini.api_key}"
    headers = {"Content-Type": "application/json"}
    data = {"contents": [{"parts": [{"text": prompt}]}]}
    timeout = httpx.Timeout(timeout=10.0, read=15.0)
    async with httpx.AsyncClient(timeout=timeout) as client:
        response = await client.post(url, headers=headers, json=data)
        if response.status_code == 200:
            response_json = response.json()
            try:
                result = response_json["candidates"][0]["content"]["parts"][0]["text"]
                return result
            except (KeyError, IndexError):
                await send_error_notification(
                    code=response.status_code, text="Ошибка сериализации ответа", method="gemini"
                )
        else:
            await send_error_notification(text=response.text, code=response.status_code, method="gemini")
