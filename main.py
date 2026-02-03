import pandas as pd
import json
import os
import time
import requests
import hashlib
import hmac
from datetime import datetime
from dotenv import load_dotenv

# Carrega variáveis de ambiente do arquivo .env
load_dotenv()

# --- CONFIGURAÇÕES E MAPEAMENTOS (DO NOTEBOOK) ---
MAPA_NOMES = {
    100630: "Beleza", 
    100631: "Pet", 
    100632: "Mãe_e_Bebê",
    100633: "Moda_Infantil", 
    100635: "Câmeras-e-Drones", 
    100636: "Casa_e_Construcao",
    100637: "Esportes_e_Lazer", 
    100638: "Papelaria", 
    100001: "Saúde",
    100010: "Eletrodomesticos", 
    100011: "Roupas_Masculinas", 
    100013: "Celulares",
    100017: "Moda_Feminina", 
    100532: "Sapatos_Femininos", 
    100533: "Bolsas_Masculinas",
    100009: "Acessorios_Moda", 
    100535: "Áudio", 
    102187: "Pecas_Veiculos", 
    100015: "Viagens_e_Bagagens",
    100643: "Livros_Revistas",
    100639: "CD",
    100016: "Bolsas_Femininas",
    100012: "Sapatos_Masculinos",
    100629: "Alimentos_e_Bebidas",            
    100534: "Relógios"
    
}

ARQUIVO_HISTORICO = "banco_ofertas_completo.csv"
ARQUIVO_JS_SITE = "ofertas.js"

# --- CREDENCIAIS (DO ARQUIVO .ENV) ---
SHOPEE_APP_ID = os.getenv("SHOPEE_APP_ID")
SHOPEE_API_SECRET = os.getenv("SHOPEE_API_SECRET")

