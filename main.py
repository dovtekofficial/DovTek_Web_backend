# backend/main.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
load_dotenv()
 
from database import engine
import db_models
from routers import auth_router, scan_router
from prompts import DEMO_SCENARIOS
 
# Create all DB tables on startup if they don't exist
#db_models.Base.metadata.create_all(bind=engine)
 
app = FastAPI(title="FraudShield API", version="2.0.0")
 
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)
 
# ── Routers ──────────────────────────────────────────────────────────────────
app.include_router(auth_router.router)
app.include_router(scan_router.router)
 
 
# ── Existing Endpoints (unchanged) ───────────────────────────────────────────
@app.get("/demo/{scenario_id}")
async def get_demo(scenario_id: str):
    msg = DEMO_SCENARIOS.get(scenario_id)
    if not msg:
        raise HTTPException(status_code=404, detail="Demo not found")
    return {"message": msg}
 
@app.get("/health")
async def health():
    return {"status": "ok"}