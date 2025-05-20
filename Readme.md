# Sistema de Cadastro de Clientes (PF/PJ)

Este é um sistema de cadastro de clientes web desenvolvido com Flask (Python) para o backend e HTML, CSS, e JavaScript (com Bootstrap e Inputmask.js) para o frontend. O sistema permite o cadastro de Pessoas Físicas (PF) e Pessoas Jurídicas (PJ), coleta diversas informações e envia os dados por email. A aplicação foi preparada com foco em segurança básica para implantação.

## Funcionalidades

*   Formulário de 3 telas:
    1.  Seleção entre Pessoa Física e Pessoa Jurídica.
    2.  Formulário de cadastro específico para PF.
    3.  Formulário de cadastro específico para PJ.
*   Validação de campos no frontend e backend.
*   Máscaras de input para campos como CPF, CNPJ, CEP, Telefone, Placa.
*   Busca automática de endereço ao preencher o CEP (API ViaCEP).
*   Campos de veículo (Placa, Modelo, Cor, Ano) preenchidos manualmente.
*   Proteção CSRF implementada.
*   Envio dos dados do formulário por email para um destinatário configurado.
*   Interface estilizada com tema azul escuro.
*   Logging básico e páginas de erro customizadas (404, 500).

## Pré-requisitos

*   Python 3.7 ou superior
*   pip (gerenciador de pacotes Python)
*   Um servidor SMTP configurado para envio de emails (ex: Gmail com "Senha de App")

## Configuração do Ambiente Local para Desenvolvimento

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
    Com o ambiente virtual ativado, instale as bibliotecas Python necessárias:
    ```bash
    python -m pip install -r requirements.txt
    ```

4.  **Configure as Variáveis de Ambiente (Credenciais de Email e Chave Secreta):**
    *   Crie um arquivo chamado `.env` na pasta raiz do projeto (`cadastro_app/.env`).
    *   Adicione as seguintes variáveis ao arquivo `.env`, substituindo pelos seus próprios valores:

        ```env
        FLASK_SECRET_KEY=sua_chave_secreta_longa_aleatoria_e_segura_aqui
        EMAIL_HOST_USER=seu_email@exemplo.com
        EMAIL_HOST_PASSWORD=sua_senha_de_email_ou_senha_de_app
        EMAIL_RECEIVER=email_destino_dos_cadastros@exemplo.com
        ```
        *   `FLASK_SECRET_KEY`: Uma string longa, aleatória e secreta. Use `python -c "import secrets; print(secrets.token_hex(32))"` para gerar uma.
        *   `EMAIL_HOST_USER`: O endereço de email que será usado para enviar os cadastros.
        *   `EMAIL_HOST_PASSWORD`: A senha do email acima. **Importante:** Se usar Gmail, gere uma "Senha de App".
        *   `EMAIL_RECEIVER`: O endereço de email que receberá os dados dos formulários.

    *   **Nota de Segurança:** O arquivo `.env` contém informações sensíveis. Adicione `.env` ao seu arquivo `.gitignore` para não enviá-lo para repositórios públicos.

## Como Executar Localmente para Desenvolvimento

1.  **Certifique-se de que o ambiente virtual está ativado.**
2.  **Navegue até a pasta raiz do projeto** (`cadastro_app`).
3.  **Execute o servidor Flask de desenvolvimento:**
    Você pode rodar diretamente o `app.py` (se ele tiver `app.run(debug=True)` no final) ou o `wsgi.py` (se você configurou `app.run(debug=True)` nele para desenvolvimento).
    Exemplo usando `app.py` (assumindo que você descomentou e ajustou `app.run` para debug):
    ```bash
    python app.py
    ```
    Ou, se `wsgi.py` está configurado para rodar com debug:
    ```bash
    python wsgi.py
    ```
4.  **Acesse a Aplicação no Navegador:**
    Abra seu navegador web e vá para o endereço:
    [http://127.0.0.1:5001](http://127.0.0.1:5001) (ou a porta que você configurou).

## Preparação para Produção

O código foi preparado com as seguintes considerações de segurança e boas práticas para produção:
*   Carregamento da `SECRET_KEY` a partir de variáveis de ambiente.
*   Proteção CSRF habilitada.
*   Logging básico implementado.
*   Handlers para erros 404 e 500.

Para implantar em um ambiente de produção, siga estas etapas gerais (os detalhes variam conforme a plataforma de hospedagem):

1.  **Escolha um Servidor de Aplicação WSGI:** Gunicorn é recomendado. Adicione `gunicorn` ao `requirements.txt`.
2.  **Use um Proxy Reverso:** Nginx ou Apache são comuns. Eles servirão arquivos estáticos e encaminharão requisições dinâmicas para o Gunicorn.
3.  **Configure HTTPS (SSL/TLS):** Essencial para segurança. Use Let's Encrypt com Certbot para certificados gratuitos.
4.  **Gerenciador de Processos:** Use `systemd` (ou similar) para garantir que sua aplicação Gunicorn rode continuamente.
5.  **Variáveis de Ambiente no Servidor:** Configure `FLASK_SECRET_KEY`, `EMAIL_HOST_USER`, etc., diretamente no ambiente do servidor de produção, em vez de depender de um arquivo `.env` (embora alguns setups de `systemd` possam carregar de um arquivo `.env`).
6.  **NÃO execute com `debug=True` em produção.**

O arquivo `wsgi.py` (`from app import app`) serve como ponto de entrada para o Gunicorn.

## Estrutura do Projeto