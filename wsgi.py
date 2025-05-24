from app import app  # Importa a instância 'app' do seu arquivo app.py

# if __name__ == "__main__":
#     # Estas configurações são para desenvolvimento local.
#     # O modo debug=True é útil para ver erros detalhados no navegador.
#     # Em produção, Gunicorn chamará a instância 'app' diretamente,
#     # e debug deve ser False.
#     app.run(host='0.0.0.0', port=5001, debug=True)