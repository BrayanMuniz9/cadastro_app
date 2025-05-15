import os
import smtplib
import re
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import Flask, render_template, request, redirect, url_for, flash
from dotenv import load_dotenv
from datetime import datetime
from flask_wtf.csrf import CSRFProtect
import logging

load_dotenv()

# Configuração básica de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')

app = Flask(__name__)
csrf = CSRFProtect(app) # Proteção CSRF inicializada
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'configure_uma_secret_key_forte_no_seu_env_para_producao')

EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')
EMAIL_RECEIVER = os.getenv('EMAIL_RECEIVER')
EMAIL_SMTP_SERVER = 'smtp.gmail.com'
EMAIL_SMTP_PORT = 587

# --- Funções de Validação (sem alterações) ---
def is_valid_cpf(cpf):
    cpf = re.sub(r'[^0-9]', '', cpf)
    if len(cpf) != 11 or len(set(cpf)) == 1:
        return False
    for i in range(9, 11):
        value = sum((int(cpf[num]) * ((i + 1) - num) for num in range(0, i)))
        digit = ((value * 10) % 11) % 10
        if str(digit) != cpf[i]:
            return False
    return True

def is_valid_cnpj(cnpj):
    cnpj = re.sub(r'[^0-9]', '', cnpj)
    if len(cnpj) != 14 or len(set(cnpj)) == 1:
        return False
    tamanho = len(cnpj) - 2
    numeros = cnpj[0:tamanho]
    digitos = cnpj[tamanho:]
    soma = 0
    pos = tamanho - 7
    for i in range(tamanho):
        soma += int(numeros[i]) * pos
        pos -= 1
        if pos < 2:
            pos = 9
    resultado = soma % 11
    digito1 = 0 if resultado < 2 else 11 - resultado
    if str(digito1) != digitos[0]:
        return False
    tamanho += 1
    numeros = cnpj[0:tamanho]
    soma = 0
    pos = tamanho - 7
    for i in range(tamanho):
        soma += int(numeros[i]) * pos
        pos -= 1
        if pos < 2:
            pos = 9
    resultado = soma % 11
    digito2 = 0 if resultado < 2 else 11 - resultado
    return str(digito2) == digitos[1]

def is_valid_date(date_str, date_format="%Y-%m-%d"):
    try:
        datetime.strptime(date_str, date_format)
        return True
    except ValueError:
        return False

def is_valid_year(year_str):
    try:
        year = int(year_str)
        current_year = datetime.now().year
        return 1900 <= year <= current_year + 2 # Aumentado para +2
    except ValueError:
        return False

def is_valid_placa(placa_str):
    placa = placa_str.upper().replace('-', '')
    if re.fullmatch(r'[A-Z]{3}[0-9][A-Z0-9][0-9]{2}', placa):
        return True
    if re.fullmatch(r'[A-Z]{3}[0-9]{4}', placa):
         return True
    return False


def enviar_email_cadastro_geral(dados_formulario, tipo_pessoa):
    if not EMAIL_HOST_USER or not EMAIL_HOST_PASSWORD or not EMAIL_RECEIVER:
        app.logger.error("ERRO CRÍTICO: Credenciais de email não configuradas no .env. Não foi possível enviar o email.")
        flash('Erro interno ao processar sua solicitação. O administrador foi notificado.', 'danger') # Mensagem genérica para o usuário
        return False

    try:
        template_name = f'email_template_{tipo_pessoa}.html'
        subject = f'Novo Cadastro de Pessoa { "Física" if tipo_pessoa == "pf" else "Jurídica"} Recebido - {dados_formulario.get("nome_completo") or dados_formulario.get("razao_social", "N/A")}'

        html_body = render_template(template_name, data=dados_formulario)

        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = f"Sistema de Cadastro <{EMAIL_HOST_USER}>" # Melhor formatação do remetente
        msg['To'] = EMAIL_RECEIVER

        msg.attach(MIMEText(html_body, 'html', 'utf-8'))

        with smtplib.SMTP(EMAIL_SMTP_SERVER, EMAIL_SMTP_PORT) as server:
            server.starttls()
            server.login(EMAIL_HOST_USER, EMAIL_HOST_PASSWORD)
            server.sendmail(EMAIL_HOST_USER, EMAIL_RECEIVER, msg.as_string())

        app.logger.info(f"Email de cadastro ({tipo_pessoa.upper()}) enviado com sucesso para {EMAIL_RECEIVER} referente a {dados_formulario.get('nome_completo') or dados_formulario.get('razao_social', 'N/A')}.")
        return True
    except smtplib.SMTPAuthenticationError:
        app.logger.error(f"Falha de autenticação SMTP ao enviar email ({tipo_pessoa.upper()}). Verifique EMAIL_HOST_USER e EMAIL_HOST_PASSWORD.", exc_info=True)
        flash('Erro interno ao enviar o email de cadastro. Problema de autenticação.', 'danger')
        return False
    except Exception as e:
        app.logger.error(f"Falha CRÍTICA ao enviar email ({tipo_pessoa.upper()}): {e}", exc_info=True) # Adicionado exc_info=True
        flash(f'Ocorreu um erro ao tentar enviar o email de cadastro. Por favor, tente mais tarde.', 'danger')
        return False

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/cadastro_pf', methods=['GET'])
def cadastro_pf():
    return render_template('form_pf.html')

