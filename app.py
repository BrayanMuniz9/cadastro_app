# --- app.py MODIFICADO (com upload de DOC e anexo CSV) ---
import os
import smtplib
import re
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from flask import Flask, render_template, request, redirect, url_for, flash
from dotenv import load_dotenv
from datetime import datetime
from flask_wtf.csrf import CSRFProtect
import logging
from werkzeug.utils import secure_filename
import csv # ### ADICIONADO PARA CSV ###
import io  # ### ADICIONADO PARA CSV ###
from collections import OrderedDict

load_dotenv()

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'pdf'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

if not os.path.exists(UPLOAD_FOLDER):
    try:
        os.makedirs(UPLOAD_FOLDER)
        app.logger.info(f"Pasta '{UPLOAD_FOLDER}' criada com sucesso.")
    except OSError as e:
        app.logger.error(f"Erro ao criar a pasta '{UPLOAD_FOLDER}': {e}")

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

csrf = CSRFProtect(app)
SECRET_KEY_FROM_ENV = os.getenv('FLASK_SECRET_KEY')
if not SECRET_KEY_FROM_ENV or SECRET_KEY_FROM_ENV == 'configure_uma_secret_key_forte_no_seu_env_para_producao':
    app.logger.warning("AVISO CRÍTICO: FLASK_SECRET_KEY não configurada ou usando fallback.")
    app.secret_key = 'DEV_FALLBACK_VERY_INSECURE_KEY_XYZ123_CHANGE_ME_AGAIN'
else:
    app.secret_key = SECRET_KEY_FROM_ENV
    app.logger.info(f"FLASK_SECRET_KEY carregada do .env com sucesso.")

EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')
EMAIL_RECEIVER = os.getenv('EMAIL_RECEIVER')
EMAIL_SMTP_SERVER = 'smtp.gmail.com'
EMAIL_SMTP_PORT = 587

# --- Funções de Validação (sem alterações) ---
def is_valid_cpf(cpf): # seu código aqui
    cpf = re.sub(r'[^0-9]', '', cpf)
    if len(cpf) != 11 or len(set(cpf)) == 1: return False
    for i in range(9, 11):
        value = sum((int(cpf[num]) * ((i + 1) - num) for num in range(0, i)))
        digit = ((value * 10) % 11) % 10
        if str(digit) != cpf[i]: return False
    return True

def is_valid_cnpj(cnpj): # seu código aqui
    cnpj = re.sub(r'[^0-9]', '', cnpj)
    if len(cnpj) != 14 or len(set(cnpj)) == 1: return False
    tamanho = len(cnpj) - 2; numeros = cnpj[0:tamanho]; digitos = cnpj[tamanho:]
    soma = 0; pos = tamanho - 7
    for i in range(tamanho):
        soma += int(numeros[i]) * pos; pos -= 1
        if pos < 2: pos = 9
    resultado = soma % 11
    digito1 = 0 if resultado < 2 else 11 - resultado
    if str(digito1) != digitos[0]: return False
    tamanho += 1; numeros = cnpj[0:tamanho]; soma = 0; pos = tamanho - 7
    for i in range(tamanho):
        soma += int(numeros[i]) * pos; pos -= 1
        if pos < 2: pos = 9
    resultado = soma % 11
    digito2 = 0 if resultado < 2 else 11 - resultado
    return str(digito2) == digitos[1]

def is_valid_date(date_str, date_format="%Y-%m-%d"): # seu código aqui
    try: datetime.strptime(date_str, date_format); return True
    except ValueError: return False

def is_valid_year(year_str): # seu código aqui
    try: year = int(year_str); current_year = datetime.now().year; return 1900 <= year <= current_year + 2
    except ValueError: return False

def is_valid_placa(placa_str): # seu código aqui
    placa = placa_str.upper().replace('-', '')
    if re.fullmatch(r'[A-Z]{3}[0-9][A-Z0-9][0-9]{2}', placa): return True
    if re.fullmatch(r'[A-Z]{3}[0-9]{4}', placa): return True
    return False

