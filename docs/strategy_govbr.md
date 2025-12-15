# Estratégia de Autenticação e Navegação GOV.BR
## Justiça Ágil – Integração Segura para Procon/Consumidor.gov.br

**Data**: Dezembro 2025  
**Contexto**: Justiça Ágil precisa integrar navegação automática em portais gov.br que exigem login  
**Público**: IA Antigravidaty + Product Owner  

---

## 1. DESAFIO CENTRAL

### Barreiras de Segurança do GOV.BR
1. **Certificado Digital (eIDAS)** - Gov.br suporta múltiplos autenticadores
2. **MFA Obrigatória** - SMS, Email, Authenticator app
3. **Rate Limiting** - Proteção contra força bruta
4. **Session Timeout** - 30-60 min de inatividade
5. **CAPTCHA/Bot Detection** - Desafios contra automação
6. **Mudanças de Política** - Sistema evolui constantemente
7. **Endpoint Instável** - Manutenções sem aviso

### Cenário Ideal para Justiça Ágil
```
Locatário (classe B/C) → 
  1. Faz login manualmente gov.br (com MFA) → 
  2. Retorna à Justiça Ágil (sessão + token) → 
  3. Agente Antigravidaty assume → 
  4. Navega formulários Procon/Consumidor.gov.br → 
  5. Preenche campos + gera texto jurídico → 
  6. Usuário revisa + aprova → 
  7. Sistema envia protocolo
```

---

## 2. OPÇÕES DE INTEGRAÇÃO (Análise Comparativa)

| Opção | Abordagem | Viabilidade | Esforço | Segurança | Manutenção | Recomendação |
|-------|-----------|-------------|--------|-----------|-----------|--------------|
| **A) API OAuth2 Gov.br** | Usar OpenID Connect oficial | ⭐⭐⭐⭐⭐ Alto | Baixo (4-8 sem) | Máxima | Baixa | ✅ **PRIMEIRA OPÇÃO** |
| **B) WebDriver + Session** | Selenium/Playwright + token reutilização | ⭐⭐⭐ Médio | Médio (2-3 sem) | Alta | Média-Alta | ⚠️ Backup |
| **C) API Consumidor.gov.br** | Integração direta (se houver) | ⭐⭐ Baixo | Médio | Máxima | Média | ℹ️ Investigar |
| **D) RPA Puro (UiPath)** | Automação de UI sem API | ⭐ Muito baixo | Alto (6-12 sem) | Baixa | Muito Alta | ❌ Não recomendado |

---

## 3. ARQUITETURA RECOMENDADA: OAuth2 + Session Management

### 3.1 Fluxo Autenticação (High-Level)

```
┌─────────────────────────────────────────────────────────────────┐
│ FASE 1: LOGIN MANUAL (Usuário)                                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  1. Usuário clica "Login GOV.BR" em Justiça Ágil               │
│  2. Redireciona para gov.br/oauth/authorize                     │
│     ├─ client_id: [APP_ID_JUSTICA_AGIL]                        │
│     ├─ redirect_uri: https://justicaagil.com/auth/callback     │
│     ├─ scope: openid,profile,email,cpf                         │
│     └─ state: [CSRF_TOKEN_RANDOM]                              │
│  3. Usuário faz login + MFA no GOV.BR                          │
│  4. GOV.BR redireciona para callback com CODE                   │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ FASE 2: EXCHANGE TOKEN + CRIAR SESSÃO (Backend Justiça Ágil)   │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  1. Backend recebe CODE                                          │
│  2. POST /auth/token                                             │
│     ├─ code: [CODE]                                             │
│     ├─ client_id: [APP_ID]                                      │
│     ├─ client_secret: [SECRET] (protegido!)                     │
│     └─ redirect_uri: [CALLBACK_URL]                             │
│  3. Recebe:                                                       │
│     ├─ access_token (JWT, 1h)                                   │
│     ├─ refresh_token (90 dias)                                  │
│     ├─ id_token (contém CPF, nome, email)                       │
│  4. Valida e armazena em banco:                                 │
│     ├─ user_id, cpf, nome                                       │
│     ├─ access_token (criptografado)                             │
│     ├─ refresh_token (criptografado)                            │
│     └─ expires_at (TTL)                                         │
│  5. Cria sessão Justiça Ágil (cookie seguro)                   │
│  6. Retorna para frontend                                        │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ FASE 3: AGENTE ASSUME (Antigravidaty)                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  1. Usuário inicia fluxo "Abrir Reclamação Procon"             │
│  2. Antigravidaty (orquestrador) recebe:                        │
│     ├─ user_id (de sessão)                                      │
│     ├─ access_token (recupera do banco)                         │
│     └─ refresh_token (para renovar se expirar)                  │
│  3. Abre WebDriver (Playwright/Selenium)                        │
│  4. Navega até /procon e injeta headers:                        │
│     └─ Authorization: Bearer [access_token]                     │
│  5. Preenche formulários (parsing + automação)                  │
│  6. Gera texto jurídico (LLM legal)                            │
│  7. Aguarda aprovação do usuário                                │
│  8. Submete formulário com token válido                         │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

### 3.2 Implementação Técnica

#### Backend (Node.js/Python)

```javascript
// Pseudocódigo - Autenticação GOV.BR

