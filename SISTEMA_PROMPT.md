# 🎯 SISTEMA SIXTY DEMO - PROMPT COMPLETO

## 📋 **VISÃO GERAL DO SISTEMA**

O **Sixty Demo** é uma aplicação web de processamento inteligente de vídeos que automatiza a criação de cortes otimizados para redes sociais, com legendas sincronizadas e análise de IA.

### 🎯 **Objetivo Principal**
Criar cortes automáticos de vídeos do YouTube ou uploads locais, com legendas embutidas e formatação otimizada para plataformas como TikTok, Instagram e YouTube Shorts.

---

## ⚙️ **FUNCIONALIDADES PRINCIPAIS**

### 1. **Entrada de Vídeo**
- ✅ **Upload de arquivo local** (MP4, MOV, AVI)
- ✅ **Link do YouTube** (download automático via yt-dlp)
- ✅ **Conversão automática** para MP4
- ✅ **Validação de formato** e tamanho

### 2. **Seleção de Cortes**
- ✅ **Durações fixas**: 15s, 30s, 60s
- ✅ **Cálculo automático** de número de cortes
- ✅ **Variações inteligentes** (cortes diferentes a cada processamento)
- ✅ **Adaptação** ao tamanho do vídeo original

### 3. **Processamento por IA**
- ✅ **Transcrição automática** (Whisper)
- ✅ **Análise de conteúdo** (Google Gemini)
- ✅ **Identificação de momentos importantes**
- ✅ **Geração de legendas** sincronizadas

### 4. **Sistema de Legendas**
- ✅ **Transcrição precisa** com timestamps
- ✅ **Sincronização** com fala dos personagens
- ✅ **Efeito "typing"** (aparecem e desaparecem)
- ✅ **Posicionamento** na parte inferior
- ✅ **Fonte 11**, até 3 linhas
- ✅ **Estilo profissional** com fundo semi-transparente

### 5. **Formatação de Vídeo**
- ✅ **Aspect ratio 9:16** (1080x1920)
- ✅ **Formato MP4** (H.264)
- ✅ **Áudio AAC**
- ✅ **Legendas embutidas** no vídeo
- ✅ **Otimizado** para redes sociais

---

## 🏗️ **ARQUITETURA TÉCNICA**

### **Backend (Flask)**
```python
# Estrutura principal
app.py                    # Aplicação Flask
wsgi.py                   # Entry point para produção
services/video_processor.py  # Lógica de processamento
```

### **Frontend (HTML + Bootstrap)**
```html
templates/index.html      # Interface principal
static/style.css          # Estilos responsivos
static/script.js          # Interações JavaScript
```

### **Dependências Principais**
- **Flask 3.0.0** - Framework web
- **yt-dlp 2025.8.22** - Download YouTube
- **openai-whisper** - Transcrição de áudio
- **google-generativeai** - Análise de IA
- **ffmpeg-python** - Processamento de vídeo
- **gunicorn** - Servidor WSGI para produção

---

## 🔄 **FLUXO DE PROCESSAMENTO**

### **1. Recepção do Vídeo**
```
Usuário → Upload/URL → Validação → Download (se YouTube)
```

### **2. Análise e Corte**
```
Vídeo → Análise de duração → Cálculo de cortes → Geração de pontos de início
```

### **3. Processamento Individual**
```
Corte → Transcrição → Análise IA → Geração de legendas → Formatação final
```

### **4. Saída**
```
Vídeo processado → Preview → Download → Limpeza de arquivos temporários
```

---

## 🎨 **CARACTERÍSTICAS DE DESIGN**

### **Interface**
- ✅ **Design responsivo** (mobile-first)
- ✅ **Tema profissional** (fundo branco, painéis organizados)
- ✅ **Feedback visual** (progress bars, status)
- ✅ **Preview embutido** (vídeo direto na tela)
- ✅ **Informações de formato** (especificações técnicas)

### **Experiência do Usuário**
- ✅ **Upload drag & drop**
- ✅ **Progresso em tempo real**
- ✅ **Múltiplos cortes** visíveis simultaneamente
- ✅ **Download individual** por corte
- ✅ **Informações detalhadas** de cada corte

---

## 🧠 **SISTEMA DE IA**

### **Whisper (Transcrição)**
- **Modelo**: Local (sem necessidade de API)
- **Configuração**: `word_timestamps=True`
- **Precisão**: Alta para português
- **Output**: Timestamps precisos por segmento

### **Gemini (Análise)**
- **Modelo**: `gemini-1.5-flash`
- **Função**: Identificação de momentos importantes
- **API Key**: Configurada automaticamente
- **Fallback**: Modo demo se API indisponível

---

## 📊 **SISTEMA DE VARIAÇÕES**

### **Estratégias de Corte**
1. **Variação Simples** (vídeos < 10 min)
   - Padrão linear com pequenas variações
   
2. **Variação Média** (10-30 min)
   - Distribuição exponencial
   - Agrupamentos inteligentes
   
3. **Variação Avançada** (> 30 min)
   - Múltiplos padrões combinados
   - Distribuição uniforme
   - Clusters de interesse

### **Contador de Processamento**
- **Arquivo**: `processing_counters.json`
- **Identificação**: Nome + tamanho do arquivo
- **Seed**: `processing_count + 42` para variações consistentes

---

## 🎬 **ESPECIFICAÇÕES DE VÍDEO**

### **Entrada**
- **Formatos**: MP4, MOV, AVI
- **Tamanho máximo**: 500MB
- **Duração**: Sem limite
- **Qualidade**: Até 720p (YouTube)