# ### MODIFICADO: Adicionado csv_filename e csv_content como parâmetros ###
def enviar_email_cadastro_geral(dados_formulario, tipo_pessoa, anexo_doc_path=None, csv_filename=None, csv_content=None):
    if not EMAIL_HOST_USER or not EMAIL_HOST_PASSWORD or not EMAIL_RECEIVER:
        app.logger.error("ERRO CRÍTICO: Credenciais de email não configuradas no .env.")
        flash('Erro interno ao processar sua solicitação. O administrador foi notificado.', 'danger')
        return False

    try:
        template_name = f'email_template_{tipo_pessoa}.html'
        subject_name = dados_formulario.get("nome_completo") or dados_formulario.get("razao_social", "N/A")
        subject = f'Novo Cadastro ({tipo_pessoa.upper()}) - {subject_name}'
        
        # Adiciona o ano atual aos dados para o template de email
        dados_formulario['ano_atual'] = datetime.now().year
        html_body = render_template(template_name, data=dados_formulario)

        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = f"Sistema de Cadastro CLA <{EMAIL_HOST_USER}>"
        msg['To'] = EMAIL_RECEIVER
        msg.attach(MIMEText(html_body, 'html', 'utf-8'))

        # Anexar documento (RG/CNH/Contrato Social)
        if anexo_doc_path and os.path.exists(anexo_doc_path):
            try:
                with open(anexo_doc_path, "rb") as attachment:
                    part = MIMEBase("application", "octet-stream")
                    part.set_payload(attachment.read())
                encoders.encode_base64(part)
                part.add_header(
                    "Content-Disposition",
                    f"attachment; filename= {os.path.basename(anexo_doc_path)}",
                )
                msg.attach(part)
                app.logger.info(f"Anexo de documento {os.path.basename(anexo_doc_path)} adicionado ao email.")
            except Exception as e_attach_doc:
                app.logger.error(f"Erro ao anexar documento {anexo_doc_path}: {e_attach_doc}", exc_info=True)

        # ### ADICIONADO: Anexar arquivo CSV ###
        if csv_content and csv_filename:
            try:
                part_csv = MIMEBase('text', 'csv')
                part_csv.set_payload(csv_content.encode('utf-8')) # CSV como string, precisa ser bytes
                encoders.encode_base64(part_csv) # Embora para text/csv não seja estritamente necessário, é seguro
                part_csv.add_header('Content-Disposition', f'attachment; filename="{csv_filename}"')
                part_csv.set_param('charset', 'utf-8', header='Content-Type') # Garante charset para o CSV
                msg.attach(part_csv)
                app.logger.info(f"Anexo CSV {csv_filename} adicionado ao email.")
            except Exception as e_attach_csv:
                app.logger.error(f"Erro ao anexar CSV {csv_filename}: {e_attach_csv}", exc_info=True)
        # ------------------------------------

        with smtplib.SMTP(EMAIL_SMTP_SERVER, EMAIL_SMTP_PORT) as server:
            server.starttls()
            server.login(EMAIL_HOST_USER, EMAIL_HOST_PASSWORD)
            server.sendmail(EMAIL_HOST_USER, EMAIL_RECEIVER, msg.as_string())
        
        app.logger.info(f"Email de cadastro ({tipo_pessoa.upper()}) enviado com sucesso para {EMAIL_RECEIVER}.")
        return True
    except smtplib.SMTPAuthenticationError:
        app.logger.error(f"Falha de autenticação SMTP.", exc_info=True)
        flash('Erro interno ao enviar o email de cadastro (autenticação).', 'danger')
        return False
    except Exception as e:
        app.logger.error(f"Falha CRÍTICA ao enviar email ({tipo_pessoa.upper()}): {e}", exc_info=True)
        flash(f'Ocorreu um erro ao tentar enviar o email de cadastro.', 'danger')
        return False
    finally:
        if anexo_doc_path and os.path.exists(anexo_doc_path):
            try:
                os.remove(anexo_doc_path)
                app.logger.info(f"Arquivo de anexo de documento temporário {anexo_doc_path} removido.")
            except Exception as e_remove_doc:
                app.logger.error(f"Erro ao remover anexo de documento {anexo_doc_path}: {e_remove_doc}", exc_info=True)

