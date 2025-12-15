# Justiça Ágil

Sistema de automação para registro de reclamações no Procon/Consumidor.gov.br.

## Estrutura

```
├── backend/          # API Python FastAPI
│   ├── agents/       # Agentes de automação (navigator, generator, legal)
│   ├── services/     # Serviços (orchestrator, llm, learning)
│   ├── routers/      # Rotas API
│   └── profiles/     # Perfis Chrome persistentes
├── frontend/         # React + Vite + TailwindCSS
│   └── src/          # Código fonte
├── docs/             # Documentação
│   └── strategy_govbr.md
├── caso_real/        # Dados de teste
└── iniciar_automacao.bat
```

## Como Iniciar

### Backend
```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

### Frontend
```powershell
cd frontend
npm install
npm run dev
```

## Documentação

Consulte [docs/strategy_govbr.md](docs/strategy_govbr.md) para estratégia de integração Gov.BR.
