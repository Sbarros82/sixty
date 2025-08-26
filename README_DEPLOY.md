# 🚀 Sixty Demo - Deploy no Hostinger

## 📦 Arquivos Preparados para Deploy

Todos os arquivos necessários para o deploy no Hostinger foram criados:

### ✅ Arquivos Principais
- `app.py` - Aplicação Flask principal
- `wsgi.py` - Entry point para produção
- `requirements.txt` - Dependências Python
- `gunicorn.conf.py` - Configuração do Gunicorn

### ✅ Configurações de Servidor
- `.htaccess` - Configuração Apache
- `start_production.sh` - Script de inicialização
- `deploy_hostinger.md` - Guia completo de deploy

## 🎯 Opções de Deploy

### 1. **VPS Hostinger (Recomendado)**
- Melhor performance
- Controle total
- Suporte a processamento de vídeo

### 2. **cPanel Hostinger**
- Mais simples
- Limitações de recursos
- Adequado para testes

## 🚀 Deploy Rápido

### Passo 1: Escolher Plano
- **VPS**: Recomendado para produção
- **Shared**: Adequado para testes

### Passo 2: Upload de Arquivos
1. Fazer upload de todos os arquivos para o servidor
2. Via FTP ou File Manager do cPanel

### Passo 3: Configurar Ambiente
```bash
# VPS Hostinger
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# cPanel Hostinger
pip install -r requirements.txt
```

### Passo 4: Iniciar Aplicação
```bash
# VPS
./start_production.sh

# cPanel
python wsgi.py
```

## 🔧 Configurações Importantes

### Variáveis de Ambiente
- `GEMINI_API_KEY`: Já configurada
- `FLASK_ENV`: production
- `SECRET_KEY`: Gerada automaticamente

### Dependências do Sistema
- **FFmpeg**: Essencial para processamento de vídeo
- **Python 3.11+**: Versão mínima
- **Gunicorn**: Servidor WSGI para produção

## 📊 Recursos Necessários

### Mínimos (Teste)
- **RAM**: 1GB
- **CPU**: 1 core
- **Storage**: 10GB
- **Bandwidth**: 1TB/mês

### Recomendados (Produção)
- **RAM**: 4GB+
- **CPU**: 2+ cores
- **Storage**: 50GB+
- **Bandwidth**: 5TB+/mês

## ⚠️ Limitações

1. **Processamento de vídeo** pode ser lento em planos compartilhados
2. **Timeout** de 300s para processamento
3. **Armazenamento** limitado para vídeos grandes
4. **Recursos** compartilhados em planos básicos

## 💡 Otimizações

1. **Usar VPS** para melhor performance
2. **Configurar CDN** para arquivos estáticos
3. **Implementar fila** para processamento assíncrono
4. **Limpar arquivos** temporários regularmente

## 🆘 Suporte

### Problemas Comuns
1. **FFmpeg não encontrado**: Instalar via package manager
2. **Erro de permissão**: Ajustar permissões dos arquivos
3. **Timeout**: Aumentar timeout no Gunicorn
4. **Memória insuficiente**: Reduzir workers do Gunicorn

### Logs
```bash
# VPS
sudo journalctl -u sixty-demo -f

# cPanel
tail -f error_log
```

## 🌐 URLs de Acesso

Após o deploy, a aplicação estará disponível em:
- **VPS**: `http://seu-ip:8000` ou `https://seu-dominio.com`
- **cPanel**: `https://seu-dominio.com/sixty-demo`

## ✅ Checklist de Deploy

- [ ] Upload de todos os arquivos
- [ ] Instalação das dependências
- [ ] Configuração do FFmpeg
- [ ] Configuração do Gunicorn
- [ ] Configuração do Nginx/Apache
- [ ] Configuração do SSL/HTTPS
- [ ] Teste da aplicação
- [ ] Configuração de backup
- [ ] Monitoramento de logs

## 🎉 Pronto para Usar!

Após seguir o guia completo em `deploy_hostinger.md`, sua aplicação estará pronta para processar vídeos do YouTube e criar cortes automáticos com legendas sincronizadas!
