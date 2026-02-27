from fastapi import FastAPI, Form
from fastapi import HTTPException
import requests

app = FastAPI()

@app.post("/summarize/")
def summarize(text: str = Form(...)):
    if not text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty.")

    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "llama2",
                "prompt": f"Summarize this:\n\n{text}",
                "stream": False,
            },
            timeout=120,
        )
        response.raise_for_status()
        result = response.json()
        summary = result.get("response")
        if not summary:
            raise HTTPException(status_code=502, detail="Invalid response from Ollama.")
        return {"summary": summary}
    except requests.exceptions.ConnectionError:
        raise HTTPException(status_code=503, detail="Cannot connect to Ollama on localhost:11434.")
    except requests.exceptions.Timeout:
        raise HTTPException(status_code=504, detail="Ollama request timed out.")
    except requests.exceptions.RequestException as exc:
        raise HTTPException(status_code=502, detail=f"Ollama request failed: {exc}")
