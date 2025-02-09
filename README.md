# Multi-Model AI Chatbot

A chatbot application that leverages multiple AI models including OpenAI's GPT, Anthropic's Claude, and DeepSeek.

## Setup

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Create a .env file with your API keys:
   ```
   ANTHROPIC_API_KEY=your_anthropic_key
   OPENAI_API_KEY=your_openai_key
   DEEPSEEK_API_KEY=your_deepseek_key
   ```
4. Start the backend:
   ```bash
   uvicorn backend.main:app --reload
   ```
5. Start the frontend:
   ```bash
   streamlit run frontend/app.py
   ```

## Features

- Multiple AI model support
- Clean and intuitive UI
- Real-time chat interface
- Easy model switching
