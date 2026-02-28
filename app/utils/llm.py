import os
from typing import List
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

GROK_API_KEY = os.getenv("GROK_API_KEY")
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
