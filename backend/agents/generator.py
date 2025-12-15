from services.llm import LLMService
import json

class GeneratorAgent:
    def __init__(self, llm: LLMService):
        self.llm = llm

    async def generate_claim(self, case_data: dict) -> dict:
        # data contains: report, forensic_data, legal_analysis
        
        system_prompt = """
        Você é um Agente Gerador de Documentos Jurídicos.
        Sua função é transformar os dados do caso em uma Reclamação Formal para o Procon/Consumidor.gov.br.
        Retorne um JSON com:
        - title (Título do problema)
        - facts (Texto narrativo formal dos fatos, max 3000 chars)
        - request (Pedidos claros: o que o consumidor quer?)
        - value (Valor total estimado do prejuízo)
        """
        
        user_message = f"Dados do Caso: {json.dumps(case_data, ensure_ascii=False)}"
        
        response = await self.llm.chat_completion(
            messages=[{"role": "user", "content": user_message}],
            system_prompt=system_prompt
        )
        
        # Mock response if LLM fails or is in mock mode (likely the latter)
        if "Erro" in response or "{" not in response:
             return {
                "title": "Reclamação por Vício Oculto e Falha na Prestação de Serviço",
                "facts": f"No dia {case_data.get('date', 'recente')}, constatei problemas de {case_data.get('type', 'manutenção')} no imóvel locado. Apesar das tentativas de contato, a imobiliária não resolveu. (Texto gerado automaticamente baseado no relato: {case_data.get('report', '...')})",
                "request": "Requeiro o reparo imediato dos danos e abatimento no aluguel proporcional ao tempo de inutilização, conforme Art. 22 da Lei do Inquilinato.",
                "value": "R$ 2.500,00"
            }

        try:
            return json.loads(response)
        except:
            return {
                "title": "Reclamação Procon",
                "facts": "Erro ao gerar texto. Por favor edite.",
                "request": "Reparo imediato.",
                "value": "R$ 0,00"
            }