### **Saída**
- **Formato**: MP4 (H.264)
- **Resolução**: 1080x1920 (9:16)
- **Áudio**: AAC, 128kbps
- **Legendas**: ASS embutidas
- **Qualidade**: Otimizada para redes sociais

### **Legendas**
- **Fonte**: Arial, tamanho 11
- **Posição**: Inferior, 80px da borda
- **Máximo**: 3 linhas, 25 caracteres/linha
- **Estilo**: Fundo semi-transparente, contorno fino
- **Sincronização**: Precisão de milissegundos

---

## 🔧 **CONFIGURAÇÕES TÉCNICAS**

### **FFmpeg (Processamento)**
```bash
# Corte de vídeo
ffmpeg -i input.mp4 -ss START -t DURATION -c copy cut.mp4

# Formatação 9:16
ffmpeg -i cut.mp4 -vf "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2" -c:a aac -b:a 128k formatted.mp4

# Embutir legendas
ffmpeg -i formatted.mp4 -vf "ass=subtitles.ass" -c:a copy final.mp4
```

### **Gunicorn (Produção)**
```python
# Configurações otimizadas
bind = "0.0.0.0:8000"
workers = 4
timeout = 300  # 5 minutos para processamento
max_requests = 1000
```

---

## 🚀 **DEPLOY E INFRAESTRUTURA**

### **Requisitos Mínimos**
- **RAM**: 1GB
- **CPU**: 1 core
- **Storage**: 10GB
- **Python**: 3.11+
- **FFmpeg**: Instalado no sistema

### **Requisitos Recomendados**
- **RAM**: 4GB+
- **CPU**: 2+ cores
- **Storage**: 50GB+
- **Bandwidth**: 5TB+/mês

### **Plataformas Suportadas**
- ✅ **VPS Hostinger** (recomendado)
- ✅ **cPanel Hostinger**
- ✅ **Qualquer servidor Linux**
- ✅ **Docker** (configuração adicional)

---

## 🔒 **SEGURANÇA E LIMITAÇÕES**

### **Segurança**
- ✅ **Validação de entrada** rigorosa
- ✅ **Limite de tamanho** de arquivo
- ✅ **Timeout** de processamento
- ✅ **Limpeza** de arquivos temporários
- ✅ **CORS** configurado

### **Limitações**
- ⚠️ **Processamento sequencial** (não paralelo)
- ⚠️ **Timeout** de 300s por vídeo
- ⚠️ **Armazenamento** limitado
- ⚠️ **Recursos** dependem do servidor

---

## 📈 **MÉTRICAS E PERFORMANCE**

### **Tempos de Processamento**
- **Vídeo 1 min**: ~30-60s
- **Vídeo 5 min**: ~2-3 min
- **Vídeo 10 min**: ~5-7 min
- **Vídeo 30 min**: ~15-20 min

### **Qualidade de Saída**
- **Legendas**: 95%+ precisão
- **Sincronização**: ±100ms
- **Formato**: 100% compatível
- **Qualidade**: Otimizada para redes sociais

---

## 🛠️ **MANUTENÇÃO E MONITORAMENTO**

### **Logs**
- **Aplicação**: stdout/stderr
- **Gunicorn**: access.log, error.log
- **Sistema**: journalctl (VPS)

### **Limpeza**
- **Arquivos temporários**: Automática
- **Cache**: Semanal
- **Logs**: Rotação automática

### **Backup**
- **Código**: Git
- **Configurações**: Documentadas
- **Dados**: Não críticos (processamento temporário)

---

## 🎯 **CASOS DE USO**

### **Criadores de Conteúdo**
- ✅ **YouTube** → TikTok/Instagram
- ✅ **Podcasts** → Clips para redes sociais
- ✅ **Aulas** → Trechos educativos
- ✅ **Eventos** → Momentos destacados

### **Empresas**
- ✅ **Treinamentos** → Microlearning
- ✅ **Apresentações** → Clips promocionais
- ✅ **Eventos** → Highlights
- ✅ **Marketing** → Conteúdo para redes sociais

---

## 🔮 **ROADMAP FUTURO**

### **Melhorias Planejadas**
- 🔄 **Processamento paralelo**
- 🎵 **Detecção de música** (copyright)
- 🎨 **Filtros visuais** automáticos
- 📱 **App mobile** nativo
- 🌐 **API pública** para integração
- 💾 **Armazenamento em nuvem**
- 🎯 **Análise de engajamento**

### **Recursos Avançados**
- 🤖 **IA para thumbnails**
- 🎬 **Transições automáticas**
- 🎵 **Música de fundo** (royalty-free)
- 📊 **Analytics** de performance
- 🔗 **Integração** com redes sociais

---

## 📞 **SUPORTE E DOCUMENTAÇÃO**

### **Documentação**
- `deploy_hostinger.md` - Guia completo de deploy
- `README_DEPLOY.md` - Resumo rápido
- `SISTEMA_PROMPT.md` - Este documento

### **Troubleshooting**
- **FFmpeg não encontrado**: Instalar via package manager
- **Erro de permissão**: Ajustar permissões
- **Timeout**: Aumentar timeout no Gunicorn
- **Memória**: Reduzir workers

---

## 🎉 **CONCLUSÃO**

O **Sixty Demo** é uma solução completa e profissional para automatização de criação de conteúdo para redes sociais, combinando:

- ✅ **Tecnologia de ponta** (IA, processamento de vídeo)
- ✅ **Interface intuitiva** (design responsivo)
- ✅ **Performance otimizada** (configurações de produção)
- ✅ **Flexibilidade** (múltiplas fontes de vídeo)
- ✅ **Qualidade profissional** (formatação otimizada)

**Pronto para revolucionar a criação de conteúdo digital!** 🚀
