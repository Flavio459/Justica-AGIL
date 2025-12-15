from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

class MetaScriptRequest(BaseModel):
    claim_data: dict

@router.post("/automation/generate_script")
async def generate_helper_script(request: MetaScriptRequest):
    data = request.claim_data
    
    # Pre-escape strings to avoid backslash in f-string expressions (Python 3.8 limitation)
    company_escaped = data.get('company_name', '').replace('"', '\\"')
    facts_escaped = data.get('facts', '').replace('`', '\\`')
    request_escaped = data.get('request', '').replace('`', '\\`')
    
    # Gerar script JS que preenche o formulário
    js_code = f"""
    // --- MACRO DE PREENCHIMENTO AUTOMÁTICO - PROCON ÁGIL ---
    (async function() {{
        console.log("🚀 Iniciando Macro Procon Ágil...");
        
        const data = {{
            company: "{company_escaped}",
            facts: `{facts_escaped}`,
            request: `{request_escaped}`
        }};

        // Função auxiliar para esperar
        const sleep = (ms) => new Promise(r => setTimeout(r, ms));
        
        // 1. Tentar preencher Empresa
        const empresaInput = document.querySelector('input[placeholder*="empresa"], input[name*="empresa"], #empresaBusca');
        if (empresaInput) {{
            console.log("🏢 Preenchendo empresa...");
            empresaInput.click();
            empresaInput.value = data.company;
            empresaInput.dispatchEvent(new Event('input', {{ bubbles: true }}));
            empresaInput.dispatchEvent(new Event('change', {{ bubbles: true }}));
            
            // Tentar disparar busca
            await sleep(1000);
            const items = document.querySelectorAll('.ui-menu-item, li[role="option"]');
            if (items.length > 0) {{
                console.log("✅ Clicando na primeira sugestão...");
                items[0].click();
            }}
        }}

        await sleep(1000);

        // 2. Preencher Relato
        const relatoInput = document.querySelector('textarea[name*="relato"], textarea[name*="descricao"], #relato');
        if (relatoInput) {{
            console.log("📝 Preenchendo relato...");
            relatoInput.value = data.facts.substring(0, 3000); // Limite do site
            relatoInput.dispatchEvent(new Event('input', {{ bubbles: true }}));
        }} else {{
            console.warn("⚠️ Campo de relato não encontrado!");
        }}

        // 3. Preencher Pedido
        const pedidoInput = document.querySelector('textarea[name*="pedido"], textarea[name*="solicitacao"], #pedido');
        if (pedidoInput) {{
            console.log("📋 Preenchendo pedido...");
            pedidoInput.value = data.request;
            pedidoInput.dispatchEvent(new Event('input', {{ bubbles: true }}));
        }}
        
        alert("✅ Formulário preenchido pelo Procon Ágil!\\n\\nRevise os dados e anexe os documentos manualmente.");
        console.log("✅ Concluído!");
    }})();
    """
    
    return {"javascript_code": js_code}
