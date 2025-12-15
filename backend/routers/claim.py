from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from services.llm import LLMService
from agents.generator import GeneratorAgent
from agents.legal import LegalAgent

router = APIRouter()

llm_service = LLMService()
generator_agent = GeneratorAgent(llm_service)
legal_agent = LegalAgent(llm_service)

class GenerateClaimRequest(BaseModel):
    report: str
    forensic_data: dict = {}
    legal_analysis: dict = {}

class AnalyzeRequest(BaseModel):
    report: str
    evidences: List[str] = []

class AnalysisResponse(BaseModel):
    viability_score: int
    analysis: str
    strategy: str
    missing_info: List[str] = []
    strengths: List[str] = []
    risks: List[str] = []

@router.post("/claim/generate")
async def generate_claim_endpoint(request: GenerateClaimRequest):
    case_data = {
        "report": request.report,
        "forensic_data": request.forensic_data,
        "legal_analysis": request.legal_analysis
    }
    
    result = await generator_agent.generate_claim(case_data)
    return result

@router.post("/claim/analyze", response_model=AnalysisResponse)
async def analyze_claim_endpoint(request: AnalyzeRequest):
    """Analyze a claim and return viability score with transparent breakdown."""
    analysis = await legal_agent.analyze_case(
        user_report=request.report,
        evidences=request.evidences
    )
    
    return AnalysisResponse(
        viability_score=analysis.get("viability_score", 50),
        analysis=analysis.get("analysis", "Análise em processamento."),
        strategy=analysis.get("strategy", "Coletar mais informações."),
        missing_info=analysis.get("missing_info", []),
        strengths=analysis.get("strengths", []),
        risks=analysis.get("risks", [])
    )
