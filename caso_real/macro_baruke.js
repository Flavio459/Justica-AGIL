// --- MACRO BARUKE IMOVEIS ---
// 1. Abra o site: https://consumidor.gov.br/pages/principal/?1
// 2. Faça Login
// 3. Clique em "Nova Reclamação"
// 4. Aperte F12 -> Console -> Cole este código -> Enter

(async function () {
    console.log("🚀 Iniciando Macro Baruke...");

    // DADOS DO CASO REAL
    const data = {
        company: "Baruke Imoveis",
        facts: `Em 02/12/2025, solicitei abatimento de R$ 603,60 no aluguel referente a manutenção hidráulica corretiva realizada no imóvel locado (Rua Jaraguá, 33 - Paulista II, Indaiatuba/SP).

A manutenção incluiu:
1. Substituição do registro do chuveiro (marca DECA)
2. Substituição da boia da caixa d'água (marca Tigre 3/4)

Tenho todas as evidências (Nota Fiscal, Recibo e Fotos).
Conforme Lei 8.245/1991 (Lei do Inquilinato), Art. 22 e 23, é obrigação do locador manter a forma e destino do imóvel, respondendo pelos vícios anteriores à locação.

A Imobiliária Baruke Imóveis (CRECI 030631-J) foi notificada via WhatsApp com aprovação prévia, mas agora recusa o ressarcimento.`,
        request: "Solicito o abatimento imediato de R$ 603,60 no próximo boleto de aluguel ou o ressarcimento integral do valor pago pela manutenção corretiva, conforme garante a Lei do Inquilinato."
    };

    // Função de espera
    const sleep = ms => new Promise(r => setTimeout(r, ms));

    // 1. Busca Empresa
    console.log("🏢 Buscando empresa...");
    const busca = document.querySelector('input[placeholder*="empresa"], input[name="empresa"]');
    if (busca) {
        busca.click();
        busca.value = data.company;
        busca.dispatchEvent(new Event('input', { bubbles: true }));
        busca.dispatchEvent(new Event('keydown', { bubbles: true }));
        busca.dispatchEvent(new Event('keyup', { bubbles: true }));
    } else {
        alert("❌ Campo de busca de empresa não encontrado. Você está na tela 'Nova Reclamação'?");
        return;
    }

    // Espera usuário selecionar a empresa (difícil automatizar o clique no dropdown exato)
    alert("⚠️ POR FAVOR:\n\n1. Selecione a 'Baruke Imóveis' na lista que apareceu.\n2. Espere a página carregar.\n3. Rode este código de novo (Seta pra cima + Enter) para preencher o texto.");

    // Tenta preencher texto (caso já tenha selecionado)
    await sleep(2000);

    const relato = document.querySelector('textarea[name*="relato"], textarea[name*="texto"]');
    if (relato) {
        console.log("📝 Preenchendo relato...");
        relato.value = data.facts;
        relato.dispatchEvent(new Event('input', { bubbles: true }));
        relato.dispatchEvent(new Event('change', { bubbles: true }));

        // Pedido
        const pedido = document.querySelector('textarea[name*="pedido"]');
        if (pedido) {
            pedido.value = data.request;
            pedido.dispatchEvent(new Event('input', { bubbles: true }));
        }

        alert("✅ TEXTOS PREENCHIDOS!\n\nAgora anexe os documentos e envie.");
    }

})();
