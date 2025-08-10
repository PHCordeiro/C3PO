import pyaudio
import wave
import torch
import ollama
import pygame
import os
import edge_tts
import asyncio
import whisper
import msvcrt  # <-- IMPORTADO para capturar teclas no Windows
import re
import warnings

warnings.filterwarnings("ignore", message="FP16 is not supported on CPU; using FP32 instead")

# --- Função para limpar a resposta ---
def limpar_resposta(texto):
    texto = re.sub(r"\*.*?\*|\[.*?\]|\(.*?\)", "", texto)  # Remove *[()]
    texto = texto.strip('"').strip("'").strip()  # Remove aspas
    texto = re.sub(r"\s+", " ", texto).strip()  # Remove espaços extras
    return texto

# --- Função para traduzir para português ---
def traduzir_para_portugues(texto):
    # Checa se tem palavras que parecem inglês (3+ letras ASCII)
    if re.search(r"\b[A-Za-z]{3,}\b", texto):
        resposta_traduzida = ollama.chat(model='llama2', messages=[
            {'role': 'user', 'content': f"Traduza todo este texto para português do Brasil, mantendo o sentido: {texto}"}
        ])
        return resposta_traduzida['message']['content']
    return texto

# --- Função para limitar resposta a X palavras ---
def limitar_palavras(texto, max_palavras=20):
    palavras = texto.split()
    if len(palavras) > max_palavras:
        palavras = palavras[:max_palavras]
    return ' '.join(palavras)

def gravar_audio():
    audio = pyaudio.PyAudio()
    receptor = audio.open(
        input=True,
        format=pyaudio.paInt16,
        channels=1,
        rate=16000,
        frames_per_buffer=1024,
    )

    frames = []
    print("Gravando... Pressione ENTER para parar.")

    while True:
        bloco = receptor.read(1024)
        frames.append(bloco)
        if msvcrt.kbhit():
            if msvcrt.getch() == b'\r':
                break

    receptor.stop_stream()
    receptor.close()
    audio.terminate()

    arquivo_final = wave.open("gravacao.wav", "wb")
    arquivo_final.setnchannels(1)
    arquivo_final.setframerate(16000)
    arquivo_final.setsampwidth(audio.get_sample_size(pyaudio.paInt16))
    arquivo_final.writeframes(b"".join(frames))
    arquivo_final.close()

    return "gravacao.wav"

def transcrever_com_whisper_local(arquivo_audio):
    device = "cpu"
    print(f"using: {device}")
    modelo = whisper.load_model("tiny", device=device)  
    resultado = modelo.transcribe(arquivo_audio, language='pt')
    print(f"Transcrição: {resultado['text']}")
    return resultado['text']

def enviar_mensagem(mensagem):
    resposta = ollama.chat(model='llama2', messages=[
        {'role': 'user', 'content': f"""
Você é um androide.
Responda-me em PORTUGUÊS do Brasil, nunca em inglês. Use no máximo 15 palavras, nem uma a mais. Seja objetivo, sem floreios e sem gesticular.
Mensagem: {mensagem}
"""}
    ])
    return resposta['message']['content']

async def converter_texto_para_audio_edge(texto):
    communicate = edge_tts.Communicate(texto, voice="pt-BR-AntonioNeural") 
    await communicate.save("resposta.mp3")

def tocar_audio(arquivo):
    pygame.mixer.init()
    pygame.mixer.music.load(arquivo)
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        continue
    pygame.mixer.music.unload()

if __name__ == "__main__":
    while True:
        input("Pressione ENTER para iniciar a gravação (ou Ctrl+C para sair)...")
        
        arquivo_audio = gravar_audio()
        texto_transcrito = transcrever_com_whisper_local(arquivo_audio)

        if texto_transcrito.strip():
            resposta_ia = enviar_mensagem(texto_transcrito)
            resposta_ia = limpar_resposta(resposta_ia)
            resposta_ia = traduzir_para_portugues(resposta_ia)  # Tradução automática para PTBR
            resposta_ia = limitar_palavras(resposta_ia, 45)     # Limita a 20 palavras
            print(f"IA: {resposta_ia}")

            asyncio.run(converter_texto_para_audio_edge(resposta_ia))
            tocar_audio("resposta.mp3")

            if os.path.exists("resposta.mp3"):
                os.remove("resposta.mp3")
            if os.path.exists("gravacao.wav"):
                os.remove("gravacao.wav")
