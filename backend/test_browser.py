import asyncio
from playwright.async_api import async_playwright

async def main():
    print("Iniciando Playwright...")
    async with async_playwright() as p:
        print("Lançando navegador...")
        browser = await p.chromium.launch(headless=False)
        print("Navegador lançado! Criando página...")
        page = await browser.new_page()
        await page.goto("https://www.google.com")
        print("Acessou Google. Título:", await page.title())
        await asyncio.sleep(5)
        await browser.close()
        print("Fechado.")

if __name__ == "__main__":
    asyncio.run(main())
