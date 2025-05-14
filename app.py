import os
import smtplib
import re
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import Flask, render_template, request, redirect, url_for, flash
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

app = Flask(__name__)
app.secret_key = os.urandom(24)

EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')
EMAIL_RECEIVER = os.getenv('EMAIL_RECEIVER')
EMAIL_SMTP_SERVER = 'smtp.gmail.com'
EMAIL_SMTP_PORT = 587

# --- Funções de Validação ---
def is_valid_cpf(cpf):
    cpf = re.sub(r'[^0-9]', '', cpf) # Remove non-digits
    if len(cpf) != 11 or len(set(cpf)) == 1: # Check length and if all digits are the same
        return False
    
    # Validação dos dígitos verificadores (algoritmo padrão)
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

    # Validação dos dígitos verificadores (algoritmo padrão)
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
    if resultado < 2:
        digito1 = 0
    else:
        digito1 = 11 - resultado
    
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
    if resultado < 2:
        digito2 = 0
    else:
        digito2 = 11 - resultado
        
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
        return 1900 <= year <= current_year + 1 # Permite até o próximo ano
    except ValueError:
        return False

def is_valid_placa(placa_str):
    # Padrão Mercosul: LLLNLNN (L=Letra, N=Número) -> Ex: ABC1D23
    # Padrão Antigo: LLLNNNN -> Ex: ABC1234
    placa = placa_str.upper().replace('-', '')
    if re.fullmatch(r'[A-Z]{3}[0-9][A-Z0-9][0-9]{2}', placa): # Cobre ambos os padrões se o 4o digito for opcionalmente letra
        return True
    if re.fullmatch(r'[A-Z]{3}[0-9]{4}', placa): # Padrão antigo específico
         return True
    return False


def enviar_email_cadastro_geral(dados_formulario, tipo_pessoa):
    if not EMAIL_HOST_USER or not EMAIL_HOST_PASSWORD or not EMAIL_RECEIVER:
        app.logger.error("ERRO: Credenciais de email não configuradas no .env")
        flash('Erro ao configurar o servidor de email. Contate o administrador.', 'danger')
        return False

    try:
        template_name = f'email_template_{tipo_pessoa}.html'
        subject = f'Novo Cadastro de Pessoa { "Física" if tipo_pessoa == "pf" else "Jurídica"} Recebido'
        
        html_body = render_template(template_name, data=dados_formulario)

        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = EMAIL_HOST_USER
        msg['To'] = EMAIL_RECEIVER

        msg.attach(MIMEText(html_body, 'html', 'utf-8'))

        with smtplib.SMTP(EMAIL_SMTP_SERVER, EMAIL_SMTP_PORT) as server:
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(EMAIL_HOST_USER, EMAIL_HOST_PASSWORD)
            server.sendmail(EMAIL_HOST_USER, EMAIL_RECEIVER, msg.as_string())
        
        app.logger.info(f"Email de cadastro ({tipo_pessoa.upper()}) enviado para {EMAIL_RECEIVER}")
        return True
    except Exception as e:
        app.logger.error(f"Falha ao enviar email ({tipo_pessoa.upper()}): {e}")
        flash(f'Ocorreu um erro ao tentar enviar o email de cadastro: {e}', 'danger')
        return False

@app.route('/')
def index():
    return render_template('index.html')

#@app.route('/selecionar_tipo', methods=['POST'])
#def selecionar_tipo():
#    tipo_pessoa = request.form.get('tipo_pessoa')
#    if tipo_pessoa == 'pf':
#        return redirect(url_for('cadastro_pf'))
#    elif tipo_pessoa == 'pj':
#        return redirect(url_for('cadastro_pj'))
#    else:
#        flash('Seleção inválida.', 'warning')
#        return redirect(url_for('index'))

@app.route('/cadastro_pf', methods=['GET'])
def cadastro_pf():
    return render_template('form_pf.html')

