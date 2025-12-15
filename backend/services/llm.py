import os
from typing import List, Dict, Optional

class LLMService:
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.mock_mode = not bool(self.api_key)

    async def chat_completion(self, messages: List[Dict[str, str]], system_prompt: str = "") -> str:
        if self.mock_mode:
            return self._mock_response(messages, system_prompt)
        
        try:
            from openai import OpenAI
            client = OpenAI(api_key=self.api_key)
            
            # Prepare messages with system prompt
            api_messages = [{"role": "system", "content": system_prompt}] + messages
            
            response = client.chat.completions.create(
                model="gpt-4o-mini", # Using a fast, capable model
                messages=api_messages,
                temperature=0.7
            )
            return response.choices[0].message.content
        except ImportError:
            print("OpenAI library not found. Falling back to mock.")
            return self._mock_response(messages, system_prompt)
        except Exception as e:
            print(f"Error calling OpenAI: {e}. Falling back to mock.")
            return self._mock_response(messages, system_prompt)

    def _mock_response(self, messages: List[Dict[str, str]], system_prompt: str) -> str:
        last_msg = messages[-1]["content"].lower()
        
        # Legal Agent Simulator
        if "advogado" in system_prompt.lower() or "jurídico" in system_prompt.lower():
            if "infiltração" in last_msg or "vazamento" in last_msg:
                return """
                {
                    "viability_score": 85,
                    "analysis": "Pela Lei do Inquilinato (Art. 22), problemas estruturais são do proprietário. O caso é forte.",
                    "strategy": "Notificação extrajudicial imediata solicitando reparo em 48h.",
                    "missing_info": ["Fotos do dano", "Data do início do problema"]
                }
                """
            return """
            {
                "viability_score": 60,
                "analysis": "Preciso de mais detalhes para enquadrar na Lei 8.245/91.",
                "strategy": "Coletar evidências.",
                "missing_info": []
            }
            """

        # Forensic Agent Simulator
        if "forense" in system_prompt.lower():
            return """
            {
                "doc_type": "foto_dano",
                "extracted_data": {
                    "data_ocorrência": "2024-12-12",
                    "gravidade": "alta",
                    "elementos": ["mofo", "parede descascada"]
                },
                "confidence": 0.95
            }
            """
            
        return "Resposta simulada da IA."
