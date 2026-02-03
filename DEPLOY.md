# 🚀 Como Publicar seu "Achadinhos" no GitHub Pages

Este guia vai te ensinar a colocar seu site no ar gratuitamente usando o GitHub.

## 0. Instalar o Git (Pré-requisito)
Parece que o seu computador ainda não tem o Git instalado.

**Opção A (Mais Rápida):**
Abra o terminal (PowerShell ou CMD) e digite:
`winget install -e --id Git.Git`

**Opção B (Via Site):**
1. Baixe em [git-scm.com/download/win](https://git-scm.com/download/win).
2. Instale clicando "Next" em tudo.
3. **Importante**: Feche e abra o terminal novamente após instalar.

## 1. Preparando o GitHub
1. Crie uma conta no [GitHub.com](https://github.com/) (se não tiver).
2. Clique no **+** (canto superior direito) -> **New repository**.
3. Nomeie como `achadinhos-shopee` (ou o que preferir).
4. Deixe como **Public**.
5. **NÃO** marque "Add a README file" nem nada. Deixe vazio.
6. Clique em **Create repository**.

## 2. Enviando seu Código (Primeira Vez)
Abra o terminal na pasta do projeto (`d:\04_APPs\Achadinhos`) e rode os comandos abaixo, um por um:

```bash
# Inicia o Git
git init

# Remove arquivos desnecessários do versionamento (Cria um .gitignore)
echo .venv/ >> .gitignore
echo __pycache__/ >> .gitignore
echo .env >> .gitignore
echo banco_ofertas_completo.csv >> .gitignore  # Opcional: Se não quiser subir o histórico gigante, mas o site precisa do ofertas.js

# Adiciona todos os arquivos
git add .

# Salva a primeira versão
git commit -m "Primeira versão do Achadinhos"

# Conecta com seu repositório remoto (TROQUE PELO SEU LINK!)
# O link aparece na página do GitHub logo após criar o repo (ex: https://github.com/SeuUsuario/achadinhos.git)
git remote add origin https://github.com/gabybarross/achadinhosdagabi.git

# Envia para a nuvem
git branch -M main
git push -u origin main
```

## 3. Ativando o Site
1. Volte na página do seu repositório no GitHub.
2. Vá em **Settings** (aba no topo).
3. No menu lateral esquerdo, clique em **Pages**.
4. Em **Build and deployment** > **Branch**, mude de `None` para `main`.
5. Clique em **Save**.

🎉 **Pronto!** Em cerca de 2 minutos, o GitHub vai te dar um link (ex: `https://seuusuario.github.io/achadinhos-shopee/`). Esse é o link do seu site ao vivo!

---

## 4. Como Atualizar Diariamente?
Toda vez que o robô rodar e achar novas ofertas, o site **não** atualiza sozinho. Você precisa enviar o arquivo `ofertas.js` atualizado para o GitHub.

Para facilitar, use o arquivo **`publicar_site.bat`** que criei para você. Basta clicar duas vezes nele, e ele fará:
1. Gera o JSON atualizado.
2. Sobe para o GitHub.
3. O site atualiza automaticamente em alguns instantes.
