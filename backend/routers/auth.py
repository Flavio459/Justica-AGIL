from fastapi import APIRouter, HTTPException, Request, Depends
from fastapi.responses import RedirectResponse
import uuid
import os
import httpx
from typing import Optional
from pydantic import BaseModel
from jose import jwt

router = APIRouter()

# --- MOCK DATABASE ---
# Em produção, isso seria Redis ou SQL
MOCK_USERS_DB = {}
MOCK_SESSIONS = {}

class User(BaseModel):
    id: str
    cpf: str
    name: str
    email: str
    access_token: str

# --- CONFIG ---
USE_MOCK_AUTH = os.getenv("USE_MOCK_AUTH", "true").lower() == "true"
GOV_BR_CLIENT_ID = os.getenv("GOV_BR_CLIENT_ID", "justica_agil_mock_id")
GOV_BR_CLIENT_SECRET = os.getenv("GOV_BR_CLIENT_SECRET", "mock_secret")
GOV_BR_REDIRECT_URI = os.getenv("GOV_BR_REDIRECT_URI", "http://localhost:8000/auth/callback")
GOV_BR_AUTH_URL = "https://sso.staging.acesso.gov.br/authorize" # Staging URL example
GOV_BR_TOKEN_URL = "https://sso.staging.acesso.gov.br/token"     # Staging URL example
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")

@router.get("/auth/login")
async def login():
    """Redireciona para o Gov.br ou Mock"""
    state = str(uuid.uuid4())
    
    if USE_MOCK_AUTH:
        # Mock: redireciona direto para callback simulando sucesso
        mock_auth_url = f"/api/auth/callback?code=mock_govbr_code_123&state={state}"
        return RedirectResponse(mock_auth_url)
    else:
        # Real: redireciona para Gov.br
        params = {
            "response_type": "code",
            "client_id": GOV_BR_CLIENT_ID,
            "scope": "openid email profile cpf",
            "redirect_uri": GOV_BR_REDIRECT_URI,
            "state": state,
            "nonce": str(uuid.uuid4())
        }
        query_string = "&".join([f"{k}={v}" for k, v in params.items()])
        return RedirectResponse(f"{GOV_BR_AUTH_URL}?{query_string}")

@router.get("/auth/callback")
async def callback(code: str, state: str):
    """Callback que recebe o code e troca por token"""
    if not code:
        raise HTTPException(status_code=400, detail="Code not found")
    
    user_data = None
    access_token_val = None

    if USE_MOCK_AUTH:
        # Simula troca de token
        user_id = str(uuid.uuid4())
        fake_token = f"govbr_access_token_{uuid.uuid4()}"
        user_data = User(
            id=user_id,
            cpf="123.456.789-00",
            name="Cidadão Brasileiro Teste",
            email="cidadao@exemplo.com",
            access_token=fake_token
        )
        access_token_val = fake_token
    else:
        # Real Token Exchange
        try:
            async with httpx.AsyncClient() as client:
                data = {
                    "grant_type": "authorization_code",
                    "code": code,
                    "redirect_uri": GOV_BR_REDIRECT_URI,
                    "client_id": GOV_BR_CLIENT_ID,
                    "client_secret": GOV_BR_CLIENT_SECRET
                }
                # Basic Auth header might be needed depending on specific Gov.br env, 
                # but standard OAuth2 POST body is often sufficient or required.
                resp = await client.post(GOV_BR_TOKEN_URL, data=data)
                resp.raise_for_status()
                token_data = resp.json()

                access_token_val = token_data.get("access_token")
                id_token = token_data.get("id_token")
                
                # Decode ID Token (without verification for now as we lack public key)
                # In prod: fetch JWKS from Gov.br and verify signature
                decoded_token = jwt.get_unverified_claims(id_token)
                
                user_id = decoded_token.get("sub")
                cpf = decoded_token.get("cpf", "")
                name = decoded_token.get("name", "Unknown")
                email = decoded_token.get("email", "")

                user_data = User(
                    id=user_id,
                    cpf=cpf,
                    name=name,
                    email=email,
                    access_token=access_token_val
                )

        except Exception as e:
            print(f"Auth Error: {e}")
            raise HTTPException(status_code=500, detail="Authentication failed with Gov.br")
    
    # Save user to Mock DB (in memory)
    if user_data:
        MOCK_USERS_DB[user_data.id] = user_data
        
        # Create App Session
        session_token = str(uuid.uuid4())
        MOCK_SESSIONS[session_token] = user_data.id
        
        # Redirect to Frontend
        return RedirectResponse(f"{FRONTEND_URL}?token={session_token}")
    
    raise HTTPException(status_code=500, detail="Failed to process user data")

@router.get("/auth/me")
async def get_current_user(token: Optional[str] = None):
    """Retorna usuário logado via token de sessão"""
    if not token or token not in MOCK_SESSIONS:
        raise HTTPException(status_code=401, detail="Não autenticado")
    
    user_id = MOCK_SESSIONS[token]
    user = MOCK_USERS_DB.get(user_id)
    
    if not user:
        raise HTTPException(status_code=401, detail="Usuário não encontrado")
        
    return {
        "id": user.id,
        "name": user.name,
        "cpf": user.cpf,
        "gov_br_authenticated": True
    }
