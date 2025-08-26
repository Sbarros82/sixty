# 🚀 Deploy Sixty Demo no Hostinger

## 📋 Pré-requisitos

1. **Conta Hostinger** com suporte a Python
2. **Acesso SSH** (recomendado) ou **cPanel**
3. **Domínio** configurado

## 🔧 Opções de Deploy

### Opção 1: VPS Hostinger (Recomendado)

#### 1. Conectar via SSH
```bash
ssh root@seu-ip-do-vps
```

#### 2. Instalar dependências do sistema
```bash
# Atualizar sistema
apt update && apt upgrade -y

# Instalar Python 3.11+
apt install python3 python3-pip python3-venv -y

# Instalar FFmpeg (essencial para processamento de vídeo)
apt install ffmpeg -y

# Instalar dependências do sistema
apt install build-essential libssl-dev libffi-dev python3-dev -y
```

#### 3. Configurar ambiente
```bash
# Criar usuário para a aplicação
adduser sixty
usermod -aG sudo sixty

# Mudar para o usuário
su - sixty

# Criar diretório da aplicação
mkdir -p /home/sixty/sixty-demo
cd /home/sixty/sixty-demo
```

#### 4. Fazer upload dos arquivos
```bash
# Via SCP (do seu computador)
scp -r saas_demo/* sixty@seu-ip:/home/sixty/sixty-demo/

# Ou via Git
git clone https://github.com/seu-repo/sixty-demo.git
```

#### 5. Configurar ambiente Python
```bash
# Criar ambiente virtual
python3 -m venv venv
source venv/bin/activate

# Instalar dependências
pip install -r requirements.txt

# Instalar Gunicorn
pip install gunicorn
```

#### 6. Configurar Gunicorn
```bash
# Criar arquivo de configuração
cat > gunicorn.conf.py << EOF
bind = "0.0.0.0:8000"
workers = 4
worker_class = "sync"
worker_connections = 1000
timeout = 300
keepalive = 2
max_requests = 1000
max_requests_jitter = 100
preload_app = True
EOF
```

#### 7. Configurar Systemd
```bash
# Criar serviço
sudo tee /etc/systemd/system/sixty-demo.service << EOF
[Unit]
Description=Sixty Demo
After=network.target

[Service]
User=sixty
Group=sixty
WorkingDirectory=/home/sixty/sixty-demo
Environment="PATH=/home/sixty/sixty-demo/venv/bin"
ExecStart=/home/sixty/sixty-demo/venv/bin/gunicorn -c gunicorn.conf.py wsgi:application
ExecReload=/bin/kill -s HUP \$MAINPID
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# Ativar serviço
sudo systemctl daemon-reload
sudo systemctl enable sixty-demo
sudo systemctl start sixty-demo
```

#### 8. Configurar Nginx
```bash
# Instalar Nginx
sudo apt install nginx -y

# Configurar site
sudo tee /etc/nginx/sites-available/sixty-demo << EOF
server {
    listen 80;
    server_name seu-dominio.com www.seu-dominio.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    location /static/ {
        alias /home/sixty/sixty-demo/static/;
        expires 1M;
        add_header Cache-Control "public, immutable";
    }

    location /uploads/ {
        alias /home/sixty/sixty-demo/uploads/;
    }

    location /output/ {
        alias /home/sixty/sixty-demo/output/;
    }

    # Configurações para upload de arquivos grandes
    client_max_body_size 500M;
    proxy_read_timeout 300s;
    proxy_connect_timeout 300s;
    proxy_send_timeout 300s;
}
EOF

# Ativar site
sudo ln -s /etc/nginx/sites-available/sixty-demo /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### Opção 2: cPanel Hostinger

#### 1. Acessar cPanel
- Login no cPanel do Hostinger
- Ir para "Python Apps"

#### 2. Criar aplicação Python
- Clicar em "Create Application"
- Escolher Python 3.11+
- Definir domínio/subdomínio
- Escolher diretório: `public_html/sixty-demo`

#### 3. Fazer upload dos arquivos
- Usar File Manager ou FTP
- Upload de todos os arquivos para `public_html/sixty-demo/`

#### 4. Configurar WSGI
- O arquivo `wsgi.py` já está configurado
- O `.htaccess` redireciona para o WSGI

#### 5. Instalar dependências
```bash
# Via SSH ou Terminal do cPanel
cd public_html/sixty-demo
pip install -r requirements.txt
```

## 🔒 Configurações de Segurança

### 1. Firewall
```bash
# Configurar UFW
sudo ufw allow 22
sudo ufw allow 80
sudo ufw allow 443
sudo ufw enable
```

### 2. SSL/HTTPS
```bash
# Instalar Certbot
sudo apt install certbot python3-certbot-nginx -y

# Obter certificado
sudo certbot --nginx -d seu-dominio.com -d www.seu-dominio.com
```

### 3. Variáveis de Ambiente
```bash
# Criar arquivo .env
cat > .env << EOF
FLASK_ENV=production
GEMINI_API_KEY=AIzaSyBBC9-59-z_n1AXf1i3Rg9KCf_UPj_YGx8
SECRET_KEY=sua-chave-secreta-aqui
EOF
```

## 📁 Estrutura de Arquivos

```
sixty-demo/
├── app.py                 # Aplicação principal
├── wsgi.py               # Entry point para produção
├── requirements.txt      # Dependências Python
├── .htaccess            # Configuração Apache
├── static/              # Arquivos estáticos
├── templates/           # Templates HTML
├── services/            # Serviços da aplicação
├── uploads/             # Uploads temporários
├── output/              # Vídeos processados
└── venv/                # Ambiente virtual
```

## 🚀 Comandos Úteis

### Verificar status
```bash
sudo systemctl status sixty-demo
sudo systemctl status nginx
```

### Logs
```bash
sudo journalctl -u sixty-demo -f
sudo tail -f /var/log/nginx/error.log
```

### Reiniciar serviços
```bash
sudo systemctl restart sixty-demo
sudo systemctl restart nginx
```

### Atualizar aplicação
```bash
cd /home/sixty/sixty-demo
git pull
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart sixty-demo
```

## ⚠️ Limitações do Hostinger

1. **Recursos limitados** em planos compartilhados
2. **Processamento de vídeo** pode ser lento
3. **Armazenamento** limitado para vídeos
4. **Timeout** de 300s para processamento

## 💡 Otimizações

1. **Usar VPS** para melhor performance
2. **Configurar CDN** para arquivos estáticos
3. **Implementar fila** para processamento assíncrono
4. **Limpar arquivos** temporários regularmente

## 🆘 Troubleshooting

### Erro 500
```bash
# Verificar logs
sudo journalctl -u sixty-demo -n 50
```

### Erro de permissão
```bash
# Corrigir permissões
sudo chown -R sixty:sixty /home/sixty/sixty-demo
sudo chmod -R 755 /home/sixty/sixty-demo
```

### FFmpeg não encontrado
```bash
# Instalar FFmpeg
sudo apt install ffmpeg -y
```

### Memória insuficiente
```bash
# Ajustar workers do Gunicorn
# Editar gunicorn.conf.py
workers = 2  # Reduzir número de workers
```
