# Configuração do Gunicorn para Sixty Demo
# Otimizado para produção no Hostinger

# Configurações básicas
bind = "0.0.0.0:8000"
workers = 4
worker_class = "sync"
worker_connections = 1000

# Timeouts (importante para processamento de vídeo)
timeout = 300
keepalive = 2
graceful_timeout = 30

# Configurações de performance
max_requests = 1000
max_requests_jitter = 100
preload_app = True

# Configurações de logging
accesslog = "-"
errorlog = "-"
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Configurações de segurança
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190

# Configurações para upload de arquivos grandes
max_requests_jitter = 100
worker_tmp_dir = "/dev/shm"

# Configurações específicas para processamento de vídeo
worker_connections = 1000
backlog = 2048

# Configurações de ambiente
raw_env = [
    "FLASK_ENV=production",
    "GEMINI_API_KEY=AIzaSyBBC9-59-z_n1AXf1i3Rg9KCf_UPj_YGx8",
]

# Configurações de debug (desabilitar em produção)
reload = False
reload_engine = "auto"
reload_extra_files = []

# Configurações de SSL (se necessário)
# keyfile = "/path/to/keyfile"
# certfile = "/path/to/certfile"

# Configurações de proxy
forwarded_allow_ips = "*"
secure_scheme_headers = {
    'X-FORWARDED-PROTOCOL': 'ssl',
    'X-FORWARDED-PROTO': 'https',
    'X-FORWARDED-SSL': 'on'
}
