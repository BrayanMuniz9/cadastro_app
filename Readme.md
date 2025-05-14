# Sistema de Cadastro de Clientes (PF/PJ)

Este é um sistema de cadastro de clientes web desenvolvido com Flask (Python) para o backend e HTML, CSS, e JavaScript (com Bootstrap e Inputmask.js) para o frontend. O sistema permite o cadastro de Pessoas Físicas (PF) e Pessoas Jurídicas (PJ), coleta diversas informações e envia os dados por email.

## Funcionalidades

*   Formulário de 3 telas:
    1.  Seleção entre Pessoa Física e Pessoa Jurídica.
    2.  Formulário de cadastro específico para PF.
    3.  Formulário de cadastro específico para PJ.
*   Validação de campos no frontend e backend.
*   Máscaras de input para campos como CPF, CNPJ, CEP, Telefone, Placa.
*   Busca automática de endereço ao preencher o CEP (API ViaCEP).
*   Campos de veículo (Placa, Modelo, Cor, Ano) preenchidos manualmente.
*   Envio dos dados do formulário por email para um destinatário configurado.
*   Interface estilizada com tema azul escuro.

## Pré-requisitos

*   Python 3.7 ou superior
*   pip (gerenciador de pacotes Python)
*   Um servidor SMTP configurado para envio de emails (ex: Gmail com "Senha de App")

## Configuração do Ambiente

1.  **Clone o Repositório (ou copie os arquivos):**
    Se o projeto estiver em um repositório Git:
    ```bash
    git clone <url_do_repositorio>
    cd nome_do_projeto
    ```
    Caso contrário, apenas navegue até a pasta raiz do projeto (`cadastro_app`).

2.  **Crie e Ative um Ambiente Virtual:**
    É altamente recomendado usar um ambiente virtual para isolar as dependências do projeto.

    *   No Windows:
        ```bash
        python -m venv venv
        .\venv\Scripts\activate
        ```
    *   No macOS/Linux:
        ```bash
        python3 -m venv venv
        source venv/bin/activate
        ```

3.  **Instale as Dependências:**
    Com o ambiente virtual ativado, instale as bibliotecas Python necessárias listadas no arquivo `requirements.txt`:
    ```bash
    pip install -r requirements.txt
    ```
    Se o arquivo `requirements.txt` não existir, crie-o com o seguinte conteúdo e depois execute o comando `pip install`:
    ```txt
    Flask
    python-dotenv
    requests
    ```

4.  **Configure as Variáveis de Ambiente (Credenciais de Email):**
    *   Crie um arquivo chamado `.env` na pasta raiz do projeto (`cadastro_app/.env`).
    *   Adicione as seguintes variáveis ao arquivo `.env`, substituindo pelos seus próprios valores:

        ```env
        EMAIL_HOST_USER=seu_email@exemplo.com
        EMAIL_HOST_PASSWORD=sua_senha_de_email_ou_senha_de_app
        EMAIL_RECEIVER=email_destino_dos_cadastros@exemplo.com
        ```
        *   `EMAIL_HOST_USER`: O endereço de email que será usado para enviar os cadastros.
        *   `EMAIL_HOST_PASSWORD`: A senha do email acima. **Importante:** Se usar Gmail, você precisará gerar uma "Senha de App". Vá para sua Conta Google -> Segurança -> Senhas de app. Não use sua senha principal do Gmail aqui.
        *   `EMAIL_RECEIVER`: O endereço de email que receberá os dados dos formulários preenchidos.

    *   **Nota de Segurança:** O arquivo `.env` contém informações sensíveis. Certifique-se de que ele **não seja enviado para repositórios públicos** (adicione `.env` ao seu arquivo `.gitignore`).

## Como Executar a Aplicação

1.  **Certifique-se de que o ambiente virtual está ativado.** (Você verá `(venv)` no início do seu prompt de comando).
2.  **Navegue até a pasta raiz do projeto** (`cadastro_app`) no seu terminal, se ainda não estiver lá.
3.  **Execute o servidor Flask:**
    ```bash
    python app.py
    ```
4.  **Acesse a Aplicação no Navegador:**
    Abra seu navegador web e vá para o endereço:
    [http://127.0.0.1:5001](http://127.0.0.1:5001)

    (A porta padrão é `5001` conforme configurado em `app.py`. Se você alterou, use a porta correspondente).

## Estrutura do Projeto

/cadastro_app
app.py # Lógica do backend Flask e rotas
.env # Credenciais de email (NÃO versionar)
requirements.txt # Dependências Python
/static # Arquivos estáticos (CSS, JS, Imagens)
/css
style.css
/js
inputmask.min.js # Biblioteca de máscara
script.js # JavaScript customizado
/images
logo.png
favicon.ico
/templates # Arquivos HTML (Jinja2 templates)
index.html
form_pf.html
form_pj.html
success.html
_footer.html # Parcial do rodapé
email_template_pf.html
email_template_pj.html

## Tecnologias Utilizadas

*   **Backend:**
    *   Python
    *   Flask (Framework web)
    *   python-dotenv (Para carregar variáveis de ambiente)
*   **Frontend:**
    *   HTML5
    *   CSS3
    *   JavaScript
    *   Bootstrap 5 (Framework CSS)
    *   Inputmask.js (Para máscaras de input)
    *   Font Awesome (Ícones)
    *   Google Fonts (Poppins)
*   **APIs Externas (Frontend):**
    *   ViaCEP (Para preenchimento de endereço)

## Possíveis Melhorias Futuras

*   Persistência de dados em um banco de dados (ex: SQLite, PostgreSQL).
*   Autenticação de usuários.
*   Validações mais complexas no backend.
*   Testes unitários e de integração.
*   Melhorias na interface do usuário e experiência.
*   Tratamento de erros mais robusto.