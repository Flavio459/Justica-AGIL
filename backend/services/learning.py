"""
Sistema de Memória/Aprendizado Persistente do Procon Ágil

Este módulo armazena conhecimento adquirido durante interações:
- Seletores CSS que funcionaram em cada site
- Padrões de casos bem-sucedidos
- Erros e como foram resolvidos
- Histórico de interações para análise
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional, Any

class LearningService:
    """
    Serviço de Aprendizado Persistente.
    Toda interação contribui para o conhecimento coletivo.
    """
    
    def __init__(self, storage_path: str = "data/knowledge.json"):
        self.storage_path = storage_path
        self.knowledge = self._load_knowledge()
    
    def _load_knowledge(self) -> Dict:
        """Carrega conhecimento existente ou inicializa novo."""
        os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
        
        if os.path.exists(self.storage_path):
            try:
                with open(self.storage_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass
        
        # Estrutura inicial do conhecimento
        return {
            "version": "1.0",
            "created_at": datetime.now().isoformat(),
            "selectors": {
                "consumidor.gov.br": {
                    "login_button": [],
                    "new_claim_button": [],
                    "company_search": [],
                    "facts_textarea": [],
                    "request_textarea": [],
                    "submit_button": []
                }
            },
            "patterns": {
                "successful_claims": [],
                "legal_references": [],
                "company_mappings": {}
            },
            "errors": {
                "captcha_solutions": [],
                "selector_failures": [],
                "login_issues": []
            },
            "statistics": {
                "total_interactions": 0,
                "successful_submissions": 0,
                "failed_submissions": 0
            },
            "interaction_history": []
        }
    
    def _save_knowledge(self):
        """Persiste conhecimento para arquivo."""
        with open(self.storage_path, 'w', encoding='utf-8') as f:
            json.dump(self.knowledge, f, ensure_ascii=False, indent=2)
    
    # =================== SELETORES ===================
    
    def learn_selector(self, site: str, element_type: str, selector: str, success: bool):
        """
        Aprende qual seletor funcionou (ou não) para um elemento.
        
        Args:
            site: domínio do site (ex: "consumidor.gov.br")
            element_type: tipo de elemento (ex: "login_button")
            selector: seletor CSS que foi tentado
            success: se funcionou ou não
        """
        if site not in self.knowledge["selectors"]:
            self.knowledge["selectors"][site] = {}
        
        if element_type not in self.knowledge["selectors"][site]:
            self.knowledge["selectors"][site][element_type] = []
        
        selectors = self.knowledge["selectors"][site][element_type]
        
        # Verificar se já existe
        existing = next((s for s in selectors if s["selector"] == selector), None)
        
        if existing:
            if success:
                existing["success_count"] = existing.get("success_count", 0) + 1
            else:
                existing["fail_count"] = existing.get("fail_count", 0) + 1
            existing["last_used"] = datetime.now().isoformat()
        else:
            selectors.append({
                "selector": selector,
                "success_count": 1 if success else 0,
                "fail_count": 0 if success else 1,
                "first_seen": datetime.now().isoformat(),
                "last_used": datetime.now().isoformat()
            })
        
        # Ordenar por taxa de sucesso
        selectors.sort(key=lambda x: x["success_count"] / max(x["success_count"] + x["fail_count"], 1), reverse=True)
        
        self._save_knowledge()
    
    def get_best_selectors(self, site: str, element_type: str, limit: int = 5) -> List[str]:
        """
        Retorna os melhores seletores conhecidos para um elemento.
        Ordenados por taxa de sucesso.
        """
        try:
            selectors = self.knowledge["selectors"][site][element_type]
            return [s["selector"] for s in selectors[:limit]]
        except KeyError:
            return []
    
    # =================== PADRÕES ===================
    
    def learn_successful_claim(self, claim_data: Dict, result: Dict):
        """Aprende de uma reclamação bem-sucedida."""
        self.knowledge["patterns"]["successful_claims"].append({
            "timestamp": datetime.now().isoformat(),
            "company": claim_data.get("company_name"),
            "claim_type": self._detect_claim_type(claim_data.get("facts", "")),
            "facts_length": len(claim_data.get("facts", "")),
            "had_request": bool(claim_data.get("request")),
            "protocol": result.get("protocol")
        })
        
        self.knowledge["statistics"]["successful_submissions"] += 1
        self._save_knowledge()
    
    def learn_company_mapping(self, user_input: str, official_name: str):
        """Aprende mapeamento de nome informal para oficial."""
        self.knowledge["patterns"]["company_mappings"][user_input.lower()] = official_name
        self._save_knowledge()
    
    def get_company_suggestion(self, user_input: str) -> Optional[str]:
        """Sugere nome oficial baseado em aprendizado anterior."""
        return self.knowledge["patterns"]["company_mappings"].get(user_input.lower())
    
    # =================== ERROS ===================
    
    def learn_error(self, error_type: str, context: Dict, solution: Optional[str] = None):
        """Aprende de um erro para evitar no futuro."""
        error_key = f"{error_type}_solutions" if error_type in ["captcha", "selector", "login"] else "general_errors"
        
        if error_key not in self.knowledge["errors"]:
            self.knowledge["errors"][error_key] = []
        
        self.knowledge["errors"][error_key].append({
            "timestamp": datetime.now().isoformat(),
            "context": context,
            "solution": solution
        })
        
        self.knowledge["statistics"]["failed_submissions"] += 1
        self._save_knowledge()
    
    # =================== INTERAÇÕES ===================
    
    def log_interaction(self, interaction_type: str, data: Dict, outcome: str):
        """Registra qualquer interação para análise futura."""
        self.knowledge["interaction_history"].append({
            "timestamp": datetime.now().isoformat(),
            "type": interaction_type,
            "data": data,
            "outcome": outcome
        })
        
        # Manter apenas últimas 1000 interações
        if len(self.knowledge["interaction_history"]) > 1000:
            self.knowledge["interaction_history"] = self.knowledge["interaction_history"][-1000:]
        
        self.knowledge["statistics"]["total_interactions"] += 1
        self._save_knowledge()
    
    # =================== ANÁLISE ===================
    
    def _detect_claim_type(self, facts: str) -> str:
        """Detecta tipo de reclamação baseado no texto."""
        facts_lower = facts.lower()
        
        if any(word in facts_lower for word in ["infiltração", "vazamento", "hidráulica", "encanamento"]):
            return "manutencao_hidraulica"
        elif any(word in facts_lower for word in ["caução", "depósito", "devolução"]):
            return "caucao"
        elif any(word in facts_lower for word in ["multa", "cobrança", "taxa"]):
            return "cobranca_indevida"
        elif any(word in facts_lower for word in ["contrato", "rescisão"]):
            return "contrato"
        else:
            return "outros"
    
    def get_success_rate(self) -> float:
        """Retorna taxa de sucesso geral."""
        stats = self.knowledge["statistics"]
        total = stats["successful_submissions"] + stats["failed_submissions"]
        if total == 0:
            return 0.0
        return stats["successful_submissions"] / total
    
    def get_insights(self) -> Dict:
        """Retorna insights sobre o conhecimento acumulado."""
        return {
            "total_interactions": self.knowledge["statistics"]["total_interactions"],
            "success_rate": self.get_success_rate(),
            "known_companies": len(self.knowledge["patterns"]["company_mappings"]),
            "successful_claims": len(self.knowledge["patterns"]["successful_claims"]),
            "known_selectors": sum(
                len(elements) 
                for site in self.knowledge["selectors"].values() 
                for elements in site.values()
            )
        }


# Instância global do serviço
learning_service = LearningService()
