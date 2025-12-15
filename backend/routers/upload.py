from fastapi import APIRouter, UploadFile, File, HTTPException
import shutil
import os
import uuid
from typing import List

router = APIRouter()

UPLOAD_DIR = "temp_uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

ALLOWED_TYPES = ["image/jpeg", "image/png", "application/pdf"]
MAX_SIZE_MB = 10 * 1024 * 1024 # 10MB

from services.llm import LLMService
from agents.forensic import ForensicAgent

llm_service = LLMService()
forensic_agent = ForensicAgent(llm_service)

@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    # ... previous validation code ...
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(status_code=400, detail="Tipo de arquivo não suportado. Use JPG, PNG ou PDF.")
    
    file_ext = file.filename.split(".")[-1]
    filename = f"{uuid.uuid4()}.{file_ext}"
    file_path = os.path.join(UPLOAD_DIR, filename)
    
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        # Check size after saving
        if os.path.getsize(file_path) > MAX_SIZE_MB:
            os.remove(file_path)
            raise HTTPException(status_code=400, detail="Arquivo muito grande. Máximo 10MB.")
        
        # Determine context based on filename/type for the mock
        context = "Foto do Dano" if "image" in file.content_type else "Documento"
        
        # Call Forensic Agent
        analysis = await forensic_agent.analyze_evidence(file_path, context=context)
            
        return {
            "filename": filename,
            "original_name": file.filename,
            "path": file_path,
            "forensic_analysis": analysis
        }
    except Exception as e:
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(status_code=500, detail=f"Erro ao salvar arquivo: {str(e)}")
