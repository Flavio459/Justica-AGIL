from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import chat, upload, claim, automation, learning, script_gen, submission, auth

app = FastAPI(title="Procon Ágil API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allow all for dev
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat.router, prefix="/api")
app.include_router(upload.router, prefix="/api")
app.include_router(claim.router, prefix="/api")
app.include_router(automation.router, prefix="/api")
app.include_router(learning.router, prefix="/api")
app.include_router(script_gen.router, prefix="/api")
app.include_router(submission.router) # NOVO: Orquestrador Integrado
app.include_router(auth.router, prefix="/api") # NOVO: Auth Gov.br

@app.get("/")
def read_root():
    return {"message": "Procon Ágil API is running"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}
