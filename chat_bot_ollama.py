import ollama

def enviar_mensagem(mensagem):
    #Criando a conversa com o Ollama
    resposta = ollama.chat(model='llama2', messages=[
        {'role': 'user', 'content': f'Responda rapidamente e em português:  {mensagem}'},
    ])

    return resposta['message']['content']

print(enviar_mensagem("Qual a principal diferença entre insetos e aranhas?"))