class ShopeeMasterBot:
    def __init__(self, app_id, secret):
        self.app_id = app_id
        self.secret = secret
        self.api_url = "https://open-api.affiliate.shopee.com.br/graphql"
        self.file_historico = ARQUIVO_HISTORICO

    def _generate_signature(self, payload, timestamp):
        # Lógica do Notebook: AppId + TS + Payload + Secret
        # NOTA: Se der erro de assinatura, voltamos para o padrão (sem secret no final)
        # Mas o user pediu para seguir o notebook.
        signature_string = f"{self.app_id}{timestamp}{payload}{self.secret}"
        return hashlib.sha256(signature_string.encode('utf-8')).hexdigest()

    def query_api(self, page=1, cat_id=None, sort_type=1, list_type=0):
        """
        Constrói a query GraphQL tratando a dependência listType <-> matchId.
        """
        # Regra do Erro: "listType must contain matchId"
        # Se list_type != 0, precisamos passar 'matchId'.
        # Se for busca Global (sem cat_id), forçamos list_type=0.
        
        real_list_type = list_type
        if real_list_type != 0 and not cat_id:
            real_list_type = 0 # Fallback para evita erro em busca global
            
        args_parts = [
            f"page: {page}",
            "limit: 50",
            f"sortType: {sort_type}"
        ]
        
        if real_list_type != 0:
            args_parts.append(f"listType: {real_list_type}")
            if cat_id:
                args_parts.append(f"matchId: {cat_id}")
        elif cat_id:
            # Se list_type é 0 (Standard), usamos o parâmetro específico de categoria
            args_parts.append(f"productCatId: {cat_id}")
            
        args_str = ", ".join(args_parts)
        
        query = f"""
        {{
            productOfferV2({args_str}) {{
                nodes {{
                    productName
                    itemId
                    commissionRate
                    commission
                    price
                    sales
                    imageUrl
                    shopName
                    productLink
                    offerLink
                    periodStartTime
                    periodEndTime
                    priceMin
                    priceMax
                    productCatIds
                    ratingStar
                    priceDiscountRate
                    shopId
                    shopType
                    sellerCommissionRate
                    shopeeCommissionRate
                }}
            }}
        }}
        """
        # COPIADO DO NOTEBOOK (SEM MINIFICAÇÃO)
        payload = json.dumps({"query": query})
        
        timestamp = int(time.time())
        signature = self._generate_signature(payload, timestamp)
        
        headers = {
            "Authorization": f"SHA256 Credential={self.app_id}, Timestamp={timestamp}, Signature={signature}",
            "Content-Type": "application/json"
        }
        
        try:
            print(f"   -> Req API ({page} | L:{real_list_type} S:{sort_type})...", end="")
            response = requests.post(self.api_url, headers=headers, data=payload, timeout=20)
            res_json = response.json()
            
            # Tratamento de Erro e Retry para Rate Limit
            if "errors" in res_json: 
                msg = res_json['errors'][0].get('message')
                print(f" [ERRO: {msg}]")
                
                # Se for Rate Limit (10030), espera e tenta de novo
                if "10030" in str(msg) or "Rate limit" in str(msg):
                    print("      [RATE LIMIT] Esperando 5s para tentar novamente...")
                    time.sleep(5)
                    response = requests.post(self.api_url, headers=headers, data=payload, timeout=20)
                    res_json = response.json()
                    if "errors" in res_json:
                        print(f"      [FALHA FINAL]: {res_json['errors'][0].get('message')}")
                        return []
                    else:
                        print("      [SUCESSO NO RETRY]")
                else:
                    return []
            
            print(" [OK]")
            return res_json.get("data", {}).get("productOfferV2", {}).get("nodes", [])
        except Exception as e:
            print(f" [EXCECAO: {e}]")
            return []

    # --- ESTRATÉGIAS DE BUSCA (Baseado nos ENUMS da Shopee) ---
    # Global
    # TOP_PERFORMING = 2 (Not sortable) -> Requer matchId, então usamos 0 com Sort 2
    # ALL = 0 (Not sortable - Recommendation)
    
    # Por Categoria (list_type = 4)
    # RELEVANCE_DESC = 1
    # ITEM_SOLD_DESC = 2
    # COMMISSION_DESC = 5
    
    def salvar_dados(self, nodes, estrategia):
        if not nodes: return 0
        df_novos = pd.DataFrame(nodes)
        
        # 1. Processamento Numérico e Limpeza
        colunas_num = ['price', 'commissionRate', 'commission', 'ratingStar', 'sales']
        for col in colunas_num:
            if col in df_novos.columns:
                df_novos[col] = pd.to_numeric(df_novos[col], errors='coerce').fillna(0)

        # 2. Recalculo de Comissão se Zerado
        df_novos['commission'] = df_novos.apply(
            lambda x: round(float(x['price']) * float(x['commissionRate']), 2) 
            if x['commission'] == 0 else x['commission'], axis=1
        )
        
        # 3. Filtros de Qualidade (Rigorosos)
        df_filtrado = df_novos[(df_novos['ratingStar'] >= 4.7) & 
                               (df_novos['sales'] >= 50) & 
                               (df_novos['commission'] >= 1.50)].copy()
        
        if df_filtrado.empty: return 0

        agora = datetime.now().strftime("%d/%m/%Y %H:%M")
        df_filtrado.insert(0, 'Data Coleta', agora)
        df_filtrado.insert(1, 'Estrategia', estrategia) # Nova coluna de rastreio

        # 4. Tratamento para CSV (Ponto -> Virgula para Excel BR)
        df_para_salvar = df_filtrado.copy()
        for col in colunas_num:
            if col in df_para_salvar.columns:
                 df_para_salvar[col] = df_para_salvar[col].apply(
                    lambda x: str(round(x, 2)).replace('.', ',') if isinstance(x, (int, float)) else x
                )

        # 5. Persistência (Append Mode)
        try:
            # Se arquivo não existe, salva com header
            if not os.path.exists(self.file_historico):
                df_para_salvar.to_csv(self.file_historico, sep=';', index=False, encoding='utf-8-sig')
            else:
                # Lógica de Migração e Alinhamento de Colunas
                try: 
                    # 1. Lê apenas o cabeçalho do arquivo existente
                    df_header = pd.read_csv(self.file_historico, sep=';', nrows=0)
                    existing_cols = list(df_header.columns)
                    
                    # 2. Verifica se precisa migrar (adicionar coluna Estrategia)
                    if 'Estrategia' not in existing_cols:
                        print(" [INFO] Migrando banco de dados para incluir coluna 'Estrategia'...")
                        df_full = pd.read_csv(self.file_historico, sep=';', encoding='utf-8-sig')
                        df_full['Estrategia'] = 'Legado' # Adiciona no final
                        df_full.to_csv(self.file_historico, sep=';', index=False, encoding='utf-8-sig')
                        # Atualiza lista de colunas esperada
                        existing_cols = list(df_full.columns)
                    
                    # 3. ALINHAMENTO IMPORTANTE: Força o novo DF a ter a mesma ordem de colunas do arquivo
                    # Isso evita que 'Estrategia' caia na coluna 'productName'
                    
                    # Garante que todas as colunas do arquivo existam no novo DF (preenche com vazio se faltar algo)
                    for col in existing_cols:
                        if col not in df_para_salvar.columns:
                            df_para_salvar[col] = ""
                            
                    # Reordena o novo DF para bater com o arquivo (crucial para mode='a')
                    df_para_salvar = df_para_salvar[existing_cols]
                    
                except Exception as e:
                    print(f" [AVISO] Falha ao alinhar colunas: {e}")
                    # Se falhar, tenta salvar assim mesmo (pode dar mismatch, mas não perde dados)
                
                df_para_salvar.to_csv(self.file_historico, mode='a', sep=';', index=False, header=False, encoding='utf-8-sig')
        except PermissionError:
            print(f" [ERRO] Permissão negada ao salvar CSV. Feche o arquivo!")
        
        return len(df_para_salvar)

    def descobrir_ids_unicos(self):
        if not os.path.exists(self.file_historico): return []
        try:
            df = pd.read_csv(self.file_historico, sep=';', encoding='utf-8-sig', on_bad_lines='skip')
            ids = set()
            if 'productCatIds' not in df.columns: return []
            
            for item in df['productCatIds'].dropna():
                try:
                    # Formato '[123, 456]' ou '123'
                    limpo = str(item).replace('[', '').replace(']', '').split(',')[0].strip()
                    if limpo and int(limpo) != 0: ids.add(int(limpo))
                except: continue
            return list(ids)
        except Exception as e:
            print(f"Erro ao ler IDs: {e}")
            return []

    def organizar_arquivos_e_exportar_site(self):
        """Lê o histórico completo, limpa duplicatas, gera CSVs de nicho e exporta o JS do site."""
        if not os.path.exists(self.file_historico): 
            print("Nenhum dado para organizar.")
            return

        print("\n[INFO] Consolidando banco de dados e gerando ofertas...")
        try:
            # Lê tudo como string para evitar problemas de conversão imediata
            df = pd.read_csv(self.file_historico, sep=';', encoding='utf-8-sig', dtype=str)
            
            # --- NOVA LÓGICA DE DEDUPLICAÇÃO (Recente + Maior Comissão) ---
            try:
                # 1. Converte Data para Ordenação
                df['_temp_date'] = pd.to_datetime(df['Data Coleta'], format='%d/%m/%Y %H:%M', errors='coerce')
                
                # 2. Converte Comissão para Float (Robustness Upgrade)
                # Remove pontos de milhar antes de troca virgula por ponto
                # Ex: '1.200,50' -> '1200,50' -> '1200.50'
                # Ex: '4.236.759' (Garbage ID) -> '4236759' -> Float (ok para ordenar, mesmo sendo lixo)
                def clean_float(x):
                    try:
                        val = str(x).replace('.', '').replace(',', '.')
                        return float(val)
                    except:
                        return 0.0
                        
                df['_temp_comm'] = df['commission'].apply(clean_float)
                
                # 3. Ordena: Mais Recente (Desc) -> Maior Comissão (Desc)
                df = df.sort_values(by=['_temp_date', '_temp_comm'], ascending=[False, False])
                
                # 4. Remove Duplicatas (Mantendo o primeiro = mais recente/melhor comissão)
                if 'itemId' in df.columns:
                    df = df.drop_duplicates(subset=['itemId'], keep='first')
                
                # 5. Limpa colunas temporárias
                df = df.drop(columns=['_temp_date', '_temp_comm'])
                
            except Exception as e:
                print(f" [AVISO] Falha na ordenação inteligente, usando padrão: {e}")
                if 'itemId' in df.columns:
                    df = df.drop_duplicates(subset=['itemId'], keep='last')
            
            # Salva limpo (Tratando Erro de Permissão)
            try:
                df.to_csv(self.file_historico, sep=';', index=False, encoding='utf-8-sig')
            except PermissionError:
                print(f" [ERRO CRÍTICO] Não foi possível salvar '{self.file_historico}'. O ARQUIVO ESTÁ ABERTO? Feche-o e tente novamente.")
                return 
            
            # --- GERAÇÃO DE SAÍDA PARA O SITE (ofertas.js) ---
            ofertas_site = []
            
            # Itera sobre o DataFrame limpo
            for _, row in df.iterrows():
                try:
                    # --- Tratamento Estatístico de Preços (Código do Usuário Adaptado) ---
                    try:
                        # Convertendo strings do CSV (ex: "25,90") de volta para float
                        p_atual = float(str(row.get('price', 0)).replace(',', '.'))
                        p_min = float(str(row.get('priceMin', p_atual)).replace(',', '.'))
                        p_max = float(str(row.get('priceMax', p_atual)).replace(',', '.'))
                        # Tenta pegar taxa de desconto numérica ou string com %
                        raw_desc = str(row.get('priceDiscountRate', 0)).replace('%', '')
                        desc_rate = float(raw_desc) if raw_desc else 0
                    except:
                        p_atual = p_min = p_max = desc_rate = 0

                    # --- Lógica "A partir de" ---
                    # Se o preço mínimo for menor que o máximo, indicamos a variação
                    if p_min < p_max and p_min > 0:
                        preco_final_str = f"A partir de R$ {p_min:.2f}".replace('.', ',')
                        referencia_preco = p_min
                    else:
                        preco_final_str = f"R$ {p_atual:.2f}".replace('.', ',')
                        referencia_preco = p_atual

                    # --- Cálculo Fidedigno do Preço Original ---
                    preco_orig_str = ""
                    desconto_badge = "" # String para o frontend
                    
                    if desc_rate > 0:
                        # Normaliza taxa (ex: 10 ou 0.10)
                        # Geralmente Shopee manda 10, 25, 50 (inteiro)
                        taxa = desc_rate / 100 if desc_rate > 1 else desc_rate
                        
                        if taxa > 0 and taxa < 1:
                            try:
                                orig_raw = referencia_preco / (1 - taxa)
                                preco_orig_str = f"R$ {orig_raw:.2f}".replace('.', ',')
                                desconto_badge = f"{int(taxa * 100)}%"
                            except: pass

                    # Categoria (Mantendo a lógica do mapa)
                    cat_ids_str = str(row.get('productCatIds', ''))
                    categoria_nome = "Outros"
                    for cid, nome in MAPA_NOMES.items():
                        if str(cid) in cat_ids_str:
                            categoria_nome = nome.replace('_', ' ') 
                            break
                    
                    # Objeto JSON para o Frontend (Mantendo chaves compatíveis com index.html)
                    oferta_json = {
                        "id": str(row.get('itemId')),
                        "titulo": str(row.get('productName')),
                        "imagem_url": str(row.get('imageUrl')),
                        "preco_original": preco_orig_str,
                        "preco_promocional": preco_final_str,
                        "desconto": desconto_badge, # index.html usa 'desconto'
                        "nota": str(row.get('ratingStar', '0')).replace('.', ','), # Mantendo numero/string safe
                        "categoria": categoria_nome,
                        "link_afiliado": str(row.get('offerLink')),
                        "data_coleta": str(row.get('Data Coleta', '')),
                        # Novos campos do snippet (Frontend pode usar futuramente)
                        "vendas": f"{int(float(str(row.get('sales', 0)).replace(',', '.')))} vendidos",
                        "loja": str(row.get('shopName', '')),
                        "ativo": True
                    }
                    ofertas_site.append(oferta_json)
                except Exception as e:
                    # print(f"Erro item: {e}")
                    continue

            # Salva o arquivo JS
            js_content = f"window.ACHADINHOS_OFERTAS = {json.dumps(ofertas_site, ensure_ascii=False, indent=2)};"
            with open(ARQUIVO_JS_SITE, 'w', encoding='utf-8') as f:
                f.write(js_content)
            print(f"[OK] Site Atualizado: {len(ofertas_site)} ofertas em '{ARQUIVO_JS_SITE}'")
            print(f"[OK] Banco CSV Consolidado: {len(df)} linhas em '{self.file_historico}'")

        except Exception as e:
            print(f"Erro na organizacao: {e}")