// 1. STEP 1: Iniciar login
app.get('/api/auth/gov-br', (req, res) => {
  const state = crypto.randomBytes(32).toString('hex');
  req.session.oauth_state = state;
  
  const authUrl = new URL('https://acesso.gov.br/oauth/authorize');
  authUrl.searchParams.append('client_id', process.env.GOV_BR_CLIENT_ID);
  authUrl.searchParams.append('redirect_uri', 'https://justicaagil.com/auth/callback');
  authUrl.searchParams.append('response_type', 'code');
  authUrl.searchParams.append('scope', 'openid profile email');
  authUrl.searchParams.append('state', state);
  
  res.redirect(authUrl.toString());
});

// 2. STEP 2: Callback + Token Exchange
app.get('/auth/callback', async (req, res) => {
  const { code, state } = req.query;
  
  // Validar CSRF
  if (state !== req.session.oauth_state) {
    return res.status(401).json({ error: 'CSRF token inválido' });
  }
  
  try {
    // Exchange code por token
    const tokenResponse = await fetch('https://acesso.gov.br/oauth/token', {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: new URLSearchParams({
        grant_type: 'authorization_code',
        code,
        client_id: process.env.GOV_BR_CLIENT_ID,
        client_secret: process.env.GOV_BR_CLIENT_SECRET,
        redirect_uri: 'https://justicaagil.com/auth/callback'
      })
    });
    
    const tokens = await tokenResponse.json();
    
    // Decodificar JWT (validar assinatura!)
    const decoded = jwt.verify(tokens.id_token, process.env.GOV_BR_PUBLIC_KEY);
    const { cpf, name, email } = decoded;
    
    // Salvar tokens criptografados
    const user = await User.findOrCreate({
      cpf,
      email,
      name
    });
    
    user.access_token = encrypt(tokens.access_token);
    user.refresh_token = encrypt(tokens.refresh_token);
    user.token_expires_at = Date.now() + tokens.expires_in * 1000;
    await user.save();
    
    // Criar sessão segura
    req.session.userId = user.id;
    req.session.cpf = cpf;
    
    res.redirect('/dashboard?auth=success');
    
  } catch (error) {
    console.error('OAuth erro:', error);
    res.redirect('/login?error=auth_failed');
  }
});

// 3. STEP 3: Agente acessa token
app.get('/api/agent/token', authenticateSession, (req, res) => {
  const user = await User.findById(req.session.userId);
  
  // Renovar token se expirado
  if (user.token_expires_at < Date.now()) {
    const newTokens = await refreshAccessToken(user.refresh_token);
    user.access_token = encrypt(newTokens.access_token);
    user.token_expires_at = Date.now() + newTokens.expires_in * 1000;
    await user.save();
  }
  
  res.json({
    access_token: user.access_token, // Já criptografado
    cpf: user.cpf
  });
});
```

#### Frontend (React/Vue)

```javascript
// Justiça Ágil - Iniciar login

