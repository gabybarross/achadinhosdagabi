import time
import requests
import hashlib
import hmac
import json
import os
from dotenv import load_dotenv

# Carrega credenciais do .env
load_dotenv()

# --- PREENCHA SUAS CREDENCIAIS AQUI ---
SHOPEE_APP_ID = os.getenv("SHOPEE_APP_ID")     
SHOPEE_API_SECRET = os.getenv("SHOPEE_API_SECRET") 

class ShopeeAPI:
    def __init__(self, app_id, secret):
        self.app_id = app_id
        self.secret = secret
        self.base_url = "https://open-api.affiliate.shopee.com.br/graphql"

    def get_categories(self):
        print(f"Buscando árvore de categorias ({self.base_url})...")
        print(f"App ID: {self.app_id}")
        
        timestamp = int(time.time())
        query = '{productCategory{categoryId,categoryName,parentId}}'
        
        # DEFININDO VARIAÇÕES DE TESTE
        # 1. Minificado padrão (sem espaços)
        payload_min = json.dumps({"query": query}, separators=(',', ':'))
        # 2. Normal (com espaços do python)
        payload_std = json.dumps({"query": query})
        
        variacoes = [
            ("Minificado + AppId|Time|Payload", payload_min, f"{self.app_id}{timestamp}{payload_min}"),
            ("Minificado + AppId|Time|Payload|Secret", payload_min, f"{self.app_id}{timestamp}{payload_min}{self.secret}"),
            ("Normal + AppId|Time|Payload", payload_std, f"{self.app_id}{timestamp}{payload_std}")
        ]

        for nome, pay_str, base_str in variacoes:
            print(f"\n--- TESTANDO: {nome} ---")
            
            # Gera Assinatura manual para garantir controle total
            signature = hmac.new(self.secret.encode(), base_str.encode(), hashlib.sha256).hexdigest()
            print(f"Assinatura: {signature[:10]}...")
            
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"SHA256 Credential={self.app_id}, Timestamp={timestamp}, Signature={signature}"
            }
            
            try:
                response = requests.post(self.base_url, headers=headers, data=pay_str)
                print(f"Status: {response.status_code}")
                
                try:
                    data = response.json()
                except:
                    print(f"Body (não-json): {response.text[:100]}")
                    continue

                if "errors" in data:
                    print(f"Erro: {data['errors'][0].get('message')}")
                    if "Expired" in str(data['errors']):
                        print(" (Aumentando Timestamp em +5 min para testar futuro...)")
                        # Se expirou, não adianta testar os outros com mesmo TS agora.
                        # Mas vamos seguir o loop.
                elif data.get("data"):
                    print(">>> SUCESSO! <<<")
                    self._salvar_json(data)
                    return # Para no primeiro que funcionar
                    
            except Exception as e:
                print(f"Exceção: {e}")

    def _salvar_json(self, data):
        categorias = data.get("data", {}).get("productCategory", [])
        print(f"Encontradas {len(categorias)} categorias.")
        with open("categorias_shopee.json", "w", encoding="utf-8") as f:
            json.dump(categorias, f, indent=2, ensure_ascii=False)
        print(f"Salvo em 'categorias_shopee.json'.")

if __name__ == "__main__":
    api = ShopeeAPI(SHOPEE_APP_ID, SHOPEE_API_SECRET)
    api.get_categories()
