import os
from typing import List
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
import json
import re
from app.config import settings

GROK_API_KEY = settings.GROK_API_KEY
GROK_MODEL = "llama-3.3-70b-versatile"

# Initialize the LLM client once
llm_client = ChatGroq(groq_api_key=GROK_API_KEY, model=GROK_MODEL)

def generate_answer(question: str, context_chunks: List[str], chat_history: List[dict] = None) -> str:
    """
    Genearate answer using Grok LLaMa given a question and retrieved document chunks.

    Args:
        question (str): User's question.
        context_chunks (List[str]) : Retrieved text chunks relevant to the question.
        chat_history (List[dict], optionla) : List of previous conversation messages.
            Each dict should have 'role' ('user' or 'ai') and 'content'.

    Returns:
        str: LLM-generated answer.
    """

    chat_history = chat_history or []

    # Combine retrieved chunks into a single context string
    context = "\n\n".join(context_chunks)

    # Construct system prompt
    system_message = SystemMessage(
        content=(
            "You are a helpful AI assistant. "
            "Answer questions based ONLY on the provided context."
            "If the context does not contain enough information, say so politely."
        )
    )

    # Build conversational messages
    messages = [system_message]

    # Add previous chat history if available
    for msg in chat_history:
        if msg["role"] == "user":
            messages.append(HumanMessage(content=msg["content"]))
        elif msg["role"] == "ai":
            messages.append(AIMessage(content=msg["content"]))

    # Add the current question + context
    prompt_message = HumanMessage(
        content=f"Context:\n{context}\n\nQuestion: {question}\nAnswer:"
    )
    messages.append(prompt_message)

    # Invoke the LLM
    response = llm_client.invoke(messages)

    return response.content.strip()

def extract_json(prompt: str, retries: int = 2) -> dict:
    """
    Deterministic structured extraction using the LLM.
    Always returns parsed JSON dict (never raw string).

    Args:
        prompt: extraction instruction
        retries: retry attempts if JSON parsing fails

    Returns:
        dict
    """

    
    system = SystemMessage(
        content=(
            "You are a strict information extraction system.\n"
            "Return ONLY valid JSON.\n"
            "No explanations, no markdown, no text outside JSON."
        )
    )

    for _ in range(retries + 1):
        response = llm_client.invoke(
            [
                system,
                HumanMessage(content=prompt),
            ],
            temperature=0  # important for deterministic JSON
        )

        text = response.content.strip()

        # remove ```json blocks if model adds them
        text = re.sub(r"```json|```", "", text).strip()

        try:
            return json.loads(text)
        except Exception:
            continue

    # fallback
    return {}

# app/utils/llm.py

def extract_intent(message: str, retries: int = 2) -> str:
    """
    Classify the intent of a message as either 'BOOKING' or 'GENERAL'.
    Returns a clean string: "BOOKING" or "GENERAL".

    Args:
        message: User's message to classify
        retries: Number of retries if the LLM fails to return a valid intent

    Returns:
        str: "BOOKING" or "GENERAL"
    """

    intent_prompt = f"""
You are an intent classification system.
Decide whether this message is a booking request or a general query.
Respond ONLY with 'BOOKING' or 'GENERAL'.

Message: "{message}"
"""

    system = SystemMessage(
        content=(
            "You are a strict intent classifier.\n"
            "Respond ONLY with either BOOKING or GENERAL.\n"
            "No explanations, no markdown, no extra text."
        )
    )

    for _ in range(retries + 1):
        response = llm_client.invoke(
            [
                system,
                HumanMessage(content=intent_prompt),
            ],
            temperature=0  # deterministic
        )

        intent = response.content.strip().upper()

        if intent in ["BOOKING", "GENERAL"]:
            return intent

    # fallback if LLM fails
    return "GENERAL"