function AuthButton() {
  const handleLogin = () => {
    window.location.href = 'https://justicaagil.com/api/auth/gov-br';
  };
  
  return (
    <button onClick={handleLogin} className="btn-gov-br">
      🔐 Entrar com GOV.BR
    </button>
  );
}

// Post-login: Agente está pronto
function DashboardAgent() {
  const [agentStatus, setAgentStatus] = useState('idle');
  
  const startProconFlow = async () => {
    setAgentStatus('loading');
    
    try {
      // Obter token do backend
      const { access_token } = await fetch('/api/agent/token').then(r => r.json());
      
      // Notificar Antigravidaty
      const response = await fetch('/api/agent/execute', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          action: 'open_procon_form',
          access_token, // Agente usará isso
          user_cpf: session.cpf,
          complaint_type: 'manutencao_imobiliaria'
        })
      });
      
      const result = await response.json();
      setAgentStatus('review_pending'); // Aguarda aprovação
      
    } catch (error) {
      console.error('Erro ao iniciar agente:', error);
      setAgentStatus('error');
    }
  };
  
  return (
    <div>
      <h2>Abrir Reclamação Procon</h2>
      <button onClick={startProconFlow}>Iniciar Agente 🤖</button>
      <p>Status: {agentStatus}</p>
    </div>
  );
}
```

#### Agente (Antigravidaty)

```python
# Pseudocódigo Python - Antigravidaty integrado

from playwright.async_api import async_playwright
import httpx

class ProconAutomationAgent:
    def __init__(self, access_token: str, cpf: str):
        self.access_token = access_token
        self.cpf = cpf
        self.browser = None
    
    async def navigate_procon_form(self, complaint_data: dict):
        """
        Navega formulário Procon com token GOV.BR injetado
        """
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context()
            
            # Injetar token no localStorage / headers
            page = await context.new_page()
            
            # Interceptar requisições para adicionar Authorization
            async def handle_route(route):
                request = route.request
                headers = request.headers.copy()
                headers['Authorization'] = f'Bearer {self.access_token}'
                await route.continue_(headers=headers)
            
            await page.route('**/*', handle_route)
            
            # Navegar até Procon
            await page.goto('https://www.consumidor.gov.br/pages/conteudo/')
            
            # Aguardar login (já está feito, mas pode haver re-auth)
            try:
                await page.wait_for_url('**/dashboard/**', timeout=5000)
            except:
                # Se houver re-auth, usuário intervém
                await self.notify_user_intervention('Re-autenticação necessária')
                return
            
            # Preencher formulários
            await self.fill_complaint_form(page, complaint_data)
            
            # Gerar texto jurídico
            legal_text = await self.generate_legal_text(complaint_data)
            
            # Renderizar para aprovação do usuário
            await self.send_for_review(page, legal_text)
            
            await browser.close()
    
    async def fill_complaint_form(self, page, data):
        """Preenche campos do formulário"""
        fields_map = {
            'tipo_reclamacao': 'select[name="complaint_type"]',
            'descricao': 'textarea[name="description"]',
            'valor_afetado': 'input[name="amount"]',
            'cpf': 'input[name="cpf"]'
        }
        
        for field, selector in fields_map.items():
            if field in data:
                await page.fill(selector, str(data[field]))
    
    async def generate_legal_text(self, data):
        """Usa LLM para gerar texto jurídico eficaz"""
        prompt = f"""
        Gere uma reclamação ao Procon com base em:
        - Tipo: {data['complaint_type']}
        - Fatos: {data['facts']}
        - Pedidos: {data['requests']}
        - Fundamento legal: CDC (Lei 8.078/90), Lei 8.245/91
        
        Formato esperado:
        ## FATOS
        [narrativa dos fatos relevantes]
        
        ## PEDIDOS
        [o que pede ao Procon]
        
        ## FUNDAMENTAÇÃO LEGAL
        [artigos aplicáveis]
        """
        
        response = await llm.generate(prompt)
        return response
    
    async def send_for_review(self, page, legal_text):
        """Notifica usuário para revisar antes de enviar"""
        await httpx.post(f'https://justicaagil.com/api/review', json={
            'legal_text': legal_text,
            'status': 'awaiting_user_approval',
            'cpf': self.cpf
        })

