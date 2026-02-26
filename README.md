# Text Summarizer (LLaMA + FastAPI + Streamlit)

A simple local text summarization app using:
- **FastAPI** backend
- **Streamlit** frontend
- **Ollama** (`llama2`) as the local LLM
- <img width="624" height="750" alt="image" src="https://github.com/user-attachments/assets/1d18822c-fdf6-401d-b1c9-28231b1b20be" />


## Project Structure

```text
textsum/
├── backend/
│   └── main.py
├── frontend/
│   └── app.py
├── venv/
├── requirements.txt
└── README.md
```

## Prerequisites

- Python 3.10+
- Ollama installed and running
- `llama2` model available in Ollama

## Setup

1. Create and activate virtual environment

### PowerShell (Windows)

```powershell
python -m venv venv
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass -Force
.\venv\Scripts\Activate.ps1
```

2. Install dependencies

```powershell
pip install -r requirements.txt
```

3. Ensure Ollama is running and model is available

```powershell
ollama serve
ollama pull llama2
```

## Run the App

Open separate terminals (with the virtual environment activated):

1. Start backend (FastAPI)

```powershell
uvicorn backend.main:app --reload --port 8000
```

2. Start frontend (Streamlit)

```powershell
streamlit run frontend/app.py
```

3. Open browser

- Streamlit UI: http://localhost:8501
- FastAPI docs: http://localhost:8000/docs

## API Endpoint

### `POST /summarize/`

Form field:
- `text` (string)

Response:

```json
{
  "summary": "..."
}
```

## How It Works

- Frontend sends user text to `http://localhost:8000/summarize/`
- Backend forwards a prompt to Ollama at `http://localhost:11434/api/generate`
- Backend returns the generated summary to frontend

## Troubleshooting

- **PowerShell activation blocked**:
  - Run: `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass -Force`
  - Then: `.\venv\Scripts\Activate.ps1`
- **`source` not recognized on Windows**:
  - Use PowerShell activation above (do not use `source`)
- **Ollama connection errors**:
  - Confirm Ollama is running on `localhost:11434`
  - Confirm model exists: `ollama list`
