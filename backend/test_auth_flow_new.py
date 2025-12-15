import httpx
import asyncio

async def test_auth_flow():
    base_url = "http://localhost:8000"
    print(f"Testing Auth Flow against {base_url} (Expect Mock Mode)...")

    async with httpx.AsyncClient(follow_redirects=False) as client:
        # 1. Access Login
        print("1. Requesting /api/auth/login...")
        resp = await client.get(f"{base_url}/api/auth/login")
        
        # In mock mode, it redirects to callback
        if resp.status_code == 307 or resp.status_code == 302:
            redirect_url = resp.headers['location']
            print(f"   -> Redirected to: {redirect_url}")
            
            # 2. Follow Redirect (to Callback)
            if redirect_url.startswith("/"):
                callback_url = f"{base_url}{redirect_url}"
            else:
                callback_url = redirect_url
                
            print(f"2. Requesting Callback: {callback_url}")
            resp_callback = await client.get(callback_url)
            
            # Callback redirects to Frontend with Token
            if resp_callback.status_code == 307 or resp_callback.status_code == 302:
                frontend_redirect = resp_callback.headers['location']
                print(f"   -> Callback Redirected to: {frontend_redirect}")
                
                import urllib.parse
                parsed = urllib.parse.urlparse(frontend_redirect)
                query_params = urllib.parse.parse_qs(parsed.query)
                token = query_params.get('token', [None])[0]
                
                if token:
                    print(f"   -> SUCCESS! Obtained Session Token: {token}")
                    
                    # 3. Verify Session (/auth/me)
                    print(f"3. Verifying Session /api/auth/me with token...")
                    resp_me = await client.get(f"{base_url}/api/auth/me?token={token}")
                    print(f"   -> /me Response: {resp_me.status_code} {resp_me.json()}")
                    assert resp_me.status_code == 200
                    assert resp_me.json()['gov_br_authenticated'] is True
                else:
                    print("   -> FAILED: No token in redirect URL")
            else:
                 print(f"   -> FAILED: Callback did not redirect. Status: {resp_callback.status_code}")
        else:
            print(f"   -> FAILED: Login did not redirect. Status: {resp.status_code}")

if __name__ == "__main__":
    asyncio.run(test_auth_flow())
