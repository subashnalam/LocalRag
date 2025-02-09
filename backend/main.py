from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from .models import AnthropicModel, OpenAIModel, DeepseekModel
from .config.settings import Settings

app = FastAPI()
settings = Settings()

# Initialize models
anthropic_model = AnthropicModel(settings.ANTHROPIC_API_KEY)
openai_model = OpenAIModel(settings.OPENAI_API_KEY)
deepseek_model = DeepseekModel(settings.DEEPSEEK_API_KEY)

class ChatRequest(BaseModel):
    message: str
    model: str

@app.post("/chat")
async def chat(request: ChatRequest):
    try:
        if request.model == "claude":
            return await anthropic_model.generate_response(request.message)
        elif request.model == "gpt":
            return await openai_model.generate_response(request.message)
        elif request.model == "deepseek":
            return await deepseek_model.generate_response(request.message)
        else:
            raise HTTPException(status_code=400, detail="Invalid model specified")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
