from fastapi import APIRouter
from services.learning import learning_service

router = APIRouter()

@router.get("/insights")
async def get_insights():
    """Retorna o que o sistema aprendeu até agora."""
    return learning_service.get_insights()

@router.get("/knowledge")
async def get_full_knowledge():
    """Retorna todo o conhecimento acumulado (debug)."""
    return learning_service.knowledge

@router.post("/learn/company")
async def learn_company(user_input: str, official_name: str):
    """Ensina ao sistema um mapeamento de nome de empresa."""
    learning_service.learn_company_mapping(user_input, official_name)
    return {"status": "learned", "mapping": {user_input: official_name}}
