# C3PO

The C3PO project is an initiative to develop a robot head (inspired by C3PO from Star Wars) capable of recording audio, transcribing it into text, sending that text to an AI, and replicating the response to the user. So far, we have developed code with functions for recording, transcribing, and interacting with an AI.

## Algorithms Used

1. **Record Audio**: Listens to what was said and saves it in a list, creating a .wav file at the end.

2. **Transcribe Audio**: Transcribes the entire audio into text and temporarily prints it.

3. **Send Message to AI**: Sends the transcribed text to an AI model and retrieves the response.

## Code Structure

1. **Audio Recording**:
   - The `gravar_audio` function sets up the audio stream using the `pyaudio` library.
   - Audio input is continuously captured in real-time and stored in a list of frames.
   - When the recording is manually stopped (Ctrl+C), the audio is saved as a .wav file.

2. **Transcription**:
   - The `transcrever_audio` function uses the `speech_recognition` library to convert the recorded .wav file into text.
   - The audio file is loaded using `sr.AudioFile` and processed into a format suitable for recognition by `recognize_google`.
   - The recognized text is printed and returned.
   - Error handling is included to manage cases of unrecognized speech or API errors.

3. **AI Interaction**:
   - The `enviar_mensagem` function interacts with the AI using the `ollama` library.
   - It sends the transcribed message to the AI model and returns the generated response.

4. **Execution**:
   - The recording function (`gravar_audio`) is called first, creating a .wav file.
   - This audio file is then passed to the `transcrever_audio` function for transcription.
   - The transcription result is printed for verification.
   - Finally, the transcribed text is sent to the AI, and the AI's response is printed.

## How to Run

1. **Import the necessary libraries**:
   ```python
   import pyaudio
   import wave
   import speech_recognition as sr
   import ollama

2. **Install Package**:
   ```python
   pip install pyaudio wave
   pip install speechrecognition ollama
