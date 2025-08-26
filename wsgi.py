#!/usr/bin/env python3
"""
WSGI entry point for Sixty Demo
Configurado para deploy no Hostinger
"""

import os
import sys

# Adicionar o diretório atual ao path
sys.path.insert(0, os.path.dirname(__file__))

# Configurar variáveis de ambiente
os.environ['FLASK_ENV'] = 'production'
os.environ['GEMINI_API_KEY'] = 'AIzaSyBBC9-59-z_n1AXf1i3Rg9KCf_UPj_YGx8'

# Importar a aplicação Flask
from app import app

# Configurações para produção
app.config['DEBUG'] = False
app.config['TESTING'] = False

# Configurar CORS para produção
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

if __name__ == "__main__":
    # Para desenvolvimento local
    app.run(host='0.0.0.0', port=8080, debug=False)
else:
    # Para produção (Hostinger)
    application = app