@app.route('/enviar_cadastro_pf', methods=['POST'])
def enviar_cadastro_pf():
    form_data = request.form.to_dict()
    errors = []

    # Validações Backend PF
    if not form_data.get('nome_completo'): errors.append("Nome completo é obrigatório.")
    if not form_data.get('cpf') or not is_valid_cpf(form_data['cpf']): errors.append("CPF inválido.")
    if not form_data.get('data_nascimento') or not is_valid_date(form_data['data_nascimento']): errors.append("Data de nascimento inválida.")
    if not form_data.get('estado_civil'): errors.append("Estado civil é obrigatório.")
    if not form_data.get('email') or form_data.get('email') != form_data.get('confirme_email'): errors.append("Emails não conferem ou são inválidos.")
    if not form_data.get('tel_celular'): errors.append("Telefone celular é obrigatório.") # Adicionar validação de formato se desejar
    if not form_data.get('rg'): errors.append("RG é obrigatório.")
    if not form_data.get('orgao_emissor'): errors.append("Órgão emissor do RG é obrigatório.")
    if not form_data.get('data_emissao_rg') or not is_valid_date(form_data['data_emissao_rg']): errors.append("Data de emissão do RG inválida.")
    if not form_data.get('nacionalidade'): errors.append("Nacionalidade é obrigatória.")
    if not form_data.get('nome_mae'): errors.append("Nome da mãe é obrigatório.")
    if not form_data.get('profissao'): errors.append("Profissão é obrigatória.")
    try:
        float(form_data.get('remuneracao', '0'))
    except ValueError:
        errors.append("Remuneração deve ser um número.")
    
    if not form_data.get('placa_carro') or not is_valid_placa(form_data['placa_carro']): errors.append("Placa do carro inválida.")
    if not form_data.get('modelo_carro'): errors.append("Modelo do carro é obrigatório.")
    if not form_data.get('cor_carro'): errors.append("Cor do carro é obrigatória.")
    if not form_data.get('ano_carro') or not is_valid_year(form_data['ano_carro']): errors.append("Ano do carro inválido.")

    if not form_data.get('cep'): errors.append("CEP é obrigatório.") # Adicionar validação de formato se desejar
    if not form_data.get('endereco'): errors.append("Endereço é obrigatório.")
    if not form_data.get('numero'): errors.append("Número do endereço é obrigatório.")
    if not form_data.get('bairro'): errors.append("Bairro é obrigatório.")
    if not form_data.get('cidade'): errors.append("Cidade é obrigatória.")
    if not form_data.get('estado'): errors.append("Estado é obrigatório.")


    if errors:
        for error in errors:
            flash(error, 'danger')
        return render_template('form_pf.html', form_data=form_data)

    if enviar_email_cadastro_geral(form_data, 'pf'):
        return redirect(url_for('sucesso'))
    else:
        return render_template('form_pf.html', form_data=form_data)


@app.route('/cadastro_pj', methods=['GET'])
def cadastro_pj():
    return render_template('form_pj.html')

@app.route('/enviar_cadastro_pj', methods=['POST'])
def enviar_cadastro_pj():
    form_data = request.form.to_dict()
    errors = []

    # Validações Backend PJ
    if not form_data.get('razao_social'): errors.append("Razão Social é obrigatória.")
    if not form_data.get('cnpj') or not is_valid_cnpj(form_data['cnpj']): errors.append("CNPJ inválido.")
    if not form_data.get('data_abertura') or not is_valid_date(form_data['data_abertura']): errors.append("Data de abertura inválida.")
    if not form_data.get('ramo_atividade'): errors.append("Ramo de atividade é obrigatório.")
    if not form_data.get('email_empresa') or form_data.get('email_empresa') != form_data.get('confirme_email_empresa'): errors.append("Emails da empresa não conferem ou são inválidos.")
    if not form_data.get('tel_comercial_empresa'): errors.append("Telefone comercial é obrigatório.")
    
    if not form_data.get('placa_carro_pj') or not is_valid_placa(form_data['placa_carro_pj']): errors.append("Placa do carro (PJ) inválida.")
    if not form_data.get('modelo_carro_pj'): errors.append("Modelo do carro (PJ) é obrigatório.")
    if not form_data.get('cor_carro_pj'): errors.append("Cor do carro (PJ) é obrigatória.")
    if not form_data.get('ano_carro_pj') or not is_valid_year(form_data['ano_carro_pj']): errors.append("Ano do carro (PJ) inválido.")

    if not form_data.get('cep_empresa'): errors.append("CEP da empresa é obrigatório.")
    if not form_data.get('endereco_empresa'): errors.append("Endereço da empresa é obrigatório.")
    if not form_data.get('numero_empresa'): errors.append("Número do endereço da empresa é obrigatório.")
    if not form_data.get('bairro_empresa'): errors.append("Bairro da empresa é obrigatório.")
    if not form_data.get('cidade_empresa'): errors.append("Cidade da empresa é obrigatória.")
    if not form_data.get('estado_empresa'): errors.append("Estado da empresa é obrigatório.")

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

if __name__ == '__main__':
    app.run(debug=True, port=5001)