import os
import json
import re
import random
import datetime
from flask import Flask, request, Response, jsonify, send_from_directory
from twilio.twiml.voice_response import VoiceResponse, Gather
from twilio.rest import Client
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)

# Configurações do Twilio
twilio_sid = os.getenv("TWILIO_ACCOUNT_SID")
twilio_token = os.getenv("TWILIO_AUTH_TOKEN")
twilio_number = os.getenv("TWILIO_NUMBER")
client = Client(twilio_sid, twilio_token)

CONTACTS_FILE = "contacts.json"
LOG_FILE = "recados.json"

# ---------- Funções utilitárias ----------

def load_contacts():
    if not os.path.exists(CONTACTS_FILE):
        return {}
    with open(CONTACTS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_contacts(data):
    with open(CONTACTS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def salvar_log(nome, recado):
    log_entry = {
        "nome": nome,
        "recado": recado,
        "data": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    if not os.path.exists(LOG_FILE):
        with open(LOG_FILE, "w", encoding="utf-8") as f:
            json.dump([log_entry], f, ensure_ascii=False, indent=2)
    else:
        with open(LOG_FILE, "r+", encoding="utf-8") as f:
            data = json.load(f)
            data.append(log_entry)
            f.seek(0)
            json.dump(data, f, ensure_ascii=False, indent=2)

def _twiml_response(texto, voice="Polly.Camila"):
    resp = VoiceResponse()
    resp.say(texto, language="pt-BR", voice=voice)
    return Response(str(resp), mimetype="text/xml")

mensagens = [
    "Tudo certo, estou repassando seu recado.",
    "Já estou cuidando disso.",
    "Ok, o recado será entregue.",
    "Entendido, mensagem sendo enviada.",
    "Pronto! Deixe comigo."
]

def _twiml_response_escolhida():
    texto = random.choice(mensagens)
    return _twiml_response(texto, voice="Polly.Camila")

def fazer_ligacao(telefone, recado):
    return client.calls.create(
        twiml=f'<Response><Say voice="Polly.Camila" language="pt-BR">Aqui é da SunShield. Você tem um recado: {recado}</Say></Response>',
        to=telefone,
        from_=twilio_number
    )

def extrair_comando(speech_text):
    padrao = re.compile(r"(?:avise|mande um recado|fale|peça|pede)(?: para)?(?: o| a)?\s*(.*?)\s+que\s+(.*)")
    match = padrao.search(speech_text)
    if match:
        return match.group(1).strip(), match.group(2).strip()
    return None, None

# ---------- Rotas Flask ----------

@app.route("/voice", methods=["POST"])
def voice():
    response = VoiceResponse()
    gather = Gather(input="speech", action="/handle-reply", method="POST", timeout=5, language="pt-BR")
    gather.say("Você ligou para a SunShield. Como posso ajudar?", language="pt-BR", voice="Polly.Camila")
    response.append(gather)
    response.say("Não entendi o recado. Tente novamente.", language="pt-BR", voice="Polly.Camila")
    return Response(str(response), mimetype="text/xml")

@app.route("/handle-reply", methods=["POST"])
def handle_reply():
    speech_text = request.form.get("SpeechResult", "").lower()
    print(f"[RECEBIDO] {speech_text}")

    try:
        nome, recado = extrair_comando(speech_text)
        if not nome or not recado:
            raise ValueError("Comando não reconhecido")

        contacts = load_contacts()
        telefone = contacts.get(nome.lower())

        if telefone:
            fazer_ligacao(telefone, recado)
            salvar_log(nome, recado)
            return _twiml_response_escolhida()
        else:
            return _twiml_response(f"Desculpe, não encontrei o número de {nome}.", voice="Polly.Camila")

    except Exception as e:
        print("Erro:", e)
        return _twiml_response(
            "Não consegui entender o recado. Tente dizer: avise o João que a entrega foi feita.",
            voice="Polly.Camila"
        )

@app.route("/add-contact", methods=["POST"])
def add_contact():
    data = request.get_json()
    nome = data.get("nome", "").lower()
    telefone = data.get("telefone")

    contacts = load_contacts()
    if nome in contacts:
        return jsonify({"status": "erro", "mensagem": f"{nome} já existe. Use outro nome ou exclua o contato existente."})

    contacts[nome] = telefone
    save_contacts(contacts)
    return jsonify({"status": "sucesso", "mensagem": f"{nome} salvo com sucesso."})

@app.route("/get-contacts", methods=["GET"])
def get_contacts():
    return jsonify(load_contacts())

@app.route("/painel-contatos.html")
def serve_painel():
    return send_from_directory(".", "painel-contatos.html")

# ---------- Execução ----------
if __name__ == "__main__":
    app.run(debug=True)
