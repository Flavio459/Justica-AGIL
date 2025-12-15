"""
Navigator Agent - Chama Playwright via SUBPROCESS
Para contornar conflitos de event loop no Uvicorn/Windows Python 3.8
"""
import asyncio
import subprocess
import json
import os
import tempfile
from typing import Optional

class NavigatorAgent:
    """
    Agente Navegador REAL para Consumidor.gov.br
    Executa Playwright em processo separado para evitar conflitos de event loop.
    """
    
    def __init__(self):
        self.runner_script = os.path.join(os.path.dirname(__file__), "playwright_runner.py")
    
    async def submit_claim(self, claim_data: dict, auth_token: Optional[str] = None, headless: bool = False, dry_run: bool = False) -> dict:
        """
        Executa automação via subprocess para contornar conflitos de event loop.
        """
        steps_log = []
        
        def log_step(step: str):
            print(f"[Navigator] {step}")
            steps_log.append(step)
        
        try:
            log_step("🚀 Iniciando automação via subprocess...")
            
            # Criar arquivo JSON temporário com os dados
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
                json.dump({
                    "claim_data": claim_data,
                    "auth_token": auth_token,
                    "dry_run": dry_run
                }, f, ensure_ascii=False)
                temp_json_path = f.name
            
            log_step(f"📄 Dados salvos em: {temp_json_path}")
            
            # Executar script Playwright como subprocess
            python_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".venv", "Scripts", "python.exe")
            
            # Fallback para python do sistema se venv não existir
            if not os.path.exists(python_path):
                python_path = "python"
            
            log_step(f"🐍 Executando: {python_path} {self.runner_script}")
            
            # Rodar em thread para não bloquear
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None,
                self._run_subprocess,
                python_path,
                self.runner_script,
                temp_json_path
            )
            
            # Limpar arquivo temporário
            try:
                os.unlink(temp_json_path)
            except:
                pass
            
            return result
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            return {
                "status": "error",
                "error": str(e),
                "logs": steps_log
            }
    
    def _run_subprocess(self, python_path: str, script_path: str, json_path: str) -> dict:
        """
        Executa o subprocess de forma síncrona (será chamado via run_in_executor).
        """
        try:
            result = subprocess.run(
                [python_path, script_path, json_path],
                capture_output=True,
                text=True,
                timeout=300,  # 5 minutos de timeout
                cwd=os.path.dirname(script_path)
            )
            
            print(f"[Navigator] stdout: {result.stdout[-500:]}")  # Últimos 500 chars
            
            if result.stderr:
                print(f"[Navigator] stderr: {result.stderr[-500:]}")
            
            # Extrair JSON do output
            if "---RESULT_JSON---" in result.stdout:
                json_str = result.stdout.split("---RESULT_JSON---")[1].strip()
                return json.loads(json_str)
            else:
                return {
                    "status": "error",
                    "error": "Script não retornou resultado JSON",
                    "stdout": result.stdout[-1000:],
                    "stderr": result.stderr[-1000:]
                }
                
        except subprocess.TimeoutExpired:
            return {
                "status": "timeout",
                "error": "Automação excedeu timeout de 5 minutos"
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
