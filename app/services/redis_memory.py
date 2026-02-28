import redis
import json
from typing import List, Dict

REDIS_URL = "redis://localhost:6379/0"
r = redis.Redis.from_url(REDIS_URL, decode_responses=True)

def get_history(session_id: str) -> List[Dict[str, str]]:
    data = r.get(f"chat:{session_id}")
    if data:
        return json.loads(data)
    return []

def save_history(session_id: str, history: List[Dict[str, str]]) -> None:
    r.set(f"chat:{session_id}", json.dumps(history))