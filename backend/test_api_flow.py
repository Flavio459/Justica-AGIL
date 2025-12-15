import requests
import time
import json

BASE_URL = "http://127.0.0.1:8000/api/submission"

# Dados reais
PAYLOAD = {
    "company_name": "Baruke Imoveis",
    "facts": "TESTE DE INTEGRAÇÃO VIA API (ORCHESTRATOR). Em 02/12/2025, solicitei abatimento de R$ 603,60...",
    "request": "Abatimento imediato ou ressarcimento."
}

def main():
    print("\n--- 🧪 TESTE DO ORQUESTRADOR (MOCK FRONTEND) ---\n")
    
    # 0. Clean state
    try:
        requests.post(f"{BASE_URL}/stop")
    except:
        pass

    # 1. Start
    print("1️⃣  Solicitando abertura do navegador (POST /start)...")
    try:
        res = requests.post(f"{BASE_URL}/start")
        print(f"   Status: {res.status_code} | {res.json()}")
    except Exception as e:
        print(f"❌ Erro ao conectar na API: {e}")
        return

    print("\n2️⃣  Aguardando Login do Usuário...")
    print("   (Faça login na janela do Chrome que abriu...)")
    
    # 2. Polling Loging
    while True:
        try:
            res = requests.get(f"{BASE_URL}/status")
            data = res.json()
            status = data.get("status")
            
            print(f"   📡 Status: {status}")
            
            if status == "logged_in":
                print("\n✅ LOGIN DETECTADO!\n")
                break
            
            time.sleep(2)
        except Exception as e:
            print(f"❌ Erro no polling: {e}")
            break

    # 3. Execute
    print("3️⃣  Disparando Automação (POST /execute)...")
    try:
        # Enviar
        res = requests.post(f"{BASE_URL}/execute", json=PAYLOAD)
        print(f"   🚀 Resultado: {res.json()}")
    except Exception as e:
        print(f"❌ Erro ao executar: {e}")

if __name__ == "__main__":
    main()
