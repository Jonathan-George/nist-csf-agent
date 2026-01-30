from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import traceback

from langchain_openai import ChatOpenAI

app = FastAPI(title="NIST CSF AI Agent")

# -----------------------------
# CORS
# -----------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------------
# Load LLM ONLY (NO FAISS)
# -----------------------------

llm = ChatOpenAI(
    model="deepseek/deepseek-chat",
    openai_api_key=os.getenv("OPENROUTER_API_KEY"),
    openai_api_base="https://openrouter.ai/api/v1",
    default_headers={
        "HTTP-Referer": "https://nist-csf-agent.onrender.com",
        "X-Title": "NIST CSF AI Agent"
    },
    temperature=0,
)

# -----------------------------
# Request Model
# -----------------------------

class ChatRequest(BaseModel):
    message: str

# -----------------------------
# Intent Detection (GUARDS ONLY)
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
# LLM Reasoning (NO RAG)
# -----------------------------

def llm_reason(message: str) -> str:
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

    prompt = f"""
{system_prompt}

USER QUESTION:
{message}
"""

    response = llm.invoke(prompt)

    clean = response.content

    # HARD STRIP MARKDOWN / FORMATTING
    clean = clean.replace("**", "")
    clean = clean.replace("*", "")
    clean = clean.replace("•", "")
    clean = clean.replace("-", "")
    clean = clean.replace("_", "")
    clean = clean.replace("`", "")
    clean = clean.replace("###", "")
    clean = clean.replace("##", "")
    clean = clean.replace("#", "")

    # Collapse excessive newlines
    clean = "\n".join(
        line.strip() for line in clean.splitlines() if line.strip()
    )

    return clean

# -----------------------------
# Chat Endpoint (CORRECTED)
# -----------------------------

@app.post("/chat")
def chat(request: ChatRequest):
    try:
        intent = detect_intent(request.message)

        if intent == "out_of_scope":
            return {
                "agent_mode": "refuse",
                "response": "I can only provide guidance based on the NIST Cybersecurity Framework."
            }

        answer = llm_reason(request.message)

        return {
            "agent_mode": intent,
            "response": answer
        }

    except Exception as e:
        print("LLM ERROR:")
        traceback.print_exc()

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )
