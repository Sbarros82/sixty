import os
import json
import whisper
import ffmpeg
import subprocess
from datetime import datetime, timedelta
from .prompt_generator import PromptGenerator
from .video_templates import TemplateManager
from .audio_analyzer import AudioAnalyzer
from .video_enhancer import VideoEnhancer

class VideoProcessor:
    def __init__(self, video_path, output_folder, gemini_model, template_name='youtube'):
        self.video_path = video_path
        self.output_folder = output_folder
        self.gemini_model = gemini_model
        self.prompt_generator = PromptGenerator()
        self.template_manager = TemplateManager()
        self.template = self.template_manager.get_template(template_name)
        
        # Carregar modelo Whisper
        self.whisper_model = whisper.load_model("base")
        
        # Contador de processamentos para o mesmo vídeo
        self.processing_count = self._get_processing_count()
        
    def process_video(self, duration):
        """Processa o vídeo completo: transcrição, análise e cortes"""
        try:
            print("🎬 Iniciando processamento do vídeo...")
            
            # 1. Extrair áudio para transcrição
            audio_path = self.extract_audio()
            
            # 2. Transcrever com Whisper
            transcription = self.transcribe_audio(audio_path)
            
            # 3. Analisar conteúdo com Gemini
            analysis = self.analyze_content(transcription, duration)
            
            # 4. Criar cortes com transições suaves
            cuts = self.create_cuts(analysis, duration)
            
            # 5. Salvar metadados
            self.save_metadata(analysis, cuts)
            
            # 6. Incrementar contador de processamento
            self._increment_processing_count()
            
            return {
                'success': True,
                'cuts': cuts,
                'transcription': transcription
            }
            
        except Exception as e:
            print(f"❌ Erro no processamento: {e}")
            return {'success': False, 'error': str(e)}
    
    def extract_audio(self):
        """Extrai áudio do vídeo para transcrição"""
        audio_path = os.path.join(self.output_folder, 'audio.wav')
        
        try:
            stream = ffmpeg.input(self.video_path)
            stream = ffmpeg.output(stream, audio_path, acodec='pcm_s16le', ac=1, ar='16000')
            ffmpeg.run(stream, overwrite_output=True, quiet=True)
            return audio_path
        except Exception as e:
            print(f"Erro ao extrair áudio: {e}")
            raise
    
    def transcribe_audio(self, audio_path):
        """Transcreve áudio usando Whisper"""
        print("🎤 Transcrevendo áudio...")
        
        try:
            result = self.whisper_model.transcribe(audio_path)
            return result
        except Exception as e:
            print(f"Erro na transcrição: {e}")
            raise
    
    def analyze_content(self, transcription, duration):
        """Analisa conteúdo com Gemini para identificar momentos importantes"""
        print("🧠 Analisando conteúdo com IA...")
        
        try:
            # Preparar dados para análise
            segments = transcription.get('segments', [])
            text_content = transcription.get('text', '')
            
            if not text_content:
                # Criar análise simulada se não houver transcrição
                print("📝 Sem transcrição disponível, usando análise automática")
                return self.create_fallback_analysis(duration)
            
            # Gerar prompt para análise
            prompt = self.prompt_generator.create_analysis_prompt(segments, text_content, duration)
            
            # Analisar com Gemini
            print("🤖 Enviando para Gemini AI...")
            response = self.gemini_model.generate_content(prompt)
            
            try:
                analysis = json.loads(response.text)
                print("✅ Análise da IA concluída com sucesso")
                return analysis
            except json.JSONDecodeError:
                # Se o Gemini não retornar JSON válido, criar análise simulada
                print("⚠️ Resposta do Gemini não é JSON válido, usando análise automática")
                return self.create_fallback_analysis(duration)
            
        except Exception as e:
            print(f"❌ Erro na análise da IA: {e}")
            print("🔄 Usando análise automática como fallback")
            return self.create_fallback_analysis(duration)
    
    def create_fallback_analysis(self, duration):
        """Cria análise automática quando há problemas com a IA"""
        print("🔄 Criando análise automática...")
        
        # Obter duração total do vídeo
        video_info = self.get_video_info()
        total_duration = video_info.get('duration', 300)
        
        # Calcular quantos cortes cabem no vídeo
        num_cuts = int(total_duration // duration)
        if num_cuts == 0:
            num_cuts = 1
        
        print(f"📊 Criando {num_cuts} cortes automáticos de {duration}s")
        
        # Criar momentos baseados na duração
        moments = []
        for i in range(num_cuts):
            start_time = i * duration
            end_time = min((i + 1) * duration, total_duration)
            
            moments.append({
                'start_time': start_time,
                'end_time': end_time,
                'summary': f'Corte {i+1} - Segmento automático',
                'transcription': f'Transcrição automática do segmento {i+1}',
                'justification': 'Segmento criado automaticamente baseado na duração escolhida',
                'emotion': 'neutro',
                'keywords': ['automático', 'segmento', 'corte']
            })
        
        return {
            'moments': moments,
            'total_moments': len(moments),
            'video_summary': f'Análise automática: {num_cuts} cortes de {duration}s'
        }
    
    def create_cuts(self, analysis, duration):
        """Cria múltiplos cortes inteligentes com variações para evitar repetição"""
        print("✂️ Criando múltiplos cortes inteligentes com variações...")
        cuts = []
        
        # Obter duração total do vídeo
        video_info = self.get_video_info()
        total_duration = video_info.get('duration', 300)  # 5 minutos padrão
        
        print(f"📊 Duração total do vídeo: {total_duration}s ({total_duration/60:.1f}min)")
        
        # Calcular número de cortes baseado na duração total
        # Para vídeos muito curtos, fazer apenas 1 corte
        if total_duration <= 5:  # Menos de 5 segundos
            num_cuts = 1
        elif total_duration <= duration:
            num_cuts = 1
        elif total_duration <= duration * 3:
            num_cuts = 3
        elif total_duration <= duration * 5:
            num_cuts = 5
        elif total_duration <= duration * 10:
            num_cuts = 10
        else:
            # Para vídeos longos, fazer mais cortes
            num_cuts = min(20, int(total_duration // duration))
        
        print(f"🎯 Criando {num_cuts} cortes de {duration}s cada com variações")
        
        # Gerar pontos de início variados para evitar repetição
        start_points = self.generate_varied_start_points(total_duration, duration, num_cuts)
        
        # Armazenar os tempos de início para uso nas legendas
        if not hasattr(self, '_cut_start_times'):
            self._cut_start_times = {}
        
        for i in range(num_cuts):
            try:
                cut_id = i + 1
                start_time = start_points[i]
                end_time = min(start_time + duration, total_duration)
                
                # Armazenar o tempo de início para este corte
                self._cut_start_times[cut_id] = start_time
                
                # Verificar se ainda há tempo suficiente para um corte
                if end_time - start_time < 1:  # Menos de 1 segundo
                    print(f"⏭️ Pulando corte {cut_id} - tempo insuficiente")
                    continue
                
                print(f"🎬 Processando corte {cut_id}: {start_time}s - {end_time}s")
                
                # Criar corte simples sem efeitos para evitar tela preta
                cut_path = self.create_simple_cut(start_time, end_time, cut_id)
                
                # Gerar transcrição para este trecho
                print(f"🎤 Transcrevendo segmento {cut_id}: {start_time}s - {end_time}s")
                transcription_data = self.transcribe_segment(start_time, end_time)
                print(f"🔍 Resultado da transcrição {cut_id}: {type(transcription_data)}")
                if isinstance(transcription_data, dict):
                    print(f"📝 Texto da transcrição {cut_id}: '{transcription_data.get('text', '')[:100]}...'")
                    print(f"📊 Segmentos da transcrição {cut_id}: {len(transcription_data.get('segments', []))}")
                    # Verificar se a transcrição tem conteúdo válido
                    if not transcription_data.get('text', '').strip():
                        print(f"⚠️ Transcrição {cut_id} vazia, criando texto padrão")
                        transcription_data = {
                            'text': f'Transcrição automática do corte {cut_id}',
                            'segments': [{'start': 0, 'end': 30, 'text': f'Transcrição automática do corte {cut_id}'}]
                        }
                else:
                    print(f"📝 Texto da transcrição {cut_id}: '{str(transcription_data)[:100]}...'")
                    # Se não é dict, converter para formato padrão
                    if not str(transcription_data).strip():
                        print(f"⚠️ Transcrição {cut_id} vazia, criando texto padrão")
                        transcription_data = {
                            'text': f'Transcrição automática do corte {cut_id}',
                            'segments': [{'start': 0, 'end': 30, 'text': f'Transcrição automática do corte {cut_id}'}]
                        }
                
                # Verificar se a transcrição foi bem-sucedida
                if isinstance(transcription_data, dict):
                    print(f"✅ Transcrição {cut_id}: {len(transcription_data.get('segments', []))} segmentos")
                    print(f"📝 Texto: {transcription_data.get('text', '')[:100]}...")
                else:
                    print(f"⚠️ Transcrição {cut_id}: {str(transcription_data)[:100]}...")
                
                # Gerar legendas
                print(f"📄 Criando legendas para corte {cut_id}")
                srt_path = self.create_subtitles(transcription_data, cut_id)
                
                # Criar vídeo final com legendas embutidas (sem narração)
                final_video_path = self.create_final_video(cut_path, srt_path, cut_id)
                
                # Extrair texto da transcrição
                transcription_text = transcription_data['text'] if isinstance(transcription_data, dict) else str(transcription_data)
                
                cuts.append({
                    'id': cut_id,
                    'start_time': start_time,
                    'end_time': end_time,
                    'duration': end_time - start_time,
                    'summary': f'Corte {cut_id} - {start_time}s a {end_time}s',
                    'transcription': transcription_text,
                    'video_path': final_video_path,
                    'srt_path': srt_path
                })
                
                print(f"✅ Corte {cut_id} criado com sucesso")
                
            except Exception as e:
                print(f"❌ Erro ao criar corte {i+1}: {e}")
                import traceback
                traceback.print_exc()
                continue
        
        print(f"🎉 Total de {len(cuts)} cortes criados com sucesso")
        return cuts
    
    def create_simple_cut(self, start_time, end_time, cut_id):
        """Cria corte simples sem efeitos para evitar tela preta"""
        output_path = os.path.join(self.output_folder, f'cut_{cut_id}.mp4')
        
        cut_duration = end_time - start_time
        
        try:
            # Verificar se o arquivo de entrada existe
            if not os.path.exists(self.video_path):
                raise FileNotFoundError(f"Arquivo de vídeo não encontrado: {self.video_path}")
            
            # Verificar se a duração é válida
            if cut_duration <= 0:
                raise ValueError(f"Duração inválida: {cut_duration}")
            
            # Comando FFmpeg simples sem efeitos
            cmd = [
                'ffmpeg', '-y',
                '-i', self.video_path,
                '-ss', str(start_time),
                '-t', str(cut_duration),
                '-c:v', 'libx264',
                '-c:a', 'aac',
                '-preset', 'fast',
                '-crf', '23',
                '-avoid_negative_ts', 'make_zero',
                output_path
            ]
            
            print(f"🔄 Executando corte simples {cut_id}: {' '.join(cmd)}")
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)
            print(f"✅ Corte simples {cut_id} criado com sucesso")
            return output_path
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Erro FFmpeg no corte {cut_id}: {e}")
            print(f"Comando: {' '.join(cmd)}")
            print(f"Erro: {e.stderr}")
            raise
        except Exception as e:
            print(f"❌ Erro inesperado no corte {cut_id}: {e}")
            raise
    
    def create_smooth_cut(self, start_time, end_time, cut_id, duration):
        """Cria corte com efeitos visuais e transições suaves"""
        output_path = os.path.join(self.output_folder, f'cut_{cut_id}.mp4')
        
        # Calcular duração da transição (15% do corte)
        cut_duration = end_time - start_time
        transition_duration = min(cut_duration * 0.15, 1.5)  # Máximo 1.5 segundos
        
        try:
            # Verificar se o arquivo de entrada existe
            if not os.path.exists(self.video_path):
                raise FileNotFoundError(f"Arquivo de vídeo não encontrado: {self.video_path}")
            
            # Verificar se a duração é válida
            if cut_duration <= 0:
                raise ValueError(f"Duração inválida: {cut_duration}")
            
            # Usar template para efeitos visuais (apenas se disponível)
            vf_filters = []
            
            # Adicionar fade in/out apenas se a duração for suficiente
            if cut_duration > transition_duration * 2:
                vf_filters.extend([
                    f'fade=in:0:{transition_duration}',
                    f'fade=out:{cut_duration-transition_duration}:{transition_duration}'
                ])
            
            # Adicionar filtros do template (apenas os básicos para evitar erros)
            if hasattr(self, 'template') and self.template and hasattr(self.template, 'video_filters'):
                # Usar apenas filtros básicos e seguros
                safe_filters = []
                for filter_str in self.template.video_filters:
                    if any(safe in filter_str.lower() for safe in ['eq=', 'scale=', 'pad=']):
                        safe_filters.append(filter_str)
                vf_filters.extend(safe_filters)
            
            # Construir comando FFmpeg
            cmd = ['ffmpeg', '-y', '-i', self.video_path, '-ss', str(start_time), '-t', str(cut_duration)]
            
            # Adicionar filtros de vídeo se houver
            if vf_filters:
                vf_string = ','.join(vf_filters)
                cmd.extend(['-vf', vf_string])
            
            # Adicionar codecs e configurações
            cmd.extend([
                '-c:v', 'libx264',
                '-c:a', 'aac',
                '-preset', 'fast',
                '-crf', '22',
                '-movflags', '+faststart',
                output_path
            ])
            
            print(f"🔄 Executando corte {cut_id}: {' '.join(cmd)}")
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)
            print(f"✅ Corte {cut_id} criado com sucesso")
            return output_path
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Erro FFmpeg no corte {cut_id}: {e}")
            print(f"Comando: {' '.join(cmd)}")
            print(f"Erro: {e.stderr}")
            
            # Fallback: corte simples sem efeitos
            try:
                print(f"🔄 Tentando fallback para corte {cut_id}...")
                cmd = [
                    'ffmpeg', '-y',
                    '-i', self.video_path,
                    '-ss', str(start_time),
                    '-t', str(cut_duration),
                    '-c:v', 'libx264',
                    '-c:a', 'aac',
                    '-preset', 'fast',
                    '-crf', '23',
                    output_path
                ]
                subprocess.run(cmd, check=True, capture_output=True, text=True)
                print(f"✅ Corte {cut_id} criado (fallback)")
                return output_path
            except subprocess.CalledProcessError as e2:
                print(f"❌ Fallback também falhou para corte {cut_id}: {e2}")
                raise
        except Exception as e:
            print(f"❌ Erro inesperado no corte {cut_id}: {e}")
            raise
    
    def create_subtitles(self, transcription_data, cut_id):
        """Cria arquivo SRT com legendas sincronizadas usando timestamps precisos do Whisper"""
        srt_path = os.path.join(self.output_folder, f'cut_{cut_id}.srt')
        
        try:
            print(f"🔍 Criando legendas para corte {cut_id}")
            print(f"📊 Tipo de dados: {type(transcription_data)}")
            print(f"📄 Dados recebidos: {str(transcription_data)[:200]}...")
            print(f"🔍 Verificando se transcription_data é válido...")
            
            # Verificação adicional para garantir que temos dados válidos
            if transcription_data is None:
                print(f"❌ transcription_data é None para corte {cut_id}")
                transcription_data = f"Transcrição automática do corte {cut_id}"
            elif isinstance(transcription_data, str) and not transcription_data.strip():
                print(f"❌ transcription_data é string vazia para corte {cut_id}")
                transcription_data = f"Transcrição automática do corte {cut_id}"
            
            # Obter duração real do corte
            cut_path = os.path.join(self.output_folder, f'cut_{cut_id}.mp4')
            if os.path.exists(cut_path):
                cmd = [
                    'ffprobe', '-v', 'quiet', '-print_format', 'json',
                    '-show_format', cut_path
                ]
                result = subprocess.run(cmd, capture_output=True, text=True, check=True)
                info = json.loads(result.stdout)
                cut_duration = float(info['format']['duration'])
                print(f"⏱️ Duração do corte {cut_id}: {cut_duration}s")
            else:
                cut_duration = 30  # Fallback
                print(f"⚠️ Arquivo de corte não encontrado, usando duração padrão: {cut_duration}s")
            
            # Verificar se temos dados de transcrição estruturados
            if isinstance(transcription_data, dict) and 'segments' in transcription_data:
                print(f"✅ Usando timestamps precisos do Whisper")
                # Usar timestamps precisos do Whisper
                segments = transcription_data['segments']
                text = transcription_data['text']
                
                print(f"📝 Segmentos encontrados: {len(segments)}")
                print(f"📄 Texto completo: {text[:100]}...")
                
                if not segments:
                    # Fallback se não há segmentos
                    print(f"⚠️ Nenhum segmento encontrado, criando legenda simples")
                    srt_content = f"1\n00:00:00,000 --> {self.format_srt_time(cut_duration)}\n{text}\n\n"
                else:
                    srt_content = ""
                    subtitle_id = 1
                    
                    # Criar legendas usando timestamps precisos
                    for segment in segments:
                        # Os timestamps já estão ajustados para o tempo real do vídeo
                        # Precisamos convertê-los para serem relativos ao início do corte
                        original_start = segment['start']
                        original_end = segment['end']
                        
                        # Obter o tempo de início do corte atual
                        cut_start_time = self.get_cut_start_time(cut_id)
                        
                        # Calcular timestamps relativos ao corte
                        relative_start = max(0, original_start - cut_start_time)
                        relative_end = max(0, original_end - cut_start_time)
                        
                        # Garantir que não exceda a duração do corte
                        relative_end = min(relative_end, cut_duration)
                        
                        segment_text = segment['text'].strip()
                        
                        # Limpar texto
                        segment_text = segment_text.replace('"', '').replace("'", '').replace('\\', '')
                        
                        if segment_text and relative_end > relative_start:
                            # Formatar tempo
                            start_str = self.format_srt_time(relative_start)
                            end_str = self.format_srt_time(relative_end)
                            
                            # Dividir em até 3 linhas para formato 9:16
                            subtitle_text = self.create_multi_line_subtitle(segment_text.split())
                            
                            srt_content += f"{subtitle_id}\n{start_str} --> {end_str}\n{subtitle_text}\n\n"
                            subtitle_id += 1
                            print(f"📄 Legenda {subtitle_id-1}: {segment_text[:50]}... (tempo: {relative_start:.1f}s - {relative_end:.1f}s)")
            else:
                print(f"⚠️ Usando fallback para texto simples")
                # Fallback para texto simples
                text = str(transcription_data).strip()
                if not text:
                    text = "Transcrição automática"
                
                # Remover caracteres especiais
                text = text.replace('"', '').replace("'", '').replace('\\', '')
                
                # Dividir em frases
                sentences = self.split_into_sentences(text)
                
                if not sentences:
                    srt_content = f"1\n00:00:00,000 --> {self.format_srt_time(cut_duration)}\n{text}\n\n"
                else:
                    # Distribuir tempo igualmente
                    time_per_sentence = cut_duration / len(sentences)
                    time_per_sentence = max(1.0, time_per_sentence)
                    
                    srt_content = ""
                    subtitle_id = 1
                    
                    for i, sentence in enumerate(sentences):
                        start_time = i * time_per_sentence
                        end_time = min((i + 1) * time_per_sentence, cut_duration)
                        
                        start_str = self.format_srt_time(start_time)
                        end_str = self.format_srt_time(end_time)
                        subtitle_text = self.create_multi_line_subtitle(sentence.split())
                        
                        srt_content += f"{subtitle_id}\n{start_str} --> {end_str}\n{subtitle_text}\n\n"
                        subtitle_id += 1
            
            # Garantir que sempre tenha conteúdo válido
            if not srt_content.strip():
                print(f"⚠️ SRT vazio para corte {cut_id}, criando conteúdo padrão")
                srt_content = f"1\n00:00:00,000 --> {self.format_srt_time(cut_duration)}\nTranscrição automática do corte {cut_id}\\NLegendas embutidas no vídeo\n\n"
            
            # VERIFICAÇÃO EXTRA para o segundo vídeo
            print(f"🔍 Verificação final SRT {cut_id}: {len(srt_content)} caracteres")
            if len(srt_content.strip()) < 20:
                print(f"🚨 SRT {cut_id} muito pequeno, criando conteúdo mínimo")
                srt_content = f"1\n00:00:00,000 --> {self.format_srt_time(cut_duration)}\nLegenda automática\\Ncorte {cut_id}\n\n"
            
            # Verificar se há legendas válidas com timestamps
            if not any('-->' in line for line in srt_content.split('\n')):
                print(f"🚨 SRT {cut_id} não tem timestamps válidos, criando legenda básica")
                srt_content = f"1\n00:00:00,000 --> {self.format_srt_time(cut_duration)}\nTranscrição automática\\Ncorte {cut_id}\n\n"
            
            with open(srt_path, 'w', encoding='utf-8') as f:
                f.write(srt_content)
            
            print(f"✅ Legendas SRT sincronizadas criadas: {cut_duration}s")
            print(f"📁 Arquivo salvo: {srt_path}")
            print(f"📄 Conteúdo final: {len(srt_content)} caracteres")
            return srt_path
            
        except Exception as e:
            print(f"❌ Erro ao criar legendas: {e}")
            import traceback
            traceback.print_exc()
            # Fallback: legenda simples
            try:
                srt_content = f"1\n00:00:00,000 --> {self.format_srt_time(cut_duration)}\n{str(transcription_data)}\n\n"
                with open(srt_path, 'w', encoding='utf-8') as f:
                    f.write(srt_content)
                print(f"✅ Fallback criado: {srt_path}")
                return srt_path
            except Exception as fallback_error:
                print(f"❌ Erro no fallback: {fallback_error}")
                raise
    
    def split_into_sentences(self, text):
        """Divide o texto em frases para melhor sincronização"""
        # Pontuação que indica fim de frase
        sentence_endings = ['.', '!', '?', '...']
        
        sentences = []
        current_sentence = ""
        
        for char in text:
            current_sentence += char
            
            if char in sentence_endings:
                # Limpar a frase
                clean_sentence = current_sentence.strip()
                if clean_sentence:
                    sentences.append(clean_sentence)
                current_sentence = ""
        
        # Adicionar a última frase se houver
        if current_sentence.strip():
            sentences.append(current_sentence.strip())
        
        # Se não conseguiu dividir em frases, dividir por vírgulas
        if len(sentences) <= 1:
            sentences = [s.strip() for s in text.split(',') if s.strip()]
        
        # Se ainda não conseguiu, dividir por espaços em grupos de palavras
        if len(sentences) <= 1:
            words = text.split()
            if len(words) > 10:
                # Dividir em grupos de 8-12 palavras
                group_size = max(8, len(words) // 3)
                sentences = []
                for i in range(0, len(words), group_size):
                    group = words[i:i + group_size]
                    sentences.append(' '.join(group))
            else:
                sentences = [text]
        
        return sentences
    
    def create_multi_line_subtitle(self, words):
        """Cria legenda em até 3 linhas para formato 9:16 com fonte pequena"""
        if not words:
            return "Transcrição\\Nautomática"
        
        # Algoritmo para dividir em até 3 linhas
        text = " ".join(words)
        
        # Se o texto é muito curto, usar apenas uma linha
        if len(text) <= 20:
            return text
        
        # Se o texto é médio, usar duas linhas
        if len(text) <= 40:
            words_list = list(words)
            mid_point = len(words_list) // 2
            
            line1_words = words_list[:mid_point]
            line2_words = words_list[mid_point:]
            
            line1 = " ".join(line1_words)
            line2 = " ".join(line2_words)
            
            return f"{line1}\\N{line2}"
        
        # Para textos longos, usar 3 linhas
        words_list = list(words)
        total_words = len(words_list)
        
        # Dividir em 3 partes aproximadamente iguais
        part1_end = total_words // 3
        part2_end = (total_words * 2) // 3
        
        line1_words = words_list[:part1_end]
        line2_words = words_list[part1_end:part2_end]
        line3_words = words_list[part2_end:]
        
        line1 = " ".join(line1_words)
        line2 = " ".join(line2_words)
        line3 = " ".join(line3_words)
        
        # Garantir que nenhuma linha fique muito longa (máximo 25 caracteres para fonte 11)
        max_chars = 25
        
        if len(line1) > max_chars or len(line2) > max_chars or len(line3) > max_chars:
            # Redistribuir palavras se alguma linha ficou muito longa
            all_words = line1_words + line2_words + line3_words
            lines = []
            current_line = []
            current_length = 0
            
            for word in all_words:
                if current_length + len(word) + 1 <= max_chars and len(lines) < 2:
                    current_line.append(word)
                    current_length += len(word) + 1
                else:
                    if current_line:
                        lines.append(" ".join(current_line))
                    current_line = [word]
                    current_length = len(word)
            
            if current_line:
                lines.append(" ".join(current_line))
            
            # Garantir que temos no máximo 3 linhas
            while len(lines) > 3:
                # Combinar as duas últimas linhas
                if len(lines) >= 2:
                    lines[-2] = lines[-2] + " " + lines[-1]
                    lines.pop()
            
            # Combinar as linhas
            return "\\N".join(lines)
        
        # Combinar as 3 linhas
        return f"{line1}\\N{line2}\\N{line3}"
    
    def format_srt_time(self, seconds):
        """Formata tempo em segundos para formato SRT"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millisecs = int((seconds % 1) * 1000)
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{millisecs:03d}"
    
    def generate_narration(self, transcription, cut_id):
        """Gera narração usando TTS"""
        narration_path = os.path.join(self.output_folder, f'narration_{cut_id}.wav')
        
        try:
            # Criar texto para narração baseado na transcrição
            if len(transcription) > 100:
                narration_text = transcription[:100] + "..."
            else:
                narration_text = transcription
            
            # Usar gTTS (Google Text-to-Speech) para gerar narração
            from gtts import gTTS
            
            tts = gTTS(text=narration_text, lang='pt', slow=False)
            tts.save(narration_path)
            
            print(f"🎤 Narração gerada: {narration_path}")
            return narration_path
            
        except ImportError:
            print("gTTS não disponível, criando narração simulada...")
            # Fallback: criar áudio silencioso
            cmd = [
                'ffmpeg', '-y',
                '-f', 'lavfi',
                '-i', 'anullsrc=channel_layout=stereo:sample_rate=44100',
                '-t', '3',
                narration_path
            ]
            
            subprocess.run(cmd, check=True, capture_output=True)
            return narration_path
            
        except Exception as e:
            print(f"Erro ao gerar narração: {e}")
            # Fallback: criar áudio silencioso
            cmd = [
                'ffmpeg', '-y',
                '-f', 'lavfi',
                '-i', 'anullsrc=channel_layout=stereo:sample_rate=44100',
                '-t', '3',
                narration_path
            ]
            
            subprocess.run(cmd, check=True, capture_output=True)
            return narration_path
    
    def mix_audio(self, video_path, narration_path, cut_id):
        """Mixa áudio original com narração e retorna vídeo com áudio mixado"""
        final_video_path = os.path.join(self.output_folder, f'mixed_video_{cut_id}.mp4')
        
        try:
            # Verificar se o arquivo de vídeo existe
            if not os.path.exists(video_path):
                print(f"❌ Arquivo de vídeo não encontrado: {video_path}")
                return video_path
            
            # Verificar se o arquivo de narração existe
            if not os.path.exists(narration_path):
                print(f"❌ Arquivo de narração não encontrado: {narration_path}")
                # Se não há narração, apenas copiar o vídeo
                cmd = [
                    'ffmpeg', '-y',
                    '-i', video_path,
                    '-c:v', 'libx264',
                    '-c:a', 'aac',
                    '-preset', 'fast',
                    '-crf', '22',
                    final_video_path
                ]
            else:
                # Mixar áudio original (volume 0.7) + narração (volume 0.3) mantendo vídeo
                cmd = [
                    'ffmpeg', '-y',
                    '-i', video_path,
                    '-i', narration_path,
                    '-filter_complex', '[0:a]volume=0.7[a1];[1:a]volume=0.3[a2];[a1][a2]amix=inputs=2:duration=first[outa]',
                    '-map', '0:v',
                    '-map', '[outa]',
                    '-c:v', 'libx264',
                    '-c:a', 'aac',
                    '-preset', 'fast',
                    '-crf', '22',
                    '-b:a', '128k',
                    final_video_path
                ]
            
            print(f"🔄 Executando: {' '.join(cmd)}")
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)
            print(f"✅ Vídeo com áudio mixado criado: {final_video_path}")
            return final_video_path
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Erro ao mixar áudio: {e}")
            print(f"Comando: {' '.join(cmd)}")
            print(f"Erro: {e.stderr}")
            # Retornar vídeo original se falhar
            return video_path
        except Exception as e:
            print(f"❌ Erro inesperado ao mixar áudio: {e}")
            return video_path
    
    def get_video_info(self):
        """Obtém informações do vídeo usando FFprobe"""
        try:
            cmd = [
                'ffprobe', '-v', 'quiet', '-print_format', 'json',
                '-show_format', '-show_streams', self.video_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            info = json.loads(result.stdout)
            
            # Extrair duração
            duration = float(info['format']['duration'])
            
            return {
                'duration': duration,
                'format': info['format']['format_name'],
                'size': info['format']['size']
            }
        except Exception as e:
            print(f"Erro ao obter informações do vídeo: {e}")
            return {'duration': 300}  # 5 minutos padrão
    
    def _get_processing_count(self):
        """Obtém o número de vezes que este vídeo foi processado"""
        try:
            # Criar um identificador único baseado no nome e tamanho do arquivo
            video_info = self.get_video_info()
            video_id = f"{os.path.basename(self.video_path)}_{video_info.get('size', 0)}"
            
            # Arquivo para armazenar contadores
            counter_file = os.path.join(self.output_folder, 'processing_counters.json')
            
            if os.path.exists(counter_file):
                with open(counter_file, 'r', encoding='utf-8') as f:
                    counters = json.load(f)
            else:
                counters = {}
            
            count = counters.get(video_id, 0)
            print(f"📊 Este vídeo já foi processado {count} vezes")
            return count
            
        except Exception as e:
            print(f"⚠️ Erro ao obter contador de processamento: {e}")
            return 0
    
    def _increment_processing_count(self):
        """Incrementa o contador de processamentos para este vídeo"""
        try:
            video_info = self.get_video_info()
            video_id = f"{os.path.basename(self.video_path)}_{video_info.get('size', 0)}"
            
            counter_file = os.path.join(self.output_folder, 'processing_counters.json')
            
            if os.path.exists(counter_file):
                with open(counter_file, 'r', encoding='utf-8') as f:
                    counters = json.load(f)
            else:
                counters = {}
            
            counters[video_id] = counters.get(video_id, 0) + 1
            
            with open(counter_file, 'w', encoding='utf-8') as f:
                json.dump(counters, f, indent=2, ensure_ascii=False)
            
            print(f"📈 Contador de processamento incrementado para {counters[video_id]}")
            
        except Exception as e:
            print(f"⚠️ Erro ao incrementar contador: {e}")
    
    def generate_varied_start_points(self, total_duration, cut_duration, num_cuts):
        """Gera pontos de início variados para evitar repetição de cortes"""
        import random
        import math
        
        print(f"🎲 Gerando {num_cuts} pontos de início variados para vídeo de {total_duration}s")
        print(f"🔄 Este é o {self.processing_count + 1}º processamento deste vídeo")
        
        # Para vídeos muito curtos, usar pontos fixos
        if total_duration <= cut_duration * 2:
            return [0] if num_cuts == 1 else [0, total_duration - cut_duration]
        
        # Calcular espaço disponível para variação
        available_duration = total_duration - cut_duration
        if available_duration <= 0:
            return [0]
        
        # Usar seed baseado no contador de processamento para garantir variação
        random.seed(self.processing_count + 42)  # +42 para evitar seed 0
        
        # Estratégias diferentes baseadas na duração do vídeo
        if total_duration <= 300:  # Até 5 minutos - variação simples
            return self._simple_variation(available_duration, cut_duration, num_cuts)
        elif total_duration <= 1800:  # Até 30 minutos - variação média
            return self._medium_variation(available_duration, cut_duration, num_cuts)
        else:  # Mais de 30 minutos - variação avançada
            return self._advanced_variation(available_duration, cut_duration, num_cuts)
    
    def _simple_variation(self, available_duration, cut_duration, num_cuts):
        """Variação simples para vídeos curtos"""
        import random
        
        # Dividir o vídeo em seções e escolher pontos aleatórios
        section_size = available_duration / num_cuts
        start_points = []
        
        for i in range(num_cuts):
            section_start = i * section_size
            section_end = min((i + 1) * section_size, available_duration)
            
            # Escolher ponto aleatório dentro da seção
            if section_end > section_start:
                random_offset = random.uniform(0, min(section_end - section_start, cut_duration * 0.5))
                start_point = section_start + random_offset
            else:
                start_point = section_start
            
            start_points.append(max(0, start_point))
        
        # Garantir que não há sobreposição
        start_points.sort()
        for i in range(1, len(start_points)):
            if start_points[i] - start_points[i-1] < cut_duration:
                start_points[i] = start_points[i-1] + cut_duration
        
        return start_points
    
    def _medium_variation(self, available_duration, cut_duration, num_cuts):
        """Variação média para vídeos médios (até 30 min)"""
        import random
        
        # Criar padrões de variação mais sofisticados
        patterns = [
            'linear_random',      # Linear com variação aleatória
            'exponential',        # Distribuição exponencial
            'clustered',          # Agrupamentos
            'spread_out'          # Bem distribuído
        ]
        
        # Escolher padrão baseado no número de cortes
        if num_cuts <= 3:
            pattern = 'spread_out'
        elif num_cuts <= 7:
            pattern = 'linear_random'
        else:
            pattern = random.choice(patterns)
        
        print(f"📊 Usando padrão de variação: {pattern}")
        
        if pattern == 'linear_random':
            return self._linear_random_variation(available_duration, cut_duration, num_cuts)
        elif pattern == 'exponential':
            return self._exponential_variation(available_duration, cut_duration, num_cuts)
        elif pattern == 'clustered':
            return self._clustered_variation(available_duration, cut_duration, num_cuts)
        else:  # spread_out
            return self._spread_out_variation(available_duration, cut_duration, num_cuts)
    
    def _advanced_variation(self, available_duration, cut_duration, num_cuts):
        """Variação avançada para vídeos longos (mais de 30 min)"""
        import random
        
        # Para vídeos muito longos, criar múltiplas estratégias
        print(f"🎯 Vídeo longo detectado, aplicando variação avançada")
        
        # Dividir em zonas temporais
        zones = 4  # Dividir em 4 zonas
        zone_duration = available_duration / zones
        
        start_points = []
        cuts_per_zone = max(1, num_cuts // zones)
        
        for zone in range(zones):
            zone_start = zone * zone_duration
            zone_end = min((zone + 1) * zone_duration, available_duration)
            
            # Gerar cortes para esta zona
            zone_cuts = min(cuts_per_zone, num_cuts - len(start_points))
            if zone_cuts > 0:
                zone_points = self._spread_out_variation(
                    zone_end - zone_start, 
                    cut_duration, 
                    zone_cuts
                )
                # Ajustar para a zona atual
                zone_points = [zone_start + p for p in zone_points]
                start_points.extend(zone_points)
        
        # Se ainda faltam cortes, distribuir aleatoriamente
        while len(start_points) < num_cuts:
            random_point = random.uniform(0, available_duration)
            # Verificar se não está muito próximo de outros pontos
            too_close = any(abs(random_point - p) < cut_duration * 0.8 for p in start_points)
            if not too_close:
                start_points.append(random_point)
        
        # Ordenar e garantir espaçamento mínimo
        start_points.sort()
        for i in range(1, len(start_points)):
            if start_points[i] - start_points[i-1] < cut_duration:
                start_points[i] = start_points[i-1] + cut_duration
        
        return start_points[:num_cuts]
    
    def _linear_random_variation(self, available_duration, cut_duration, num_cuts):
        """Variação linear com elementos aleatórios"""
        import random
        
        base_interval = available_duration / (num_cuts + 1)
        start_points = []
        
        for i in range(num_cuts):
            base_point = (i + 1) * base_interval
            # Adicionar variação aleatória de ±20% do intervalo
            variation = random.uniform(-0.2, 0.2) * base_interval
            start_point = base_point + variation
            start_points.append(max(0, min(start_point, available_duration)))
        
        return sorted(start_points)
    
    def _exponential_variation(self, available_duration, cut_duration, num_cuts):
        """Distribuição exponencial - mais cortes no início"""
        import math
        
        start_points = []
        for i in range(num_cuts):
            # Usar função exponencial para concentrar no início
            progress = i / (num_cuts - 1) if num_cuts > 1 else 0
            exponential_factor = math.exp(-2 * progress)  # Decaimento exponencial
            start_point = available_duration * (1 - exponential_factor)
            start_points.append(max(0, start_point))
        
        return sorted(start_points)
    
    def _clustered_variation(self, available_duration, cut_duration, num_cuts):
        """Variação com agrupamentos"""
        import random
        
        # Criar 2-3 agrupamentos
        num_clusters = min(3, num_cuts // 2)
        cluster_size = available_duration / num_clusters
        
        start_points = []
        cuts_per_cluster = num_cuts // num_clusters
        
        for cluster in range(num_clusters):
            cluster_start = cluster * cluster_size
            cluster_end = min((cluster + 1) * cluster_size, available_duration)
            
            # Distribuir cortes dentro do agrupamento
            cluster_cuts = min(cuts_per_cluster, num_cuts - len(start_points))
            for j in range(cluster_cuts):
                progress = j / max(1, cluster_cuts - 1)
                start_point = cluster_start + (cluster_end - cluster_start) * progress
                # Adicionar pequena variação aleatória
                variation = random.uniform(-cut_duration * 0.3, cut_duration * 0.3)
                start_point += variation
                start_points.append(max(cluster_start, min(start_point, cluster_end)))
        
        return sorted(start_points)
    
    def _spread_out_variation(self, available_duration, cut_duration, num_cuts):
        """Distribuição bem espaçada"""
        import random
        
        # Dividir o vídeo em seções iguais
        section_size = available_duration / num_cuts
        start_points = []
        
        for i in range(num_cuts):
            section_start = i * section_size
            section_end = min((i + 1) * section_size, available_duration)
            
            # Escolher ponto no meio da seção com pequena variação
            mid_point = (section_start + section_end) / 2
            variation = random.uniform(-section_size * 0.3, section_size * 0.3)
            start_point = mid_point + variation
            
            start_points.append(max(section_start, min(start_point, section_end)))
        
        return sorted(start_points)
    
    def get_cut_start_time(self, cut_id):
        """Obtém o tempo de início de um corte específico"""
        try:
            # Armazenar os pontos de início dos cortes para referência
            if not hasattr(self, '_cut_start_times'):
                self._cut_start_times = {}
            
            # Se já temos o tempo armazenado, retornar
            if cut_id in self._cut_start_times:
                start_time = self._cut_start_times[cut_id]
                print(f"⏱️ Tempo de início do corte {cut_id}: {start_time}s (armazenado)")
                return start_time
            
            # Se não temos, calcular baseado no padrão de variação
            # Isso é um fallback - o ideal é que os tempos sejam armazenados durante a criação dos cortes
            video_info = self.get_video_info()
            total_duration = video_info.get('duration', 300)
            
            # Usar o mesmo algoritmo de variação para calcular o tempo de início
            # Por enquanto, usar um cálculo simples baseado no ID do corte
            cut_duration = 30  # Assumir duração padrão
            available_duration = total_duration - cut_duration
            
            if available_duration <= 0:
                return 0
            
            # Calcular baseado no ID do corte (1-indexed)
            start_time = (cut_id - 1) * cut_duration
            
            # Garantir que não exceda o vídeo
            start_time = min(start_time, available_duration)
            
            # Armazenar para uso futuro
            self._cut_start_times[cut_id] = start_time
            
            print(f"⏱️ Tempo de início do corte {cut_id}: {start_time}s (calculado)")
            return start_time
            
        except Exception as e:
            print(f"⚠️ Erro ao obter tempo de início do corte {cut_id}: {e}")
            return 0
    
    def transcribe_segment(self, start_time, end_time):
        """Transcreve um segmento específico do vídeo com sincronização avançada"""
        try:
            # Extrair áudio do segmento
            audio_segment_path = os.path.join(self.output_folder, f'segment_{start_time}_{end_time}.wav')
            
            cmd = [
                'ffmpeg', '-y',
                '-i', self.video_path,
                '-ss', str(start_time),
                '-t', str(end_time - start_time),
                '-vn', '-acodec', 'pcm_s16le',
                '-ar', '16000',
                audio_segment_path
            ]
            
            subprocess.run(cmd, check=True, capture_output=True)
            
            # Transcrever com Whisper com configurações otimizadas para obter timestamps
            model = whisper.load_model("base")
            result = model.transcribe(
                audio_segment_path,
                language='pt',  # Especificar português
                task='transcribe',
                verbose=False,
                word_timestamps=True  # Obter timestamps por palavra
            )
            
            # Limpar arquivo temporário
            os.remove(audio_segment_path)
            
            # Processar o texto e timestamps para melhor sincronização
            text = result.get('text', '').strip()
            segments = result.get('segments', [])
            
            # Se não há texto, usar fallback
            if not text:
                return {
                    'text': f"Transcrição do segmento {start_time}s - {end_time}s",
                    'segments': []
                }
            
            # Limpar e normalizar o texto
            text = text.replace('\n', ' ').replace('  ', ' ')
            text = text.strip()
            
            # Ajustar timestamps para o tempo real do vídeo
            adjusted_segments = []
            for segment in segments:
                adjusted_segment = {
                    'start': segment['start'] + start_time,
                    'end': segment['end'] + start_time,
                    'text': segment['text'].strip()
                }
                adjusted_segments.append(adjusted_segment)
            
            return {
                'text': text,
                'segments': adjusted_segments
            }
            
        except Exception as e:
            print(f"Erro ao transcrever segmento: {e}")
            return {
                'text': f"Transcrição do segmento {start_time}s - {end_time}s",
                'segments': []
            }
    
    def create_final_video(self, video_path, srt_path, cut_id):
        """Cria vídeo final com legendas embutidas em formato 9:16"""
        output_path = os.path.join(self.output_folder, f'final_cut_{cut_id}.mp4')
        
        try:
            print(f"🎬 Criando vídeo final para corte {cut_id}")
            
            # Verificar se o arquivo de vídeo existe
            if not os.path.exists(video_path):
                print(f"❌ Arquivo de vídeo não encontrado: {video_path}")
                return video_path
            
            # Verificar se o arquivo SRT existe e tem conteúdo
            srt_exists = os.path.exists(srt_path)
            srt_has_content = False
            
            if srt_exists:
                try:
                    with open(srt_path, 'r', encoding='utf-8') as f:
                        srt_content = f.read()
                    srt_has_content = len(srt_content.strip()) > 10
                    print(f"📄 SRT {cut_id}: {len(srt_content)} caracteres, válido: {srt_has_content}")
                    print(f"📄 Primeiros 100 caracteres do SRT: {srt_content[:100]}")
                    if not srt_has_content:
                        print(f"⚠️ SRT {cut_id} tem conteúdo insuficiente: '{srt_content.strip()}'")
                except Exception as read_error:
                    print(f"❌ Erro ao ler SRT: {read_error}")
                    srt_has_content = False
            
            if not srt_exists or not srt_has_content:
                print(f"⚠️ SRT inválido para corte {cut_id}, criando SRT básico...")
                try:
                    # Criar SRT básico com texto de exemplo usando fonte 11
                    basic_srt_content = f"1\n00:00:00,000 --> 00:00:30,000\nTranscrição automática\\Ndo corte {cut_id}\n\n"
                    with open(srt_path, 'w', encoding='utf-8') as f:
                        f.write(basic_srt_content)
                    print(f"✅ SRT básico criado: {srt_path}")
                    print(f"📄 Conteúdo do SRT básico: {basic_srt_content}")
                    srt_has_content = True
                except Exception as srt_error:
                    print(f"❌ Erro ao criar SRT básico: {srt_error}")
                    srt_has_content = False
            
            # GARANTIR que sempre temos um SRT válido para o segundo vídeo
            if not srt_has_content:
                print(f"🚨 FORÇANDO criação de SRT para corte {cut_id} (segundo vídeo)")
                try:
                    # Criar SRT forçado para garantir legendas
                    forced_srt_content = f"1\n00:00:00,000 --> 00:00:30,000\nLegenda automática\\Ncorte {cut_id}\n\n"
                    with open(srt_path, 'w', encoding='utf-8') as f:
                        f.write(forced_srt_content)
                    print(f"✅ SRT forçado criado: {srt_path}")
                    srt_has_content = True
                except Exception as forced_error:
                    print(f"❌ Erro ao criar SRT forçado: {forced_error}")
                    srt_has_content = False
            
            # Para vídeos curtos, apenas copiar sem legendas para evitar problemas
            video_info = self.get_video_info()
            total_duration = video_info.get('duration', 300)
            
            if total_duration <= 10:  # Vídeos muito curtos
                print(f"📹 Vídeo curto ({total_duration}s), copiando sem legendas")
                cmd = [
                    'ffmpeg', '-y',
                    '-i', video_path,
                    '-vf', 'scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2:black',
                    '-c:v', 'libx264',
                    '-c:a', 'aac',
                    '-preset', 'fast',
                    '-crf', '23',
                    output_path
                ]
            else:
                # Comando FFmpeg para adicionar legendas embutidas com formato 9:16
                # Escapar o caminho do SRT para Windows
                srt_path_escaped = srt_path.replace('\\', '/').replace(':', '\\:')
                
                # Estilo refinado para legendas: formato 9:16 com fonte 11
                subtitle_style = (
                    'FontSize=11,'  # Fonte pequena (11) para formato vertical
                    'PrimaryColour=&Hffffff,'  # Texto branco
                    'OutlineColour=&H000000,'  # Contorno preto
                    'BackColour=&H60000000,'  # Fundo mais transparente (60%)
                    'Bold=0,'  # Sem negrito para fonte menor
                    'Outline=1,'  # Contorno mais fino
                    'Shadow=1,'  # Sombra sutil
                    'MarginV=80,'  # Margem vertical maior (mais próximo do fundo)
                    'MarginL=50,'  # Margem esquerda
                    'MarginR=50,'  # Margem direita
                    'Alignment=2,'  # Alinhamento centralizado
                    'Spacing=0.7'  # Espaçamento menor entre linhas
                )
                
                if srt_has_content:
                    # Com legendas
                    cmd = [
                        'ffmpeg', '-y',
                        '-i', video_path,
                        '-vf', f'scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2:black,subtitles={srt_path_escaped}:force_style=\'{subtitle_style}\'',
                        '-c:v', 'libx264',
                        '-c:a', 'aac',
                        '-preset', 'fast',
                        '-crf', '23',
                        output_path
                    ]
                else:
                    # Sem legendas
                    cmd = [
                        'ffmpeg', '-y',
                        '-i', video_path,
                        '-vf', 'scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2:black',
                        '-c:v', 'libx264',
                        '-c:a', 'aac',
                        '-preset', 'fast',
                        '-crf', '23',
                        output_path
                    ]
            
            print(f"🔄 Executando FFmpeg para corte {cut_id}: {' '.join(cmd)}")
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)
            print(f"✅ Vídeo final criado: {output_path}")
            return output_path
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Erro ao criar vídeo final para corte {cut_id}: {e}")
            print(f"Comando: {' '.join(cmd)}")
            print(f"Erro: {e.stderr}")
            
            # Fallback: apenas copiar o vídeo com formato 9:16
            try:
                print(f"🔄 Tentando fallback para vídeo final...")
                cmd = [
                    'ffmpeg', '-y',
                    '-i', video_path,
                    '-vf', 'scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2:black',
                    '-c:v', 'libx264',
                    '-c:a', 'aac',
                    '-preset', 'fast',
                    '-crf', '23',
                    output_path
                ]
                subprocess.run(cmd, check=True, capture_output=True, text=True)
                print(f"✅ Vídeo final criado (fallback): {output_path}")
                return output_path
            except Exception as fallback_error:
                print(f"❌ Erro no fallback: {fallback_error}")
                return video_path
        except Exception as e:
            print(f"❌ Erro inesperado ao criar vídeo final para corte {cut_id}: {e}")
            return video_path
    
    def save_metadata(self, analysis, cuts):
        """Salva metadados do processamento"""
        metadata = {
            'timestamp': datetime.now().isoformat(),
            'original_video': self.video_path,
            'analysis': analysis,
            'cuts': cuts,
            'total_cuts': len(cuts)
        }
        
        metadata_path = os.path.join(self.output_folder, 'metadata.json')
        
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
