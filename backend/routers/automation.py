from fastapi import APIRouter
from pydantic import BaseModel
from agents.navigator import NavigatorAgent
from typing import Optional

router = APIRouter()
navigator = NavigatorAgent()

class SubmitClaimRequest(BaseModel):
    claim_data: dict
    headless: bool = False  # False = Mostra navegador
    dry_run: bool = False   # True = Preenche mas não envia

@router.post("/automation/submit")
async def submit_claim(request: SubmitClaimRequest):
    result = await navigator.submit_claim(
        request.claim_data,
        headless=request.headless,
        dry_run=request.dry_run
    )
    return result
