import httpx
import json
from typing import Dict, Any, Optional

OLLAMA_BASE_URL = "http://localhost:11434"
DEFAULT_MODEL = "qwen2.5:3b"

def ping_ollama() -> bool:
    """Kiểm tra kết nối tới Ollama API."""
    try:
        response = httpx.get(f"{OLLAMA_BASE_URL}/api/version", timeout=3.0)
        return response.status_code == 200
    except httpx.RequestError:
        return False

def check_model_exists(model_name: str = DEFAULT_MODEL) -> bool:
    """Kiểm tra xem model đã được tải về máy chưa."""
    try:
        response = httpx.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=3.0)
        if response.status_code == 200:
            models = response.json().get("models", [])
            return any(m.get("name") == model_name or m.get("name").startswith(model_name + ":") for m in models)
        return False
    except httpx.RequestError:
        return False

def generate_json(system_prompt: str, user_prompt: str, model: str = DEFAULT_MODEL) -> Optional[Dict[str, Any]]:
    """
    Gọi Ollama API để sinh ra nội dung JSON (Structured Output).
    """
    payload = {
        "model": model,
        "format": "json", # Ép format JSON theo tính năng mới của Ollama
        "stream": False,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
    }
    
    try:
        response = httpx.post(f"{OLLAMA_BASE_URL}/api/chat", json=payload, timeout=60.0)
        response.raise_for_status()
        result = response.json()
        content = result["message"]["content"]
        
        # Parse chuỗi JSON thành Dict
        return json.loads(content)
    except httpx.RequestError as e:
        raise Exception(f"Lỗi khi kết nối Ollama: {str(e)}")
    except json.JSONDecodeError:
        raise Exception("Ollama trả về nội dung không phải là JSON chuẩn.")
