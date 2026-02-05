# Manual do Projeto: Bot de Ofertas Shopee (Achadinhos)

Este documento detalha o funcionamento, critérios e automações do sistema de captura e publicação de ofertas da Shopee.

---

## 1. Visão Geral
O sistema é um **Bot Automatizado** que:
1.  Busca produtos na API de Afiliados da Shopee.
2.  Filtra os melhores produtos com base em critérios de qualidade e comissão.
3.  Organiza os produtos em **Nichos** (ex: Mercado, Eletrônicos, Moda).
4.  Gera um site estático (`index.html` + `ofertas.js`) com as ofertas.
5.  Mantém um banco de dados histórico (`.csv`) e exporta para Excel (`.xlsx`).
6.  Possui verificação automática de links para remover ofertas expiradas.

---

## 2. Estrutura de Arquivos

| Arquivo | Função |
| :--- | :--- |
| `main.py` | **Coração do sistema.** Busca ofertas, aplica filtros, define nichos e gera o site. |
| `test_link_validity.py` | **Script de Limpeza.** Verifica se links antigos ainda funcionam, limpa o banco e gera o Excel. |
| `publicar_site.bat` | **Atalho Manual.** Executa o `main.py` e sobe as alterações para o Git (Modo Rápido). |
| `run_validity_cleanup.bat` | **Automação Diária.** Roda a limpeza completa e sincroniza com o Git. |
| `banco_ofertas_completo.csv` | **Banco de Dados.** Histórico de todas as ofertas já coletadas. |
| `ofertas_para_site.xlsx` | **Relatório Excel.** Versão "limpa" e ativa das ofertas para análise. |
| `selecao.xlsx` | Lista de links manuais que o usuário quer adicionar. |
| `palavrachave.xlsx` | Lista de termos de busca que o bot deve procurar sempre. |
| `.env` | Credenciais da API (App ID e Secret). |

---

## 3. Critérios de Seleção (Lógica de Negócios)

O sistema aceita produtos seguindo duas lógicas distintas, dependendo do Nicho.

### A. Regra Geral (Padrão)
Aplicada para Eletrônicos, Casa, Moda, etc.
*   **Nota (Avaliação):** Mínimo **4.7** estrelas.
*   **Vendas:** Mínimo **50** unidades vendidas.
*   **Comissão:** Mínimo **R$ 1,50** por venda.

### B. Regra "Mercado & Despensa" (Exceção)
Aplicada para Alimentos, Limpeza e Higiene.
*   **Nota (Avaliação):** Mínimo **4.7** estrelas.
*   **Vendas:** Mínimo **50** unidades vendidas.
*   **Comissão:** **Livre** (Aceita comissões menores que R$ 1,50, pois são itens de alto giro).

### C. Definição de Nicho
O sistema decide o nicho do produto na seguinte ordem:
1.  **Por ID:** Se o ID da categoria for de Mercado (ex: 100629), vira "Mercado & Despensa".
2.  **Por Palavra-Chave:** Se o título conter termos como *sabão, arroz, chocolate*, vira "Mercado & Despensa".
3.  **Mapeamento Padrão:** Usa o mapa de IDs da Shopee (ex: 100013 = Eletrônicos).
4.  **Outros:** Se não se encaixar em nada, vira "Outros".

---

## 4. Fluxos de Execução

### Modo Automático (Diário às 09:00)
1.  O Windows executa `run_validity_cleanup.bat`.
2.  O script verifica **TODAS** as ofertas do banco na API da Shopee.
3.  Remove ofertas inativas/expiradas.
4.  Re-gera o arquivo `ofertas_para_site.xlsx` (incluindo a coluna Nicho).
5.  Atualiza o arquivo do site `ofertas.js`.
6.  Faz **Commit e Push** automático para o Git.

### Modo Manual (Quando você quiser)
Você clica em `publicar_site.bat`.
1.  Ele roda o `main.py` para descobrir **novas** ofertas.
2.  Adiciona essas ofertas ao banco e ao site.
3.  Faz **Commit e Push** automático.
4.  *Nota: Neste modo, ele NÃO verifica a validade das ofertas antigas para ser mais rápido.*

---

## 5. Como usar

1.  **Adicionar Ofertas Manuais:** Coloque os links no `selecao.xlsx` e rode o `publicar_site.bat`.
2.  **Monitorar Termos:** Adicione palavras no `palavrachave.xlsx` e rode o `publicar_site.bat`.
3.  **Ver Ofertas Ativas:** Abra o arquivo `ofertas_para_site.xlsx` (ele é atualizado todo dia de manhã).
4.  **Forçar Limpeza:** Se quiser limpar ofertas ruins agora, rode manualmente o `run_validity_cleanup.bat` (demora ~10 min).

---
*Gerado em: 05/02/2026*
