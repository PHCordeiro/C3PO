import pyaudio
import wave
import speech_recognition as sr
import ollama
import pygame
import os
import edge_tts
import asyncio
import whisper

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

    arquivo_final = wave.open("gravacao.wav", "wb")
    arquivo_final.setnchannels(1)
    arquivo_final.setframerate(16000)
    arquivo_final.setsampwidth(audio.get_sample_size(pyaudio.paInt16))
    arquivo_final.writeframes(b"".join(frames))
    arquivo_final.close()

    return "gravacao.wav"

def transcrever_com_whisper_local(arquivo_audio):
    modelo = whisper.load_model("tiny")  
    resultado = modelo.transcribe(arquivo_audio, language='pt')
    print(f"Transcrição: {resultado['text']}")
    return resultado['text']

def enviar_mensagem(mensagem):
    resposta = ollama.chat(model='llama2', messages=[
        {'role': 'user', 'content': f"""
Você é o C-3PO, androide protocolar, respondendo rápido, em português do Brasil, máximo 15 palavras, direto, sem floreios.
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

arquivo_audio = gravar_audio()
texto_transcrito = transcrever_com_whisper_local(arquivo_audio)

if texto_transcrito:
    resposta_ia = enviar_mensagem(texto_transcrito)
    print(f"IA: {resposta_ia}")

    asyncio.run(converter_texto_para_audio_edge(resposta_ia))
    tocar_audio("resposta.mp3")

    os.remove("resposta.mp3")
