import asyncio
import os
import sys

# Add backend to path
sys.path.append(os.getcwd())

from agents.navigator import NavigatorAgent

async def main():
    print("--- CONECTANDO AO NAVEGADOR ---")
    
    # Dados reais do caso Baruke
    claim_data = {
        "company_name": "Baruke Imoveis",
        "facts": "Em 02/12/2025, solicitei abatimento de R$ 603,60 no aluguel referente a manutencao hidraulica corretiva realizada no imovel locado (Rua Jaragua, 33 - Paulista II, Indaiatuba/SP). A manutencao incluiu substituicao do registro do chuveiro DECA e boia da caixa d agua Tigre 3/4. Conforme Lei 8.245/91 Art. 22, e obrigacao do locador manter o imovel. A imobiliaria Baruke Imoveis (CRECI 030631-J) se recusa a efetuar o abatimento devido.",
        "request": "Abatimento de R$ 603,60 no aluguel ou ressarcimento integral conforme Lei 8.245/91."
    }
    
    # URL de conexão CDP padrão (IPv4 explícito)
    cdp_url = "http://127.0.0.1:9222"
    
    from playwright.async_api import async_playwright
    
    async with async_playwright() as p:
        try:
            print(f"Tentando conectar em {cdp_url}...")
            browser = await p.chromium.connect_over_cdp(cdp_url)
            context = browser.contexts[0]
            if not context.pages:
                page = await context.new_page()
            else:
                # Usar a aba ativa (provavelmente onde o usuário logou)
                page = context.pages[0] 
                
            print("✅ Conectado com sucesso!")
            
            # Instanciar agente e INJETAR a página já conectada
            agent = NavigatorAgent()
            agent.browser = browser
            agent.page = page
            
            # Executar lógica de preenchimento (sem abrir novo browser)
            # Precisamos adaptar submit_claim para aceitar page externa ou verificar se self.page já existe
            
            await agent.submit_claim(claim_data, headless=False, dry_run=True)
            
        except Exception as e:
            print(f"❌ Erro ao conectar: {e}")
            print("Certifique-se de ter rodado o iniciar_automacao.bat!")

if __name__ == "__main__":
    if sys.platform == 'win32':
        # FIX: Usar ProactorEventLoopPolicy para Windows + Subprocess
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    asyncio.run(main())
