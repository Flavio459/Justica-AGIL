from services.llm import LLMService
import json

class ForensicAgent:
    def __init__(self, llm: LLMService):
        self.llm = llm

    async def analyze_evidence(self, file_path: str, context: str = "") -> dict:
        # In a real scenario, this would use OCR/Vision API first.
        # Here we simulate sending the "description" of the file to the LLM
        
        system_prompt = """
        Você é um Agente Forense Especialista em disputas imobiliárias.
        Sua função é extrair dados técnicos e fatos de documentos ou descrições de imagens.
        Retorne SEMPRE um JSON.
        """
        
        user_message = f"Analise este arquivo (simulado): {file_path}. Contexto: {context}"
        
        response = await self.llm.chat_completion(
            messages=[{"role": "user", "content": user_message}],
            system_prompt=system_prompt
        )
        
        try:
            return json.loads(response)
        except:
            return {"error": "Falha ao processar resposta do Forense", "raw": response}