@app.route('/enviar_cadastro_pf', methods=['POST'])
def enviar_cadastro_pf():
    form_data = request.form.to_dict()
    errors = []

    required_fields_pf = {
        'nome_completo': "Nome completo", 'cpf': "CPF", 'data_nascimento': "Data de nascimento",
        'estado_civil': "Estado civil", 'email': "Email", 'confirme_email': "Confirmação de Email",
        'tel_celular': "Telefone celular", 'rg': "RG", 'orgao_emissor': "Órgão emissor",
        'data_emissao_rg': "Data de emissão RG", 'nacionalidade': "Nacionalidade",
        'nome_mae': "Nome da mãe", 'profissao': "Profissão", 'remuneracao': "Remuneração",
        'placa_carro': "Placa do carro", 'modelo_carro': "Modelo do carro",
        'cor_carro': "Cor do carro", 'ano_carro': "Ano do carro", 'cep': "CEP",
        'endereco': "Endereço", 'numero': "Número", 'bairro': "Bairro",
        'cidade': "Cidade", 'estado': "Estado"
    }

    for field, label in required_fields_pf.items():
        if not form_data.get(field):
            errors.append(f"{label} é obrigatório.")

    if form_data.get('cpf') and not is_valid_cpf(form_data['cpf']): errors.append("CPF inválido.")
    if form_data.get('data_nascimento') and not is_valid_date(form_data['data_nascimento']): errors.append("Data de nascimento inválida.")
    if form_data.get('email') and form_data.get('confirme_email') and form_data['email'] != form_data['confirme_email']:
        errors.append("Os emails não correspondem.")
    if form_data.get('data_emissao_rg') and not is_valid_date(form_data['data_emissao_rg']): errors.append("Data de emissão do RG inválida.")
    if form_data.get('remuneracao'):
        try:
            float(form_data['remuneracao'])
        except ValueError:
            errors.append("Remuneração deve ser um número.")
    if form_data.get('placa_carro') and not is_valid_placa(form_data['placa_carro']): errors.append("Placa do carro inválida.")
    if form_data.get('ano_carro') and not is_valid_year(form_data['ano_carro']): errors.append("Ano do carro inválido.")

    if errors:
        for error in errors:
            flash(error, 'danger')
        return render_template('form_pf.html', form_data=form_data)

    if enviar_email_cadastro_geral(form_data, 'pf'):
        return redirect(url_for('sucesso'))
    else:
        # A função enviar_email_cadastro_geral já define flash em caso de erro de envio
        return render_template('form_pf.html', form_data=form_data)


@app.route('/cadastro_pj', methods=['GET'])
def cadastro_pj():
    return render_template('form_pj.html')

@app.route('/enviar_cadastro_pj', methods=['POST'])
def enviar_cadastro_pj():
    form_data = request.form.to_dict()
    errors = []

    required_fields_pj = {
        'razao_social': "Razão Social", 'cnpj': "CNPJ", 'data_abertura': "Data de abertura",
        'ramo_atividade': "Ramo de atividade", 'email_empresa': "Email da empresa",
        'confirme_email_empresa': "Confirmação de Email da empresa",
        'tel_comercial_empresa': "Telefone comercial", 'placa_carro_pj': "Placa do carro",
        'modelo_carro_pj': "Modelo do carro", 'cor_carro_pj': "Cor do carro",
        'ano_carro_pj': "Ano do carro", 'cep_empresa': "CEP", 'endereco_empresa': "Endereço",
        'numero_empresa': "Número", 'bairro_empresa': "Bairro", 'cidade_empresa': "Cidade",
        'estado_empresa': "Estado"
    }
    for field, label in required_fields_pj.items():
        if not form_data.get(field):
            errors.append(f"{label} é obrigatório.")

    if form_data.get('cnpj') and not is_valid_cnpj(form_data['cnpj']): errors.append("CNPJ inválido.")
    if form_data.get('data_abertura') and not is_valid_date(form_data['data_abertura']): errors.append("Data de abertura inválida.")
    if form_data.get('email_empresa') and form_data.get('confirme_email_empresa') and form_data['email_empresa'] != form_data['confirme_email_empresa']:
        errors.append("Os emails da empresa não correspondem.")
    if form_data.get('placa_carro_pj') and not is_valid_placa(form_data['placa_carro_pj']): errors.append("Placa do carro (PJ) inválida.")
    if form_data.get('ano_carro_pj') and not is_valid_year(form_data['ano_carro_pj']): errors.append("Ano do carro (PJ) inválido.")


    if errors:
        for error in errors:
            flash(error, 'danger')
        return render_template('form_pj.html', form_data=form_data)

    if enviar_email_cadastro_geral(form_data, 'pj'):
        return redirect(url_for('sucesso'))
    else:
        return render_template('form_pj.html', form_data=form_data)


@app.route('/sucesso')
def sucesso():
    return render_template('success.html')

# Handlers de Erro
@app.errorhandler(404)
def page_not_found(e):
    app.logger.warning(f"Recurso não encontrado (404): {request.url} - Erro: {e}")
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    app.logger.error(f"Erro interno do servidor (500): {request.url} - Erro: {e}", exc_info=True)
    return render_template('500.html'), 500


if __name__ == '__main__':
    # Para desenvolvimento local, você pode rodar com:
    # app.run(host='0.0.0.0', port=5001, debug=True)
    # Para produção, Gunicorn chamará a instância 'app' diretamente.
    # O modo debug NÃO deve ser True em produção.
    pass