# Função de orquestração
async def execute_procon_complaint(access_token, cpf, complaint_data):
    agent = ProconAutomationAgent(access_token, cpf)
    await agent.navigate_procon_form(complaint_data)
```

---

## 4. TRATAMENTO DE DESAFIOS DE SEGURANÇA

### 4.1 Expiração de Token

**Problema**: Token expira enquanto agente trabalha

**Solução**:
```
1. Verificar TTL antes de usar
2. Se expirado, usar refresh_token para renovar
3. Salvar novo token criptografado
4. Redirecionar agente para continuar
```

**Código**:
```python
async def ensure_valid_token(user_id: str):
    user = await User.get(user_id)
    if user.token_expires_at < datetime.now():
        new_tokens = await refresh_access_token(user.refresh_token)
        user.access_token = encrypt(new_tokens['access_token'])
        await user.save()
    return decrypt(user.access_token)
```

### 4.2 MFA - Bloqueio de Navegação

**Problema**: Gov.br pode pedir MFA novamente

**Solução**:
```
1. Agente detecta desafio MFA
2. Pausa automação
3. Notifica usuário para completar MFA
4. Retoma após confirmação
```

**Implementação**:
```python
async def detect_mfa_challenge(page):
    mfa_selectors = [
        '[data-testid="mfa-challenge"]',
        '.otp-input',
        '[id*="sms-verify"]'
    ]
    
    for selector in mfa_selectors:
        if await page.query_selector(selector):
            return True
    return False

# No fluxo principal
if await detect_mfa_challenge(page):
    await notify_user(user_id, {
        'type': 'mfa_required',
        'message': 'Insira código MFA para continuar'
    })
    await page.wait_for_url('**/success/**', timeout=300000) # 5 min
```

### 4.3 Rate Limiting e Throttling

**Problema**: Gov.br bloqueia IPs com muitas requisições

**Solução**:
```
1. Implementar exponential backoff
2. Respeitar headers Retry-After
3. Usar proxies/VPNs se necessário (verificar legalidade)
4. Distribuir requisições ao longo do tempo
```

**Código**:
```python
import asyncio
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
async def fetch_with_retry(url: str, headers: dict):
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers, timeout=30.0)
        response.raise_for_status()
        return response.json()

# Usar no agente
try:
    data = await fetch_with_retry(
        'https://consumidor.gov.br/api/cases',
        headers={'Authorization': f'Bearer {token}'}
    )
except Exception as e:
    logger.error(f'Rate limit excedido: {e}')
    await notify_user('Sistema gov.br temporariamente indisponível')
```

### 4.4 Injeção e Validação de Entrada

**Problema**: Agente pode preencher campos incorretos ou maliciosos

**Solução**:
```
1. Validar tipos de dados
2. Sanitizar strings (remover scripts)
3. Confirmar seletores antes de preencher
```

**Código**:
```python
from bleach import clean

async def safe_fill_form(page, field_name: str, value: str):
    # Validar valor
    if field_name == 'cpf':
        if not validate_cpf(value):
            raise ValueError('CPF inválido')
    elif field_name == 'email':
        if not is_valid_email(value):
            raise ValueError('Email inválido')
    
    # Sanitizar
    safe_value = clean(value, tags=[], strip=True)
    
    # Preencher
    selector = FIELD_MAPPING.get(field_name)
    if not selector:
        raise KeyError(f'Campo desconhecido: {field_name}')
    
    await page.fill(selector, safe_value)
