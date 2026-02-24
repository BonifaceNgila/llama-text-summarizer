from fastapi import FastAPI, Form
import requests

app = FastAPI()

@app.post("/summarize/")
def summarize(text: str = Form(...)):
    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": "llama2",
            "prompt": f"Summarize this:\n\n{text}",
            "stream": False
        }
    )
    result = response.json()
    return {"summary": result["response"]}
