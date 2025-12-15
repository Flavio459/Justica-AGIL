import asyncio
import os
from playwright.async_api import async_playwright
from agents.navigator import NavigatorAgent

async def main():
    print("\n===================================================")
    print("   🤖 MODO INTERATIVO - HUMAN IN THE LOOP")
    print("===================================================\n")
    
    # 1. Dados da Reclamação
    claim_data = {
        "company_name": "Baruke Imoveis",
        "facts": "Em 02/12/2025, solicitei abatimento de R$ 603,60 no aluguel referente a manutencao hidraulica corretiva realizada no imovel locado (Rua Jaragua, 33 - Paulista II, Indaiatuba/SP). A manutencao incluiu substituicao do registro do chuveiro DECA e boia da caixa d agua Tigre 3/4. Conforme Lei 8.245/91 Art. 22, e obrigacao do locador manter o imovel. A imobiliaria Baruke Imoveis (CRECI 030631-J) se recusa a efetuar o abatimento devido.",
        "request": "Abatimento de R$ 603,60 no aluguel ou ressarcimento integral conforme Lei 8.245/91."
    }

    print("1. Vou abrir uma janela do navegador para você.")
    print("2. Por favor, faça o LOGIN no Gov.br nela.")
    print("3. Quando estiver logado e na tela inicial, VOLTE AQUI e aperte ENTER.")
    print("\n⏳ Iniciando navegador...")

    async with async_playwright() as p:
        # LaunchPersistentContext: Mantém cookies e sessão em pasta temporária
        # args anti-bot básicos
        browser_context = await p.chromium.launch_persistent_context(
            user_data_dir="tmp/chrome_session",
            # channel="chrome", <--- REVERTIDO: Chrome oficial bloqueou automação
            headless=False,
            viewport={'width': 1280, 'height': 800},
            args=["--disable-blink-features=AutomationControlled", "--no-sandbox"]
        )
        
        page = browser_context.pages[0] if browser_context.pages else await browser_context.new_page()
        
        # Mascarar webdriver (Script Stealth Básico)
        await page.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        await page.goto("https://consumidor.gov.br/pages/principal/")
        
        # --- BLOQUEIO HUMAN IN THE LOOP ---
        input("\n🔴🔴🔴 FAÇA O LOGIN NO NAVEGADOR E DEPOIS APERTE ENTER AQUI PARA CONTINUAR... 🔴🔴🔴")
        print("\n🚀 Ok! Assumindo o controle...")
        
        # Inicializa Agente com a página JÁ ABERTA
        agent = NavigatorAgent()
        agent.page = page
        agent.browser = browser_context # Para evitar erros se ele tentar fechar
        
        # Executa preenchimento
        await agent.submit_claim(claim_data)
        
        input("\n✅ Finalizado! Pressione Enter para fechar o navegador.")
        # NÃO FECHA AUTOMATICAMENTE - Deixa o usuário fechar
        # await browser_context.close()  <-- Comentado
        print("Mantenha o terminal aberto ou feche a janela manualmente.")

if __name__ == "__main__":
    asyncio.run(main())
