
import subprocess
import time
import os
import asyncio
import shutil
from typing import Optional
from playwright.async_api import async_playwright
from agents.navigator import NavigatorAgent

def find_chrome_path():
    """Tenta encontrar o executável do Chrome em locais padrões"""
    possible_paths = [
        os.path.join(os.environ.get("ProgramFiles", "C:\\Program Files"), "Google\\Chrome\\Application\\chrome.exe"),
        os.path.join(os.environ.get("ProgramFiles(x86)", "C:\\Program Files (x86)"), "Google\\Chrome\\Application\\chrome.exe"),
        os.path.join(os.environ.get("LOCALAPPDATA", ""), "Google\\Chrome\\Application\\chrome.exe"),
        "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
        "C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe"
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            return path
            
    return None

CHROMIUM_PATH = find_chrome_path()

class BrowserOrchestrator:
    def __init__(self):
        self.browser_process: Optional[subprocess.Popen] = None
        self.cdp_url = "http://127.0.0.1:9222"
        # PERFIL PERSISTENTE: Salva cookies e login para reuso
        self.user_data_dir = os.path.abspath("profiles/user_gov_br")
        self.agent: Optional[NavigatorAgent] = None
        
    def _clean_session(self):
        """Limpa a sessão anterior -- DESATIVADO PARA PERFIL PERSISTENTE"""
        # if os.path.exists(self.user_data_dir):
        #     try:
        #         shutil.rmtree(self.user_data_dir)
        #     except Exception as e:
        #         print(f"[Orchestrator] Aviso ao limpar sessão: {e}")
        pass

    def launch_browser(self):
        """Lança o Chrome Oficial em modo de depuração remota com Perfil Persistente"""
        if self.browser_process:
            print("[Orchestrator] Navegador já está rodando.")
            return

        if not CHROMIUM_PATH:
            print("[Orchestrator] ERRO CRÍTICO: Chrome não encontrado no sistema!")
            raise FileNotFoundError("Não foi possível encontrar o executável do Google Chrome.")

        # self._clean_session() -> Não limpar mais!
        
        # Cria diretório se não existir
        os.makedirs(self.user_data_dir, exist_ok=True)

        cmd = [
            CHROMIUM_PATH,
            "--remote-debugging-port=9222",
            f"--user-data-dir={self.user_data_dir}",
            "--no-first-run",
            "--no-default-browser-check",
            # "--start-maximized", # Opcional: parecer mais humano
            "https://consumidor.gov.br/pages/principal/?1" 
        ]
        
        print(f"[Orchestrator] Lançando Chrome: {' '.join(cmd)}")
        
        # Popen lança o processo independente
        self.browser_process = subprocess.Popen(cmd, shell=False) 
        
        # Espera um pouco para o browser subir
        time.sleep(3)

    async def connect_and_check_login(self) -> dict:
        """
        Tenta conectar via CDP e verifica se o usuário está logado.
        Retorna status: 'not_connected', 'connected_waiting_login', 'logged_in'
        """
        if not self.browser_process:
            return {"status": "browser_not_started"}
            
        try:
            async with async_playwright() as p:
                # Tenta conectar no Chrome que lançamos
                browser = await p.chromium.connect_over_cdp(self.cdp_url)
                context = browser.contexts[0]
                
                if not context.pages:
                    page = await context.new_page()
                else:
                    page = context.pages[0] # Pega a aba ativa

                # Verifica URL e Elementos de Login
                title = await page.title()
                url = page.url
                
                # Lógica simples de detecção de login
                # Se estiver na página "principal" e NÃO tiver botão de "Entrar", assumimos logado
                # Ajustar seletores conforme a realidade do site
                
                print(f"[Orchestrator] Verificando página: {title} - {url}")

                # Exemplo: Se tiver texto "Sair" ou nome do usuário, está logado
                # Se tiver botão "Entrar" ou "Gov.br", não está
                
                is_logged_in = False
                
                # Verifica element "Sair" ou "Minha Área"
                if "consumidor.gov.br/pages/principal" in url:
                    # Se estamos na principal, verificamos se tem o nome do usuário
                    user_badge = await page.query_selector("i.fa-user") # Exemplo visual
                    if user_badge: 
                         is_logged_in = True
                    
                    # Ou verifica se tem botão de "Nova Reclamação" visível
                    new_claim_btn = await page.query_selector("a[href*='reclamacao/registrar']")
                    if new_claim_btn:
                        is_logged_in = True
                
                await browser.close() # Desconecta o CDP (não fecha o browser)
                
                if is_logged_in:
                    return {"status": "logged_in"}
                else:
                    return {"status": "connected_waiting_login"}
                    
        except Exception as e:
            print(f"[Orchestrator] Erro de conexão CDP: {e}")
            return {"status": "connection_error"}

    async def run_automation(self, claim_data: dict, auth_token: Optional[str] = None):
        """
        Conecta e executa a automação (NavigatorAgent)
        """
        print(f"[Orchestrator] Iniciando Automação... Token Presente: {bool(auth_token)}")
        
        # Aqui instanciamos o NavigatorAgent de verdade
        self.agent = NavigatorAgent()
        
        # Conecta (código duplicado do connect, idealmente refatorar para manter conexão viva)
        # Por simplicidade do MVP, reconecta
        async with async_playwright() as p:
             browser = await p.chromium.connect_over_cdp(self.cdp_url)
             context = browser.contexts[0]
             page = context.pages[0]
             
             self.agent.browser = browser
             self.agent.page = page
             
             # Executa o preenchimento
             await self.agent.submit_claim(claim_data, auth_token=auth_token)
             
             print("[Orchestrator] Automação concluída.")
             # Não fecha o browser para o usuário ver/revisar

    def stop_browser(self):
        if self.browser_process:
            self.browser_process.terminate()
            self.browser_process = None

# Instância global (Singleton simples para o MVP)
orchestrator_instance = BrowserOrchestrator()
