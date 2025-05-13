import os
import json
from flask import Flask, request, Response
from twilio.twiml.voice_response import VoiceResponse, Gather
from twilio.rest import Client
import openai
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# Configs
twilio_sid = os.getenv("TWILIO_ACCOUNT_SID")
twilio_token = os.getenv("TWILIO_AUTH_TOKEN")
twilio_number = os.getenv("TWILIO_NUMBER")
openai.api_key = os.getenv("OPENAI_API_KEY")

client = Client(twilio_sid, twilio_token)

# Contatos
with open("contacts.json", "r", encoding="utf-8") as f:
    contacts = json.load(f)


@app.route("/voice", methods=["POST"])
def voice():
    """Atende ligação e pergunta pelo recado"""
    response = VoiceResponse()
    gather = Gather(input="speech", action="/handle-reply", method="POST", timeout=5)
    gather.say("Você ligou para a SunShield. Como posso ajudar?")
    response.append(gather)
    response.say("Não entendi o recado. Tente novamente.")
    return Response(str(response), mimetype="text/xml")


@app.route("/handle-reply", methods=["POST"])
def handle_reply():
    """Processa a resposta de voz com GPT"""
    speech_text = request.form.get("SpeechResult", "").lower()
    print(f"[RECEBIDO] {speech_text}")

    prompt = f"""
    Extraia nome e recado da frase abaixo. Sempre retorne no formato JSON:
    {{ "destinatario": "João", "recado": "a entrega foi feita" }}
    Frase: "{speech_text}"
    """

    try:
        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        content = completion["choices"][0]["message"]["content"]
        print("[GPT]:", content)
        data = json.loads(content)

        nome = data.get("destinatario", "").lower()
        mensagem = data.get("recado")
        telefone = contacts.get(nome)

        if telefone:
            print(f"Ligando para {nome} ({telefone}) com o recado: {mensagem}")
            call = client.calls.create(
                twiml=f'<Response><Say>Recado de {twilio_number}: {mensagem}</Say></Response>',
                to=telefone,
                from_=twilio_number
            )
            return _twiml_response("Tudo certo, estou repassando seu recado.")
        else:
            return _twiml_response(f"Desculpe, não encontrei o número de {nome}.")

    except Exception as e:
        print("Erro:", e)
        return _twiml_response("Não consegui interpretar o recado. Pode repetir?")


def _twiml_response(texto):
    resp = VoiceResponse()
    resp.say(texto)
    return Response(str(resp), mimetype="text/xml")


if __name__ == "__main__":
    app.run(debug=True)
