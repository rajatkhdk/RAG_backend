# AI Interview Assistant - RAG + Booking Backend
A production-style backend system that combines Retrieval Augmented Generation (RAG) with intent detection and interview booking.

The system can:
- Upload documents (pdf/txt) and index them into a vector database.
- Answer user questions using RAG
- Maintain conversation history
- Detect booking intent automatically
- Extract structured booking info using LLM
- Store bookings in SQL database

This project demonstrates LLM engineering + backend system design, not just a chatbot.

# Features

1. **Document Ingestion**
- Upload pdf/txt
- Chunk text
- Generate embeddings
- Store vectors in Qdrant
- Store metadata in SQL

2. **Conversatinal RAG API**
- Retrieves top-k relevant chunks
- Feeds context to LLM
- Maintain chat history using Redis

3. **Smart Intent Detection**
- Classifies:
    - General: normal RAG response
    - Booking: extract structured details

4. **Interview Booking**
- LLM extracts:
    - name
    - email
    - date
    - time
- Saves to SQL DB
- Returns confirmation JSON

# Qdrant
Since this is a backend demo, I used self-hosted Qdrant instead of managed services like Pinecone.

Benefits:
- runs locally woth Docker
- no API keys
- reproducible

# Installation and Setup

1. Clone repo

```bash
git clone <repo-url>
cd project
```
2. Environment variables: <br>
create .env
```
REDIS_HOST=localhost
REDIS_PORT=6379

QDRANT_HOST=localhost
QDRANT_PORT=6333

DATABASE_URL=sqlite:///./app.db

GROK_API_KEY= your_api_key
```
3. Run with docker
```bash
docker compose up -d --build
```
Starts:
- Qdrant
- Redis

4. Locally:
```bash
source .venv/bin/activate
uv add -r requirement.txt
uvicorn app.main:app --reload
```
Make sure Qdrant and Redis are running

# API Endpoints

in swagger: http://127.0.0.1:8000/docs

1. POST /ingest/upload
Upload pdf/txt and index into vector DB.

```code
strategy: fixed or sentence
file: Choose/upload .pdf/.txt file
```

2. POST /conversational/query

```code
session_id: text
message: question
```

# Demo flow
- Step 1: Upload docs
- Step 2: Ask questions
```code
"What is the evaluation metric used?"
```
- Step 3: Book interview
```code
"I an Rajat ans I want to schedule an interview tomorrow at 3pm, my email is xyz@gmail.com"
```