```

---

## 5. CHECKLIST DE IMPLEMENTAÇÃO

### Fase 1: Setup Gov.BR (2-3 semanas)

- [ ] Registrar app Justiça Ágil em https://acesso.gov.br (solicitar client_id + secret)
- [ ] Documentar fluxo OAuth2 da gov.br (endpoints, scopes, rate limits)
- [ ] Validar certificados SSL/TLS
- [ ] Testar login manual no ambiente dev
- [ ] Implementar token storage criptografado
- [ ] Setup Redis para session management

### Fase 2: Backend Integration (1-2 semanas)

- [ ] Implementar endpoints de autenticação
- [ ] Validação de JWT gov.br
- [ ] Refresh token logic
- [ ] CSRF protection
- [ ] Logging e auditoria (quem acessou, quando, do que)
- [ ] Testes E2E

### Fase 3: Agente Integration (2-3 semanas)

- [ ] Integrar Antigravidaty com backend Justiça Ágil
- [ ] Implementar WebDriver (Playwright/Selenium)
- [ ] Detecção de MFA + user intervention
- [ ] Form filling + validação
- [ ] LLM legal text generation
- [ ] Review flow (usuário aprova antes de enviar)
- [ ] Testes com Procon/Consumidor.gov.br

### Fase 4: Segurança & Compliance (1 semana)

- [ ] Audit de dados sensíveis (CPF, tokens)
- [ ] Criptografia em repouso e trânsito
- [ ] LGPD compliance (dados retidos, direito à exclusão)
- [ ] Rate limiting + DDoS protection
- [ ] Testes de penetração

---

## 6. STACK RECOMENDADO

```
┌─────────────────────────────────────────────┐
│  Frontend: React 18 + TypeScript             │
│  - Componentes de autenticação (gov.br)     │
│  - Dashboard de status do agente            │
└─────────────────────────────────────────────┘
         ↓ (autenticado + token)
┌─────────────────────────────────────────────┐
│  Backend: Node.js (Express) ou Python       │
│  - OAuth2 handler                           │
│  - Token management (refresh, encrypt)      │
│  - Session management (Redis)               │
│  - API para agente                          │
└─────────────────────────────────────────────┘
         ↓ (access_token injetado)
┌─────────────────────────────────────────────┐
│  Agente: Antigravidaty (Python)             │
│  - Playwright/Selenium WebDriver            │
│  - Form parsing + filling                   │
│  - LLM legal text generation                │
│  - MFA handling                             │
└─────────────────────────────────────────────┘
         ↓ (navegação automática)
┌─────────────────────────────────────────────┐
│  Gov.BR Portal                              │
│  - Procon / Consumidor.gov.br              │
│  - Defesa do Consumidor                     │
└─────────────────────────────────────────────┘
```

**Dependências Críticas**:
```
Backend:
- jsonwebtoken (validar JWT gov.br)
- node-jose (parsing de chaves públicas)
- redis (session store)
- bcrypt (criptografia de tokens)

Agente:
- playwright ou selenium (WebDriver)
- httpx (async HTTP)
- langchain ou similiar (LLM orchestration)
- tenacity (retry logic)
```

---

## 7. RISCOS E MITIGAÇÕES

| Risco | Impacto | Mitigação |
|-------|---------|-----------|
| Gov.br muda autenticação | Alto | Monitorar changelog gov.br, testes E2E contínuos |
| Token vazado | Crítico | Criptografia AES-256, short TTL, audit log |
| Agente faz logout usuário | Alto | Detectar logout, notificar, solicitar re-auth |
| Rate limit | Médio | Backoff exponencial, pooling de requisições |
| MFA não reconhecida | Médio | User intervention, timeout, fallback manual |
| CPF/dados PII vazados | Crítico | LGPD compliance, criptografia, access control |

---

## 8. PRÓXIMOS PASSOS

1. **Contactar GOV.BR**
   - Solicitar integração OAuth2
   - Documentação técnica oficial
   - Suporte para integrações

2. **Pesquisar API Consumidor.gov.br**
   - Verificar se existe API pública
   - Comparar com automação WebDriver
   - Decisão entre ambas

3. **Prototipo Rápido**
   - Login manual gov.br no navegador
   - Capturar token (devtools)
   - Testar acesso Procon com token

4. **Refinar Segurança**
   - Pen test
   - Validação LGPD
   - Aprovação jurídica

---

## CONCLUSÃO

A estratégia **OAuth2 + Session Management + WebDriver Instruído** é o melhor balanço entre:
- ✅ Segurança (tokens curtos, refresh, criptografia)
- ✅ Usabilidade (login manual = usuário confortável)
- ✅ Sustentabilidade (segue padrão gov.br)
- ✅ Flexibilidade (Antigravidaty assume após auth)

**Esforço estimado**: 6-8 semanas para MVP funcional e seguro.
