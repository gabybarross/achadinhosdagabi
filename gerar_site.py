from main import ShopeeMasterBot, SHOPEE_APP_ID, SHOPEE_API_SECRET

def gerar_apenas_site():
    print("--- 🔄 REGERANDO ARQUIVOS DO SITE (SEM NOVA BUSCA) ---")
    
    # Instancia o bot apenas para usar os métodos de organização
    bot = ShopeeMasterBot(SHOPEE_APP_ID, SHOPEE_API_SECRET)
    
    # Chama apenas a função final
    bot.organizar_arquivos_e_exportar_site()
    
    print("--- ✅ CONCLUÍDO! OFERTAS.JS ATUALIZADO ---")

if __name__ == "__main__":
    gerar_apenas_site()