def main():
    print("--- INICIANDO BOT SHOPEE MASTER (Multi-Strategy) ---")
    
    bot = ShopeeMasterBot(SHOPEE_APP_ID, SHOPEE_API_SECRET)
    
    # FASE 1: Estratégias Globais (Sem Categoria específica)
    print("\n[Fase 1] Buscas Globais...")
    estrategias_globais = [
        ("Mais Vendidos Geral", 0, 2), # list_type=0 (Global), sort_type=2 (Sold Desc)
        ("Recomendação Geral", 0, 0) # list_type=0 (All)
    ]
    
    for nome_est, l_type, s_type in estrategias_globais:
        print(f" -> Executando: {nome_est}...")
        res = bot.query_api(page=1, sort_type=s_type, list_type=l_type)
        count = bot.salvar_dados(res, nome_est)
        print(f"    + {count} itens salvos.")

    # 2. Descobre quais categorias foram encontradas (Sementes)
    ids_encontrados = bot.descobrir_ids_unicos()
    
    # FASE 2: Mineração Profunda por Categoria
    if ids_encontrados:
        print(f"\n[Fase 2] Minerando {len(ids_encontrados)} Nichos Específicos...")
        
        # Strategies por Categoria
        # list_type=4 (Detail Category)
        estrategias_nicho = [
            ("Mais Vendidos", 2),   # ITEM_SOLD_DESC
            ("Alta Comissão", 5),   # COMMISSION_DESC
            ("Relevância", 1)       # RELEVANCE_DESC
        ]
        
        for cid in ids_encontrados:
            nome_nicho = MAPA_NOMES.get(cid, str(cid))
            print(f" -> Nicho: {nome_nicho} (ID: {cid})")
            
            for nome_est, s_type in estrategias_nicho:
                # print(f"    - {nome_est}...", end="")
                res_cat = bot.query_api(page=1, cat_id=cid, sort_type=s_type, list_type=4) 
                saved = bot.salvar_dados(res_cat, f"{nome_nicho} - {nome_est}")
                # print(f" {saved} novos.")
                time.sleep(2) # Respeitar API (Aumentado para evitar 10030)

    # 4. Finalização: Limpeza e Geração do Site
    bot.organizar_arquivos_e_exportar_site()
    print("\n--- CICLO FINALIZADO ---")

if __name__ == "__main__":
    main()
