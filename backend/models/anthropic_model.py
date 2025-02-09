import anthropic
from typing import Dict

class AnthropicModel:
    def __init__(self, api_key: str):
        self.client = anthropic.Anthropic(api_key=api_key)
    
    async def generate_response(self, message: str) -> Dict[str, str]:
        try:
            response = self.client.messages.create(
                model="claude-2",
                max_tokens=1000,
                messages=[{"role": "user", "content": message}]
            )
            return {"response": response.content[0].text}
        except Exception as e:
            return {"error": str(e)}