# ### ADICIONADO: Função para gerar conteúdo CSV ###
def gerar_conteudo_csv(dados_formulario, tipo_pessoa):
    output = io.StringIO()
    # ### MODIFICADO: Usar ponto e vírgula como delimitador ###
    writer = csv.writer(output, delimiter=';', quoting=csv.QUOTE_MINIMAL) 
    # Ou, para ser ainda mais seguro com aspas, mesmo com ponto e vírgula:
    # writer = csv.writer(output, delimiter=';', quoting=csv.QUOTE_ALL)

    # Cabeçalho para o formato de duas colunas
    headers_duas_colunas = ['Campo', 'Valor']
    writer.writerow(headers_duas_colunas)

    # Definir os campos e seus rótulos amigáveis em uma ordem específica
    # Usaremos OrderedDict para garantir que a ordem seja mantida no CSV
    campos_ordenados_pf = OrderedDict([
        ('nome_completo', "Nome Completo"),
        ('cpf', "CPF"),
        ('data_nascimento', "Data de Nascimento"),
        ('estado_civil', "Estado Civil"),
        ('nacionalidade', "Nacionalidade"),
        ('nome_mae', "Nome da Mãe"),
        ('email', "Email"),
        ('tel_celular', "Telefone Celular"),
        ('tel_comercial', "Telefone Comercial"),
        ('rg', "RG"),
        ('orgao_emissor', "Órgão Emissor RG"),
        ('data_emissao_rg', "Data Emissão RG"),
        ('placa_carro', "Placa do Carro"),
        ('modelo_carro', "Modelo do Carro"),
        ('cor_carro', "Cor do Carro"),
        ('ano_carro', "Ano do Carro"),
        ('cep', "CEP"),
        ('endereco', "Endereço"),
        ('numero', "Número"),
        ('complemento', "Complemento"),
        ('bairro', "Bairro"),
        ('cidade', "Cidade"),
        ('estado', "Estado (UF)"),
        ('forma_pagamento', "Forma de Pagamento"),
        ('melhor_data_pagamento', "Melhor Data para Pagamento"),
        ('aceite_termos', "Aceitou os Termos"),
        ('documento_anexo_nome', "Nome do Arquivo do Documento Anexado")
    ])

    campos_ordenados_pj = OrderedDict([
        ('razao_social', "Razão Social"),
        ('nome_fantasia', "Nome Fantasia"),
        ('cnpj', "CNPJ"),
        ('data_abertura', "Data de Abertura"),
        ('inscricao_estadual', "Inscrição Estadual"),
        ('ramo_atividade', "Ramo de Atividade"),
        ('email_empresa', "Email da Empresa"),
        ('tel_comercial_empresa', "Telefone Comercial Empresa"),
        ('tel_celular_contato', "Telefone Celular Contato"),
        ('placa_carro_pj', "Placa do Carro (PJ)"),
        ('modelo_carro_pj', "Modelo do Carro (PJ)"),
        ('cor_carro_pj', "Cor do Carro (PJ)"),
        ('ano_carro_pj', "Ano do Carro (PJ)"),
        ('cep_empresa', "CEP Empresa"),
        ('endereco_empresa', "Endereço Empresa"),
        ('numero_empresa', "Número Empresa"),
        ('complemento_empresa', "Complemento Empresa"),
        ('bairro_empresa', "Bairro Empresa"),
        ('cidade_empresa', "Cidade Empresa"),
        ('estado_empresa', "Estado Empresa (UF)"),
        ('forma_pagamento_pj', "Forma de Pagamento (PJ)"),
        ('melhor_data_pagamento_pj', "Melhor Data para Pagamento (PJ)"),
        ('aceite_termos_pj', "Aceitou os Termos (PJ)"),
        ('documento_anexo_pj_nome', "Nome do Arquivo do Documento Anexado (PJ)")
    ])

    campos_a_iterar = None
    if tipo_pessoa == 'pf':
        campos_a_iterar = campos_ordenados_pf
    elif tipo_pessoa == 'pj':
        campos_a_iterar = campos_ordenados_pj
    else:
        app.logger.error(f"Tentativa de gerar CSV para tipo_pessoa desconhecido: {tipo_pessoa}")
        return None

    # Escrever cada campo e seu valor em uma nova linha
    for chave_campo, rotulo_campo in campos_a_iterar.items():
        valor = dados_formulario.get(chave_campo, '') # Pega o valor do formulário
        # Tratamento especial para o aceite_termos para ser mais legível
        if chave_campo in ['aceite_termos', 'aceite_termos_pj']:
            valor = 'Sim' if valor == 'sim' else 'Não'
        # Tratamento para melhor_data_pagamento
        if chave_campo in ['melhor_data_pagamento', 'melhor_data_pagamento_pj'] and valor:
            valor = f"Dia {valor}"

        writer.writerow([rotulo_campo, valor])
    
    csv_string = output.getvalue()
    output.close()
    return csv_string
