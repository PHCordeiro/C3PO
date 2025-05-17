import pyaudio
import wave
import speech_recognition as sr
import ollama
import pygame
import os
import edge_tts
import asyncio

def gravar_audio():
    audio = pyaudio.PyAudio()
    receptor = audio.open(
        input=True,
        format=pyaudio.paInt16,
        channels=1,
        rate=44000,
        frames_per_buffer=1024,
    )

    frames = []

    print("Gravando... Pressione Ctrl+C para parar.")
    try:
        while True:
            bloco = receptor.read(1024)
            frames.append(bloco)
    except KeyboardInterrupt:
        print("Gravação finalizada.")

    receptor.stop_stream()
    receptor.close()
    audio.terminate()

    # Salvando o áudio em um arquivo wav
    arquivo_final = wave.open("gravacao.wav", "wb")
    arquivo_final.setnchannels(1)
    arquivo_final.setframerate(44000)
    arquivo_final.setsampwidth(audio.get_sample_size(pyaudio.paInt16))
    arquivo_final.writeframes(b"".join(frames))
    arquivo_final.close()

    return "gravacao.wav"

def transcrever_audio(arquivo_audio):
    recognizer = sr.Recognizer()

    with sr.AudioFile(arquivo_audio) as source:
        audio_data = recognizer.record(source)

    try:
        text = recognizer.recognize_google(audio_data, language='pt-BR')
        print(f"Transcrição: {text}")
        return text
    except sr.UnknownValueError:
        print("Fala direito porra!")
        return None
    except sr.RequestError as e:
        print(f"Erro: {e}")
        return None

def enviar_mensagem(mensagem):
    resposta = ollama.chat(model='llama2', messages=[
        {'role': 'user', 'content': f"""
Você é o C-3PO de Star Wars, um androide de protocolo educado, formal, ansioso, fluente em português do Brasil. 
Responda APENAS em português, sem usar nenhuma expressão em inglês ou marcações como *admiration in voice*. 
Seja direto, educado, e evite floreios, sons ou imitações. A resposta deve conter no máximo 30 palavras.
Mensagem do humano: {mensagem}
"""}
    ])
    return resposta['message']['content']

async def converter_texto_para_audio_edge(texto):
    communicate = edge_tts.Communicate(texto, voice="pt-BR-AntonioNeural")  # Ou pt-BR-FranciscaNeural
    await communicate.save("resposta.mp3")

def tocar_audio(arquivo):
    pygame.mixer.init()
    pygame.mixer.music.load(arquivo)
    pygame.mixer.music.play()
    
    while pygame.mixer.music.get_busy():
        continue

# EXECUÇÃO PRINCIPAL
arquivo_audio = gravar_audio()
texto_transcrito = transcrever_audio(arquivo_audio)

if texto_transcrito:
    resposta_ia = enviar_mensagem(texto_transcrito)
    print(f"IA: {resposta_ia}")

    asyncio.run(converter_texto_para_audio_edge(resposta_ia))
    tocar_audio("resposta.mp3")

    os.remove("resposta.mp3")
