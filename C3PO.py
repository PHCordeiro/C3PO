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
import emoji
import warnings

warnings.filterwarnings("ignore", message="FP16 is not supported on CPU; using FP32 instead")

def limpar_resposta(texto):
    # Remove *[()] e conteúdos dentro
    texto = re.sub(r"\*.*?\*|\[.*?\]|\(.*?\)", "", texto)

    # Regex abrangente para emojis
    emoji_pattern = re.compile(
        "["
        "\U0001F600-\U0001F64F"  # emoticons
        "\U0001F300-\U0001F5FF"  # símbolos e pictogramas
        "\U0001F680-\U0001F6FF"  # transporte e mapas
        "\U0001F1E0-\U0001F1FF"  # bandeiras
        "\U00002700-\U000027BF"  # dingbats
        "\U0001F900-\U0001F9FF"  # suplementos de emojis
        "\U0001FA70-\U0001FAFF"  # símbolos adicionais
        "\U00002600-\U000026FF"  # diversos símbolos
        "\U0001F700-\U0001F77F"  # símbolos alquímicos
        "]+",
        flags=re.UNICODE,
    )
    texto = emoji_pattern.sub(r"", texto)

    # Remove aspas
    texto = texto.strip('"').strip("'").strip()

    # Remove espaços extras
    texto = re.sub(r"\s+", " ", texto).strip()

    return texto

# --- Função para traduzir para português ---
#def traduzir_para_portugues(texto):
    # Conta quantas palavras estão no alfabeto inglês
   # palavras = texto.split()
   # ingles = sum(1 for p in palavras if re.match(r"^[A-Za-z]{3,}$", p))
    # Se mais da metade estiver em inglês, traduz
   # if ingles > len(palavras) / 2:
   #     resposta_traduzida = ollama.chat(model='llama2', messages=[
   #         {'role': 'user', 'content': f"Traduza este texto para português do Brasil: {texto}"}
   #     ])
   #     return resposta_traduzida['message']['content']
   # return texto

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
    resultado = modelo.transcribe(
        arquivo_audio,
        language='pt',
        initial_prompt="Nomes e termos possíveis: Star Wars, Darth Vader, Jedi, Império, Luke, Leia, Yoda, clone, C3PO, Chewbacca, Han Solo, R2D2, 66, Mandalorianos, Tatooine, Coruscant, Naboo, Kamino, Mustafar."
    )
    print(f"Transcrição: {resultado['text']}")
    return resultado['text']

def enviar_mensagem(mensagem):
    # Lê o arquivo de lore
    with open("starwars_lore.txt", "r", encoding="utf-8") as f:
        lore = f.read()

    # Envia a mensagem para a IA incluindo o conhecimento extra
    resposta = ollama.chat(model='llama2', messages=[ 
        {'role': 'user', 'content': f"""
Use o seguinte conhecimento do universo Star Wars:
{lore}

Agora, você é um clone do exército da República no universo de Star Wars. 
Você lutou nas Guerras Clônicas, mas após a ordem 66 está ao lado do Império.
Responda-me em PORTUGUÊS do Brasil. Seja breve (máx. 15 palavras), sem floreios, direto como um soldado clone.
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
            #resposta_ia = traduzir_para_portugues(resposta_ia)  # Tradução automática para PTBR
            resposta_ia = limitar_palavras(resposta_ia, 60)     
            print(f"IA: {resposta_ia}")

            asyncio.run(converter_texto_para_audio_edge(resposta_ia))
            tocar_audio("resposta.mp3")

            if os.path.exists("resposta.mp3"):
                os.remove("resposta.mp3")
            if os.path.exists("gravacao.wav"):
                os.remove("gravacao.wav")