# -----------------------------------------

# --- ROTAS DO SITE INSTITUCIONAL ---
@app.route('/')
def home(): # Renomeado de index para home para clareza
    return render_template('home.html', page_title="CLA Rastreamento - Segurança e Monitoramento Veicular")

@app.route('/sobre-nos')
def sobre_nos():
    return render_template('sobre.html', page_title="Sobre Nós - CLA Rastreamento")

@app.route('/servicos')
def servicos():
    return render_template('servicos.html', page_title="Nossos Serviços - CLA Rastreamento")

@app.route('/contato')
def contato():
    return render_template('contato.html', page_title="Contato - CLA Rastreamento")

@app.route('/cadastro') # Nova rota para a seleção PF/PJ
def index(): 
    return render_template('index.html') # Novo nome do template de seleção

# --- ROTAS DO FORMULÁRIO DE CADASTRO ---
@app.route('/cadastro_pf', methods=['GET'])
def cadastro_pf():
    return render_template('form_pf.html', form_data=None) # Passa form_data=None para evitar erro no primeiro GET

@app.route('/enviar_cadastro_pf', methods=['POST'])
def enviar_cadastro_pf():
    form_data = request.form.to_dict()
    errors = []
    anexo_salvo_path = None

    required_fields_pf = {
        'nome_completo': "Nome completo", 'cpf': "CPF", 'data_nascimento': "Data de nascimento",
        'estado_civil': "Estado civil", 'email': "Email", 'confirme_email': "Confirmação de Email",
        'tel_celular': "Telefone celular", 'rg': "RG", 'orgao_emissor': "Órgão emissor",
        'data_emissao_rg': "Data de emissão RG", 'nacionalidade': "Nacionalidade",
        'nome_mae': "Nome da mãe",
        'placa_carro': "Placa do carro", 'modelo_carro': "Modelo do carro",
        'cor_carro': "Cor do carro", 'ano_carro': "Ano do carro", 'cep': "CEP",
        'endereco': "Endereço", 'numero': "Número", 'bairro': "Bairro",
        'cidade': "Cidade", 'estado': "Estado",
        'forma_pagamento': "Forma de pagamento",
        'melhor_data_pagamento': "Melhor data para pagamento",
        'aceite_termos': "Aceite dos termos contratuais"
    }

    for field, label in required_fields_pf.items():
        if field == 'aceite_termos':
            if not form_data.get(field) == 'sim':
                errors.append(f"Você deve aceitar os {label.lower()}.")
        elif not form_data.get(field):
            errors.append(f"{label} é obrigatório.")

    if form_data.get('cpf') and not is_valid_cpf(form_data['cpf']): errors.append("CPF inválido.")
    if form_data.get('data_nascimento') and not is_valid_date(form_data['data_nascimento']): errors.append("Data de nascimento inválida.")
    if form_data.get('email') and form_data.get('confirme_email') and form_data['email'] != form_data['confirme_email']:
        errors.append("Os emails não correspondem.")
    if form_data.get('data_emissao_rg') and not is_valid_date(form_data['data_emissao_rg']): errors.append("Data de emissão do RG inválida.")
    if form_data.get('remuneracao') and form_data.get('remuneracao') != '':
        try:
            float(form_data['remuneracao'])
        except ValueError:
            errors.append("Remuneração deve ser um número.")
    if form_data.get('placa_carro') and not is_valid_placa(form_data['placa_carro']): errors.append("Placa do carro inválida.")
    if form_data.get('ano_carro') and not is_valid_year(form_data['ano_carro']): errors.append("Ano do carro inválido.")

    if 'documento_anexo' not in request.files or not request.files['documento_anexo'].filename:
        errors.append('O anexo do documento (RG ou CNH) é obrigatório.')
    else:
        file = request.files['documento_anexo']
        if allowed_file(file.filename):
            original_filename = secure_filename(file.filename)
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S%f")
            unique_filename = f"pf_{timestamp}_{original_filename}"
            anexo_salvo_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
            try:
                file.save(anexo_salvo_path)
                form_data['documento_anexo_nome'] = unique_filename
                app.logger.info(f"Arquivo PF {unique_filename} salvo em {anexo_salvo_path}")
            except Exception as e_save:
                app.logger.error(f"Erro ao salvar o arquivo PF {unique_filename}: {e_save}", exc_info=True)
                errors.append("Erro ao processar o anexo do documento.")
                anexo_salvo_path = None
        else:
            errors.append('Tipo de arquivo do documento não permitido. Use PDF, JPG ou PNG.')

    if errors:
        for error in errors:
            flash(error, 'danger')
        if anexo_salvo_path and os.path.exists(anexo_salvo_path):
            try: os.remove(anexo_salvo_path); app.logger.info(f"Anexo PF {anexo_salvo_path} removido devido a erros.")
            except Exception as e_del_err: app.logger.error(f"Erro ao remover anexo PF {anexo_salvo_path} após erro: {e_del_err}")
        return render_template('form_pf.html', form_data=form_data)

    conteudo_csv_pf = gerar_conteudo_csv(form_data, 'pf')
    nome_arquivo_csv_pf = f"cadastro_pf_{form_data.get('cpf', 'sem_cpf').replace('.', '').replace('-', '')}_{datetime.now().strftime('%Y%m%d%H%M')}.csv"

    if enviar_email_cadastro_geral(form_data, 'pf', 
                                   anexo_doc_path=anexo_salvo_path, 
                                   csv_filename=nome_arquivo_csv_pf, 
                                   csv_content=conteudo_csv_pf):
        flash('Cadastro enviado com sucesso! Em breve entraremos em contato.', 'success')
        return redirect(url_for('sucesso'))
    else:
        return render_template('form_pf.html', form_data=form_data)


