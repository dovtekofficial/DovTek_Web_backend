# backend/main.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from models import ScanRequest, ScanResult
from analyzer import analyze_message
from prompts import DEMO_SCENARIOS

from dotenv import load_dotenv
load_dotenv()


app = FastAPI(title="FraudShield API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],        # ← allows Chrome extension origin
    allow_credentials=False,    # ← must be False when using wildcard
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/scan", response_model=ScanResult)
async def scan(body: ScanRequest):
    try:
        return await analyze_message(body.message)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@app.get("/demo/{scenario_id}")
async def get_demo(scenario_id: str):
    msg = DEMO_SCENARIOS.get(scenario_id)
    if not msg:
        raise HTTPException(status_code=404, detail="Demo not found")
    return {"message": msg}

@app.get("/health")
async def health():
    return {"status": "ok"}