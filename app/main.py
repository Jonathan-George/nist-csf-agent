from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import traceback

from langchain_openai import ChatOpenAI

# -----------------------------
# Validate API key EARLY
# -----------------------------

OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")
if not OPENROUTER_API_KEY:
    raise RuntimeError("OPENROUTER_API_KEY is not set in the environment")

# -----------------------------
# FastAPI App
# -----------------------------

app = FastAPI(title="NIST CSF AI Agent")

# -----------------------------
# CORS
# -----------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------------
# Load LLM (CORRECT + STABLE)
# -----------------------------

llm = ChatOpenAI(
    model="deepseek/deepseek-chat",
    api_key=OPENROUTER_API_KEY,                 # ✅ REQUIRED
    base_url="https://openrouter.ai/api/v1",    # ✅ REQUIRED
    default_headers={
        "HTTP-Referer": "https://nist-csf-agent.onrender.com",
        "X-Title": "NIST CSF AI Agent",
    },
    temperature=0,
)

# -----------------------------
# Request Model
# -----------------------------

class ChatRequest(BaseModel):
    message: str

# -----------------------------
# Intent Detection
# -----------------------------

def detect_intent(message: str) -> str:
    msg = message.lower().strip()

    if "outside nist" in msg:
        return "out_of_scope"
    if msg.startswith("explain"):
        return "teach"
    if "assessment" in msg or msg.startswith("assess"):
        return "assess"
    if msg.startswith(("yes", "no")):
        return "evaluate"

    return "general"

# -----------------------------
# LLM Reasoning (ASYNC)
# -----------------------------

async def llm_reason(message: str) -> str:
    system_prompt = (
        "You are a NIST Cybersecurity Framework expert AI. "
        "Always respond in plain conversational English. "
        "Never use markdown, bullet points, numbered lists, or headings. "
        "Do not structure answers like documentation. "
        "Respond like a human security consultant speaking naturally. "
        "Answer ONLY using the NIST Cybersecurity Framework. "
        "If the answer is not found, say: "
        "'This is not explicitly addressed in the NIST Cybersecurity Framework.'"
    )

    prompt = f"{system_prompt}\n\nUSER QUESTION:\n{message}"

    response = await llm.ainvoke(prompt)
    text = response.content

    for ch in ["**", "*", "•", "-", "_", "`", "#"]:
        text = text.replace(ch, "")

    return "\n".join(line.strip() for line in text.splitlines() if line.strip())

# -----------------------------
# Chat Endpoint
# -----------------------------

@app.post("/chat")
async def chat(request: ChatRequest):
    try:
        intent = detect_intent(request.message)

        if intent == "out_of_scope":
            return {
                "agent_mode": "refuse",
                "response": "I can only provide guidance based on the NIST Cybersecurity Framework.",
            }

        answer = await llm_reason(request.message)

        return {
            "agent_mode": intent,
            "response": answer,
        }

    except Exception:
        print("🔥 CHAT ERROR")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="LLM execution failed")
