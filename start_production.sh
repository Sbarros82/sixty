#!/bin/bash

# Script para iniciar Sixty Demo em produção
# Usar: ./start_production.sh

echo "🚀 Iniciando Sixty Demo em produção..."

# Verificar se estamos no diretório correto
if [ ! -f "app.py" ]; then
    echo "❌ Erro: app.py não encontrado. Execute este script no diretório da aplicação."
    exit 1
fi

# Verificar se o ambiente virtual existe
if [ ! -d "venv" ]; then
    echo "📦 Criando ambiente virtual..."
    python3 -m venv venv
fi

# Ativar ambiente virtual
echo "🔧 Ativando ambiente virtual..."
source venv/bin/activate

# Instalar/atualizar dependências
echo "📥 Instalando dependências..."
pip install -r requirements.txt

# Verificar se FFmpeg está instalado
if ! command -v ffmpeg &> /dev/null; then
    echo "⚠️  FFmpeg não encontrado. Instalando..."
    if command -v apt &> /dev/null; then
        sudo apt update && sudo apt install ffmpeg -y
    elif command -v yum &> /dev/null; then
        sudo yum install ffmpeg -y
    else
        echo "❌ Não foi possível instalar FFmpeg automaticamente. Instale manualmente."
    fi
fi

# Criar diretórios necessários
echo "📁 Criando diretórios..."
mkdir -p uploads output static templates services

# Verificar se Gunicorn está instalado
if ! pip show gunicorn &> /dev/null; then
    echo "📦 Instalando Gunicorn..."
    pip install gunicorn
fi

# Configurar variáveis de ambiente
export FLASK_ENV=production
export GEMINI_API_KEY=AIzaSyBBC9-59-z_n1AXf1i3Rg9KCf_UPj_YGx8

# Iniciar aplicação com Gunicorn
echo "🌟 Iniciando aplicação com Gunicorn..."
echo "📍 Acesse: http://localhost:8000"
echo "🛑 Para parar: Ctrl+C"

gunicorn -c gunicorn.conf.py wsgi:application
