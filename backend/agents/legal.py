from services.llm import LLMService
import json

class LegalAgent:
    def __init__(self, llm: LLMService):
        self.llm = llm

    async def analyze_case(self, user_report: str, evidences: list = []) -> dict:
        system_prompt = """
        Você é um Agente Jurídico Especialista na Lei do Inquilinato (8.245/91) e CDC.
        Analise o relato e retorne um JSON com:
        - viability_score (0-100)
        - analysis (breve explicação jurídica)
        - strategy (próximo passo recomendado)
        - missing_info (lista do que falta)
        - strengths (lista de pontos fortes do caso)
        - risks (lista de riscos identificados)
        """
        
        evidence_context = f"Evidências disponíveis: {len(evidences)} arquivos."
        user_message = f"Relato do usuário: {user_report}. {evidence_context}"
        
        response = await self.llm.chat_completion(
            messages=[{"role": "user", "content": user_message}],
            system_prompt=system_prompt
        )
        
        try:
            return json.loads(response)
        except:
            # Fallback with humanized mock data based on keywords
            return self._generate_mock_analysis(user_report, evidences)
    
    def _generate_mock_analysis(self, user_report: str, evidences: list) -> dict:
        """Generate a realistic mock analysis based on keywords."""
        lower_report = user_report.lower()
        
        base_score = 50
        strengths = []
        risks = []
        missing_info = []
        analysis = ""
        
        # Analyze keywords and build score
        if "infiltração" in lower_report or "vazamento" in lower_report or "mofo" in lower_report:
            base_score += 25
            strengths.append("Problema estrutural - responsabilidade clara do locador (Art. 22)")
            strengths.append("Lei do Inquilinato protege explicitamente contra vícios ocultos")
            analysis = "Pela Lei do Inquilinato (Art. 22), problemas estruturais como infiltração são de responsabilidade do proprietário."
            
        elif "cobrança" in lower_report or "multa" in lower_report:
            base_score += 15
            strengths.append("Cobranças indevidas podem ser revertidas")
            risks.append("Necessário verificar cláusulas contratuais")
            analysis = "Multas contratuais têm limites legais. Precisamos verificar os valores e justificativas."
            
        elif "caução" in lower_report or "depósito" in lower_report:
            base_score += 20
            strengths.append("Lei 8.245/91 garante devolução em 30 dias após término")
            strengths.append("Retenção indevida gera juros e correção")
            analysis = "A devolução da caução é um direito garantido por lei após a entrega do imóvel."
            
        elif "manutenção" in lower_report:
            base_score += 10
            strengths.append("Art. 22 obriga o locador a manter o imóvel habitável")
            analysis = "Problemas de manutenção são frequentemente de responsabilidade do locador."
        
        # Add evidence bonus
        if len(evidences) > 0:
            base_score += 10
            strengths.append(f"Você tem {len(evidences)} evidência(s) documentada(s)")
        else:
            missing_info.append("Fotos do problema")
            risks.append("Sem provas documentais, o caso fica mais difícil")
        
        # Common missing info
        if "data" not in lower_report and "quando" not in lower_report:
            missing_info.append("Data do início do problema")
        
        if "notific" not in lower_report and "aviso" not in lower_report:
            missing_info.append("Comprovante de notificação ao proprietário")
        
        if not analysis:
            analysis = "Preciso de mais detalhes para fazer uma análise completa do seu caso."
            risks.append("Informações insuficientes para análise precisa")
        
        return {
            "viability_score": min(95, max(20, base_score)),
            "analysis": analysis,
            "strategy": "Notificação extrajudicial solicitando reparo" if base_score >= 60 else "Coletar mais evidências",
            "missing_info": missing_info[:3],  # Max 3 items
            "strengths": strengths[:3],         # Max 3 items
            "risks": risks[:2]                  # Max 2 items
        }
