from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from typing import Dict, Any, Optional
import asyncio
from services.orchestrator import orchestrator_instance

router = APIRouter(prefix="/api/submission", tags=["submission"])

class ClaimData(BaseModel):
    company_name: str
    facts: str
    request: str

@router.post("/start")
async def start_browser():
    """Lança o navegador oficial do usuário em modo seguro"""
    try:
        # Run blocking function in thread pool to avoid blocking event loop
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, orchestrator_instance.launch_browser)
        return {"status": "browser_launched", "message": "Navegador aberto. Aguardando login..."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/status")
async def check_status():
    """Verifica se o usuário já fez login"""
    status = await orchestrator_instance.connect_and_check_login()
    return status

@router.post("/execute")
async def execute_automation(data: ClaimData, request: Request):
    """Quando logado, executa a automação"""
    # Roda em background idealmente, mas aqui vamos esperar para ver o log
    # Em produção, usar BackgroundTasks do FastAPI
    
    auth_header = request.headers.get('Authorization')
    token = None
    if auth_header and auth_header.startswith("Bearer "):
         token = auth_header.split(" ")[1]

    try:
        await orchestrator_instance.run_automation(data.dict(), auth_token=token)
        return {"status": "automation_started"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@router.post("/stop")
async def stop_browser():
    """Fecha o navegador forçadamente"""
    orchestrator_instance.stop_browser()
    return {"status": "browser_closed"}
