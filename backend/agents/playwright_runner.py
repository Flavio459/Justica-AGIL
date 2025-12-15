#!/usr/bin/env python3
"""
Playwright Automation Script - Executado como SUBPROCESS
IMPORTANTE: Modo DRY_RUN = preenche tudo mas NAO envia
"""
import sys
import json
import os
import re
from playwright.sync_api import sync_playwright

def run_automation(claim_data: dict, auth_token: str = None, dry_run: bool = True) -> dict:
    steps_log = []
    
    def log_step(step: str):
        print(f"[Navigator] {step}", flush=True)
        steps_log.append(step)
    
    try:
        with sync_playwright() as p:
            log_step("[START] Conectando ao Chrome porta 9222...")
            
            try:
                browser = p.chromium.connect_over_cdp("http://localhost:9222")
                context = browser.contexts[0]
                page = context.pages[0] if context.pages else context.new_page()
                log_step("[OK] Conectado!")
            except Exception as e:
                return {"status": "error", "error": f"Chrome nao conectado: {e}", "logs": steps_log}
            
            # Navegar para pagina de busca
            log_step("[NAV] Indo para consumidor.gov.br...")
            page.goto("https://consumidor.gov.br/pages/principal/")
            page.wait_for_load_state("networkidle")
            page.wait_for_timeout(2000)
            
            # Verificar login
            # Verificar login
            if auth_token:
                log_step(f"[AUTH] Injetando Token OAuth: {auth_token[:10]}...")
                # OAUTH2 INJECTION STRATEGY:
                # 1. Definir cookie/header (Mock)
                # context.add_cookies([{'name': 'govbr_token', 'value': auth_token, 'url': 'https://consumidor.gov.br'}])
                log_step("[AUTH] Token injetado (Simulação)")

            if "Sair" in page.content() or "Minha" in page.content():
                log_step("[OK] Logado!")
            else:
                return {"status": "login_required", "message": "Faca login primeiro", "logs": steps_log}
            
            # PASSO 1: Buscar empresa
            company = claim_data.get("company_name", "Vivo")
            log_step(f"[BUSCA] Digitando: {company}")
            
            try:
                campo = page.locator('#autocomplete_empresa, input[placeholder*="empresa"]').first
                campo.click()
                campo.fill(company)
                log_step("[OK] Empresa digitada")
                page.wait_for_timeout(3000)  # Esperar mais
                
                # Tentar selecionar do autocomplete
                try:
                    opcao = page.locator('.ui-menu-item a, .ui-autocomplete li, .typeahead-item').first
                    opcao.wait_for(timeout=5000)
                    opcao.click()
                    log_step("[OK] Empresa selecionada do autocomplete")
                    page.wait_for_timeout(2000)
                except:
                    log_step("[!] Autocomplete lento ou empresa nao encontrada - tentando continuar com ENTER")
                    # Tentar pressionar Enter para aceitar o que foi digitado ou fechar o autocomplete
                    campo.press("Enter")
                    page.wait_for_timeout(2000)
            except Exception as e:
                log_step(f"[!] Campo busca: {e}")
            
            page.wait_for_load_state("networkidle")
            
            # PASSO 2: Clicar em Registrar Reclamacao
            log_step("[NAV] Procurando botao de reclamacao...")
            try:
                btn = page.locator('a:has-text("Registrar"), button:has-text("Registrar"), a:has-text("reclamacao")').first
                btn.click()
                log_step("[OK] Clicou em Registrar")
                page.wait_for_load_state("networkidle")
                page.wait_for_timeout(3000)
            except:
                log_step("[!] Botao nao encontrado - talvez ja esteja na pagina do formulario")
            
            # PASSO 3: Preencher campos do formulario
            facts = claim_data.get("facts", "")[:3000]
            request = claim_data.get("request", "")
            
            log_step(f"[FORM] Preenchendo campos...")
            
            # Tentar preencher todos os textareas visiveis
            textareas = page.locator('textarea:visible').all()
            log_step(f"[INFO] Encontrados {len(textareas)} textareas")
            
            for i, ta in enumerate(textareas):
                try:
                    placeholder = ta.get_attribute('placeholder') or ta.get_attribute('name') or f"textarea_{i}"
                    if i == 0:
                        ta.fill(facts)
                        log_step(f"[OK] Preencheu textarea[{i}] com fatos")
                    elif i == 1:
                        ta.fill(request)
                        log_step(f"[OK] Preencheu textarea[{i}] com pedido")
                except Exception as e:
                    log_step(f"[!] Erro textarea[{i}]: {e}")
            
            # Preencher selects se houver
            try:
                selects = page.locator('select:visible').all()
                for s in selects:
                    options = s.locator('option').all()
                    if len(options) > 1:
                        s.select_option(index=1)
                        log_step("[OK] Selecionou opcao em dropdown")
            except:
                pass
            
            # Screenshot final
            os.makedirs("temp_uploads", exist_ok=True)
            screenshot_path = "temp_uploads/claim_preview.png"
            page.screenshot(path=screenshot_path, full_page=True)
            log_step(f"[SCREENSHOT] Salvo: {screenshot_path}")
            
            # DRY RUN - NAO ENVIA
            log_step("[FINAL] MODO TESTE - NAO clicou em enviar")
            log_step("[INFO] Formulario preenchido. Revise no Chrome.")
            
            return {
                "status": "dry_run_complete",
                "message": "Preenchido com sucesso. Revise no Chrome antes de enviar manualmente.",
                "screenshot": screenshot_path,
                "logs": steps_log
            }
    
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"status": "error", "error": str(e), "logs": steps_log}


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(json.dumps({"status": "error", "error": "Usage: python playwright_runner.py <json>"}))
        sys.exit(1)
    
    with open(sys.argv[1], 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    result = run_automation(
        claim_data=data.get("claim_data", {}),
        auth_token=data.get("auth_token"),
        dry_run=data.get("dry_run", True)
    )
    
    print("---RESULT_JSON---")
    print(json.dumps(result, ensure_ascii=False))
