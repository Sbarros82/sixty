import os
import json
import uuid
from datetime import datetime
from flask import Flask, request, render_template, jsonify, send_file
from werkzeug.utils import secure_filename
import google.generativeai as genai
from services.video_processor import VideoProcessor
from services.prompt_generator import PromptGenerator
import yt_dlp
from demo_mode import enable_demo_mode

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024  # 500MB max
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['OUTPUT_FOLDER'] = 'output'
app.config['GEMINI_API_KEY'] = 'AIzaSyBBC9-59-z_n1AXf1i3Rg9KCf_UPj_YGx8'

# Configurar CORS para permitir requisições
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

# Configurar Gemini
genai.configure(api_key=app.config['GEMINI_API_KEY'])
model = genai.GenerativeModel('gemini-1.5-flash')

# Criar pastas necessárias
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)

ALLOWED_EXTENSIONS = {'mp4', 'mov', 'avi', 'mkv'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/test')
def test():
    """Rota de teste para verificar se o servidor está funcionando"""
    return jsonify({
        'status': 'ok',
        'message': 'Sixty está funcionando!',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/upload', methods=['POST'])
def upload_video():
    try:
        print("📥 Recebendo requisição de upload...")
        
        # Verificar se há arquivo enviado
        if 'video_file' in request.files:
            print("📁 Processando upload de arquivo...")
            return handle_file_upload(request)
        else:
            print("🌐 Processando upload via URL...")
            return handle_url_upload(request)
        
    except Exception as e:
        print(f"❌ Erro na rota upload: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Erro interno: {str(e)}'}), 500

def handle_file_upload(request):
    """Processa upload de arquivo de vídeo"""
    try:
        file = request.files['video_file']
        duration = int(request.form.get('duration', 30))
        template = request.form.get('template', 'youtube')
        
        if file.filename == '':
            return jsonify({'error': 'Nenhum arquivo selecionado'}), 400
        
        # Validar extensão
        allowed_extensions = {'mp4', 'mov', 'avi', 'mkv', 'webm'}
        if not file.filename.lower().endswith(tuple('.' + ext for ext in allowed_extensions)):
            return jsonify({'error': 'Formato de arquivo não suportado. Use: MP4, MOV, AVI, MKV, WEBM'}), 400
        
        # Validar duração
        if duration not in [15, 30, 60]:
            duration = 30
        
        print(f"Processando arquivo: {file.filename} com duração: {duration} e template: {template}")
        
        # Gerar ID único para o projeto
        project_id = str(uuid.uuid4())
        project_folder = os.path.join(app.config['OUTPUT_FOLDER'], project_id)
        os.makedirs(project_folder, exist_ok=True)
        
        # Salvar arquivo
        video_path = os.path.join(project_folder, secure_filename(file.filename))
        file.save(video_path)
        
        print(f"Arquivo salvo: {video_path}")
        
        # Processar vídeo com template escolhido
        processor = VideoProcessor(video_path, project_folder, model, template)
        result = processor.process_video(duration)
        
        if not result.get('success', False):
            return jsonify({'error': result.get('error', 'Erro no processamento')}), 500
        
        return jsonify({
            'success': True,
            'project_id': project_id,
            'cuts': result.get('cuts', []),
            'message': 'Vídeo processado com sucesso!'
        })
        
    except Exception as e:
        print(f"Erro no upload de arquivo: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Erro no upload: {str(e)}'}), 500

def handle_url_upload(request):
    """Processa upload via URL (YouTube ou demo)"""
    try:
        # Verificar se o conteúdo é JSON
        if not request.is_json:
            return jsonify({'error': 'Conteúdo deve ser JSON'}), 400
        
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Dados JSON inválidos'}), 400
        
        video_url = data.get('video_url', '').strip()
        duration = data.get('duration', 15)
        template = data.get('template', 'youtube')
        
        # Validar URL
        if not video_url:
            return jsonify({'error': 'URL do vídeo é obrigatória'}), 400
        
        # Validar duração
        if duration not in [15, 30, 60]:
            duration = 30
        
        print(f"Processando URL: {video_url} com duração: {duration} e template: {template}")
        
        # Gerar ID único para o projeto
        project_id = str(uuid.uuid4())
        project_folder = os.path.join(app.config['OUTPUT_FOLDER'], project_id)
        os.makedirs(project_folder, exist_ok=True)
        
        # Verificar se é modo demo
        demo_urls = ['demo', 'test', 'https://www.youtube.com/watch?v=demo', 'https://youtu.be/demo']
        is_demo = any(demo_url in video_url.lower() for demo_url in demo_urls)
        
        if is_demo:
            print("🎭 Ativando modo de demonstração...")
            DemoProcessor = enable_demo_mode()
            processor = DemoProcessor('demo_video.mp4', project_folder, model, template)
            result = processor.process_video(duration)
        else:
            # Validar URL do YouTube
            if not video_url.startswith('https://www.youtube.com/') and not video_url.startswith('https://youtu.be/'):
                return jsonify({'error': 'URL deve ser do YouTube ou use "demo" para modo de demonstração'}), 400
            
            # Download do vídeo do YouTube
            video_path = download_youtube_video(video_url, project_folder)
            
            if not video_path:
                return jsonify({'error': 'Erro ao baixar vídeo do YouTube. Tente fazer upload de um arquivo local.'}), 400
            
            # Processar vídeo com template escolhido
            processor = VideoProcessor(video_path, project_folder, model, template)
            result = processor.process_video(duration)
        
        if not result.get('success', False):
            return jsonify({'error': result.get('error', 'Erro no processamento')}), 500
        
        return jsonify({
            'success': True,
            'project_id': project_id,
            'cuts': result.get('cuts', []),
            'message': 'Vídeo processado com sucesso!'
        })
        
    except Exception as e:
        print(f"Erro no upload via URL: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Erro no processamento: {str(e)}'}), 500

def download_youtube_video(url, output_folder):
    """Download vídeo do YouTube usando yt-dlp, sempre convertendo para MP4"""
    try:
        print(f"Baixando vídeo: {url}")
        
        ydl_opts = {
            'format': 'bestvideo[ext=mp4][height<=720]+bestaudio[ext=m4a]/best[height<=720]',
            'outtmpl': os.path.join(output_folder, 'original_video.%(ext)s'),
            'quiet': False,  # Mostrar progresso
            'no_warnings': False,
            'ignoreerrors': False,
            'socket_timeout': 60,
            'retries': 10,
            'fragment_retries': 10,
            'http_chunk_size': 10485760,  # 10MB chunks
            'buffersize': 1024,
            'http_headers': {
                'User-Agent': (
                    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                    'AppleWebKit/537.36 (KHTML, like Gecko) '
                    'Chrome/120.0.0.0 Safari/537.36'
                )
            },
            'nocheckcertificate': True,
            'prefer_ffmpeg': True,
            'geo_bypass': True,
            'geo_bypass_country': 'US',
            # 🔑 Força conversão para MP4
            'postprocessors': [{
                'key': 'FFmpegVideoConvertor',
                'preferedformat': 'mp4',
            }],
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            print("Extraindo informações do vídeo...")
            info = ydl.extract_info(url, download=True)
            
            if not info:
                print("❌ Não foi possível extrair informações do vídeo")
                return None
            
            # Verifica o arquivo final gerado
            video_path = os.path.join(output_folder, 'original_video.mp4')
            
            if os.path.exists(video_path):
                print(f"✅ Vídeo baixado com sucesso: {video_path}")
                return video_path
            else:
                print("❌ Arquivo não encontrado após download")
                return None

    except Exception as e:
        print(f"Erro ao baixar vídeo: {e}")
        return download_with_alternative_method(url, output_folder)

def download_with_alternative_method(url, output_folder):
    """Método alternativo de download com conversão para MP4"""
    try:
        print("Tentando método alternativo de download...")
        
        ydl_opts = {
            'format': 'worst[ext=mp4]/worst',  # Qualidade mais baixa, preferindo MP4
            'outtmpl': os.path.join(output_folder, 'original_video.%(ext)s'),
            'quiet': False,
            'no_warnings': False,
            'ignoreerrors': True,
            'socket_timeout': 60,
            'retries': 10,
            # 🔑 Força conversão para MP4
            'postprocessors': [{
                'key': 'FFmpegVideoConvertor',
                'preferedformat': 'mp4',
            }],
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            
            # Verifica o arquivo final gerado
            video_path = os.path.join(output_folder, 'original_video.mp4')
            
            if os.path.exists(video_path):
                print(f"✅ Download alternativo bem-sucedido: {video_path}")
                return video_path
            else:
                print("❌ Método alternativo também falhou")
                return None
                
    except Exception as e:
        print(f"Erro no método alternativo: {e}")
        return None

@app.route('/preview/<project_id>/<cut_id>')
def preview_cut(project_id, cut_id):
    """Preview de um corte específico (streaming de vídeo)"""
    try:
        # Tentar diferentes nomes de arquivo possíveis
        possible_paths = [
            os.path.join(app.config['OUTPUT_FOLDER'], project_id, f'final_cut_{cut_id}.mp4'),
            os.path.join(app.config['OUTPUT_FOLDER'], project_id, f'cut_{cut_id}.mp4'),
            os.path.join(app.config['OUTPUT_FOLDER'], project_id, f'processed_cut_{cut_id}.mp4')
        ]
        
        for cut_path in possible_paths:
            if os.path.exists(cut_path):
                # Retornar vídeo para streaming (não como download)
                return send_file(
                    cut_path, 
                    mimetype='video/mp4',
                    as_attachment=False,
                    conditional=True  # Suporte a range requests para streaming
                )
        
        return jsonify({'error': 'Corte não encontrado'}), 404
    except Exception as e:
        return jsonify({'error': f'Erro ao carregar preview: {str(e)}'}), 500

@app.route('/download/<project_id>/<cut_id>')
def download_cut(project_id, cut_id):
    """Download de um corte específico"""
    try:
        # Tentar diferentes nomes de arquivo possíveis
        possible_paths = [
            os.path.join(app.config['OUTPUT_FOLDER'], project_id, f'final_cut_{cut_id}.mp4'),
            os.path.join(app.config['OUTPUT_FOLDER'], project_id, f'cut_{cut_id}.mp4'),
            os.path.join(app.config['OUTPUT_FOLDER'], project_id, f'processed_cut_{cut_id}.mp4')
        ]
        
        for cut_path in possible_paths:
            if os.path.exists(cut_path):
                return send_file(cut_path, as_attachment=True, download_name=f'cut_{cut_id}.mp4')
        
        return jsonify({'error': 'Corte não encontrado'}), 404
    except Exception as e:
        return jsonify({'error': f'Erro ao baixar: {str(e)}'}), 500

@app.route('/download/srt/<project_id>/<cut_id>')
def download_srt(project_id, cut_id):
    """Download das legendas SRT"""
    try:
        srt_path = os.path.join(app.config['OUTPUT_FOLDER'], project_id, f'cut_{cut_id}.srt')
        if os.path.exists(srt_path):
            return send_file(srt_path, as_attachment=True, download_name=f'cut_{cut_id}.srt')
        else:
            return jsonify({'error': 'Arquivo SRT não encontrado'}), 404
    except Exception as e:
        return jsonify({'error': f'Erro ao baixar SRT: {str(e)}'}), 500

@app.route('/templates')
def get_templates():
    """Listar templates disponíveis"""
    try:
        from services.video_templates import TemplateManager
        tm = TemplateManager()
        templates = tm.list_templates()
        return jsonify({
            'templates': [
                {
                    'id': template_id,
                    'name': template_name,
                    'description': template_desc
                }
                for template_id, template_name, template_desc in templates
            ]
        })
    except Exception as e:
        return jsonify({'error': f'Erro ao listar templates: {str(e)}'}), 500

@app.route('/status/<project_id>')
def get_status(project_id):
    """Verificar status do processamento"""
    try:
        project_folder = os.path.join(app.config['OUTPUT_FOLDER'], project_id)
        metadata_path = os.path.join(project_folder, 'metadata.json')
        
        if os.path.exists(metadata_path):
            with open(metadata_path, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
            return jsonify(metadata)
        else:
            return jsonify({'status': 'processing'})
    except Exception as e:
        return jsonify({'error': f'Erro ao verificar status: {str(e)}'}), 500

if __name__ == '__main__':
    print("🎬 Sixty - Editor de Vídeo Inteligente")
    print("📱 Acesse: http://192.168.0.119:8080")
    print("🛑 Pressione Ctrl+C para parar")
    app.run(debug=False, host='0.0.0.0', port=8080)
