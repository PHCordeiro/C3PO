import pyaudio
import wave
import speech_recognition as sr
import openai
from gtts import gTTS
import os

# Configurações da OpenAI
openai.api_key = 'sua-chave-api'

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

    #Salvando o áudio em um arquivo wav
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

arquivo_audio  = gravar_audio()
transcrever_audio(arquivo_audio)