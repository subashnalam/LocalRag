import openai
from typing import Dict

class OpenAIModel:
    def __init__(self, api_key: str):
        self.client = openai.OpenAI(api_key=api_key)
    
    async def generate_response(self, message: str) -> Dict[str, str]:
        try:
            completion = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": message}]
            )
            return {"response": completion.choices[0].message.content}
        except Exception as e:
            return {"error": str(e)}
