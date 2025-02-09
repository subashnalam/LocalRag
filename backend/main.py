from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import anthropic
import openai
from dotenv import load_dotenv
import os

load_dotenv()

app = FastAPI()

# Load API keys
anthropic_client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
openai_client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

class ChatRequest(BaseModel):
    message: str
    model: str

@app.post("/chat")
async def chat(request: ChatRequest):
    try:
        if request.model == "claude":
            message = anthropic_client.messages.create(
                model="claude-2",
                max_tokens=1000,
                messages=[{"role": "user", "content": request.message}]
            )
            return {"response": message.content[0].text}
            
        elif request.model == "gpt":
            completion = openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": request.message}]
            )
            return {"response": completion.choices[0].message.content}
            
        elif request.model == "deepseek":
            # Implement DeepSeek API call here
            # This is a placeholder as DeepSeek implementation would depend on their API
            return {"response": "DeepSeek API implementation pending"}
            
        else:
            raise HTTPException(status_code=400, detail="Invalid model specified")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
