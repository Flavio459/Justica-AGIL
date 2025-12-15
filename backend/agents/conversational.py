from services.llm import LLMService
from agents.legal import LegalAgent
import json

class ConversationalAgent:
    def __init__(self, llm: LLMService, legal_agent: LegalAgent):
        self.llm = llm
        self.legal_agent = legal_agent

    async def chat(self, messages: list, context: dict = None) -> dict:
        """
        Orchestrate the conversation.
        1. Check if we need specific legal analysis.
        2. Generate a response using the persona "Ju".
        """
        
        system_prompt = """
        Você é a 'Ju', uma assistente jurídica virtual do 'Procon Ágil'.
        
        SUA PERSONA:
        - Empática: Você entende que problemas de consumo/moradia são estressantes.
        - Profissional: Você passa segurança e conhecimento.
        - Clara: Evita "juridiquês" desnecessário. Explica termos difíceis.
        - Proativa: Guia o usuário para a solução (fazer a reclamação).
        
        SEUS OBJETIVOS:
        1. Acolher o usuário e entender o problema.
        2. Coletar fatos principais (O que aconteceu? Quando? Tem provas?).
        3. Se o caso parecer viável, motive o usuário a usar a ferramenta de "Gerar Reclamação" ou "Upload de Arquivos".
        
        LIMITES:
        - NÃO PRESTE CONSULTORIA JURÍDICA FORMAL (não assine como advogada, não garanta ganho de causa).
        - Use frases como "Pela lei...", "Geralmente...", "Nesse tipo de caso...".
        
        CONHECIMENTO BASE (Lei do Inquilinato 8.245/91 e CDC):
        - Infiltração/Estrutural: Responsabilidade do proprietário (Art. 22).
        - Manutenção simples: Responsabilidade do inquilino (Art. 23).
        - Caução: Deve ser devolvida corrigida ao fim do contrato.
        - Multa rescisória: Deve ser proporcional ao tempo restante.
        
        Se o usuário disser algo como "Quero processar" ou "Gerar documento", inicie a coleta de dados ou indique os botões de ação.
        """

        # Extract last user message for analysis trigger
        last_user_msg = messages[-1]['content'] if messages else ""
        
        # 1. Quick Analysis Trigger (heuristic or LLM based)
        # If the user gives a substantial report, we try to get a legal insight to feed the chat context
        analysis_context = ""
        if len(last_user_msg.split()) > 5: # Only analyze if there's enough text
            try:
                # We do a 'silent' analysis call
                analysis = await self.legal_agent.analyze_case(last_user_msg)
                if analysis.get('viability_score', 0) > 60:
                   analysis_context = f"""
                   [INFO DO SISTEMA: O Agente Legal analisou este relato preliminarmente.
                   Score de Viabilidade: {analysis.get('viability_score')}/100.
                   Análise Técnica: {analysis.get('analysis')}
                   Falta: {', '.join(analysis.get('missing_info', []))}
                   USE ESSAS INFORMAÇÕES PARA DAR UMA RESPOSTA MAIS RICA, MAS NÃO KOPIE E COLE O JSON.]
                   """
            except Exception as e:
                print(f"Silent analysis failed: {e}")

        # 2. Generate Chat Response
        full_context_messages = messages[-10:] # Keep last 10 messages for context window
        
        # Inject analysis context into the system prompt for this turn if available
        current_system_prompt = system_prompt + analysis_context
        
        response_text = await self.llm.chat_completion(
            messages=full_context_messages,
            system_prompt=current_system_prompt
        )
        
        return {
            "role": "assistant",
            "content": response_text
        }