@app.route('/cadastro_pj', methods=['GET'])
def cadastro_pj():
    return render_template('form_pj.html', form_data=None) # Passa form_data=None para evitar erro no primeiro GET

@app.route('/enviar_cadastro_pj', methods=['POST'])
def enviar_cadastro_pj():
    form_data = request.form.to_dict()
    errors = []
    anexo_salvo_path_pj = None

    required_fields_pj = {
        'razao_social': "Razão Social", 'cnpj': "CNPJ", 'data_abertura': "Data de abertura",
        'ramo_atividade': "Ramo de atividade", 'email_empresa': "Email da empresa",
        'confirme_email_empresa': "Confirmação de Email da empresa",
        'tel_comercial_empresa': "Telefone comercial", 
        'placa_carro_pj': "Placa do carro", 'modelo_carro_pj': "Modelo do carro",
        'cor_carro_pj': "Cor do carro", 'ano_carro_pj': "Ano do carro",
        'cep_empresa': "CEP", 'endereco_empresa': "Endereço", 'numero_empresa': "Número",
        'bairro_empresa': "Bairro", 'cidade_empresa': "Cidade", 'estado_empresa': "Estado",
        'forma_pagamento_pj': "Forma de pagamento", # Ajuste o nome se for diferente no HTML
        'melhor_data_pagamento_pj': "Melhor data para pagamento", # Ajuste o nome
        'aceite_termos_pj': "Aceite dos termos contratuais" # Ajuste o nome
    }

    for field, label in required_fields_pj.items():
        if field == 'aceite_termos_pj':
            if not form_data.get(field) == 'sim':
                errors.append(f"Você deve aceitar os {label.lower()}.")
        elif not form_data.get(field):
            errors.append(f"{label} é obrigatório.")

    if form_data.get('cnpj') and not is_valid_cnpj(form_data['cnpj']): errors.append("CNPJ inválido.")
    if form_data.get('data_abertura') and not is_valid_date(form_data['data_abertura']): errors.append("Data de abertura inválida.")
    if form_data.get('email_empresa') and form_data.get('confirme_email_empresa') and form_data['email_empresa'] != form_data['confirme_email_empresa']:
        errors.append("Os emails da empresa não correspondem.")
    if form_data.get('placa_carro_pj') and not is_valid_placa(form_data['placa_carro_pj']): errors.append("Placa do carro (PJ) inválida.")
    if form_data.get('ano_carro_pj') and not is_valid_year(form_data['ano_carro_pj']): errors.append("Ano do carro (PJ) inválido.")


    if 'documento_anexo_pj' not in request.files or not request.files['documento_anexo_pj'].filename:
        errors.append('O anexo do documento da empresa é obrigatório.')
    else:
        file_pj = request.files['documento_anexo_pj']
        if allowed_file(file_pj.filename):
            original_filename_pj = secure_filename(file_pj.filename)
            timestamp_pj = datetime.now().strftime("%Y%m%d%H%M%S%f")
            unique_filename_pj = f"pj_{timestamp_pj}_{original_filename_pj}"
            anexo_salvo_path_pj = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename_pj)
            try:
                file_pj.save(anexo_salvo_path_pj)
                form_data['documento_anexo_pj_nome'] = unique_filename_pj
                app.logger.info(f"Arquivo PJ {unique_filename_pj} salvo em {anexo_salvo_path_pj}")
            except Exception as e_save_pj:
                app.logger.error(f"Erro ao salvar o arquivo PJ {unique_filename_pj}: {e_save_pj}", exc_info=True)
                errors.append("Erro ao processar o anexo do documento da empresa.")
                anexo_salvo_path_pj = None
        else:
            errors.append('Tipo de arquivo do documento da empresa não permitido. Use PDF, JPG ou PNG.')

    if errors:
        for error in errors:
            flash(error, 'danger')
        if anexo_salvo_path_pj and os.path.exists(anexo_salvo_path_pj):
            try: os.remove(anexo_salvo_path_pj); app.logger.info(f"Anexo PJ {anexo_salvo_path_pj} removido devido a erros.")
            except Exception as e_del_err_pj: app.logger.error(f"Erro ao remover anexo PJ {anexo_salvo_path_pj} após erro: {e_del_err_pj}")
        return render_template('form_pj.html', form_data=form_data)

    conteudo_csv_pj = gerar_conteudo_csv(form_data, 'pj')
    nome_arquivo_csv_pj = f"cadastro_pj_{form_data.get('cnpj', 'sem_cnpj').replace('.', '').replace('/', '').replace('-', '')}_{datetime.now().strftime('%Y%m%d%H%M')}.csv"

    if enviar_email_cadastro_geral(form_data, 'pj', 
                                   anexo_doc_path=anexo_salvo_path_pj, 
                                   csv_filename=nome_arquivo_csv_pj, 
                                   csv_content=conteudo_csv_pj):
        flash('Cadastro enviado com sucesso! Em breve entraremos em contato.', 'success')
        return redirect(url_for('sucesso'))
    else:
        return render_template('form_pj.html', form_data=form_data)

@app.route('/sucesso')
def sucesso():
    return render_template('success.html')

@app.errorhandler(404)
def page_not_found(e):
    app.logger.warning(f"Recurso não encontrado (404): {request.url} - Erro: {e}")
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    app.logger.error(f"Erro interno do servidor (500): {request.url} - Erro: {e}", exc_info=True)
    return render_template('500.html'), 500

if __name__ == '__main__':

    pass