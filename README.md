# 🤖 BotCall - SunShield

Este é um bot automatizado para envio de recados por voz, desenvolvido para a empresa **SunShield**. Ele recebe comandos de voz por telefone, interpreta a mensagem e faz uma ligação automática para entregar o recado ao contato desejado.

---

## 🚀 Funcionalidades principais

- ✅ Comandos de voz naturais como:
  - “Avise o João que a entrega chegou”
  - “Mande um recado para a Maria que o cliente ligou”
- ✅ Liga automaticamente para o contato cadastrado
- ✅ Respostas de voz variadas e mais humanas
- ✅ Histórico de recados enviados salvo em `recados.json`
- ✅ Painel web para adicionar e gerenciar contatos
- ✅ Rodapé com créditos e logo no painel

---

## ☎️ Como usar (envio de recado por voz)

1. **Ligue** para o número do Twilio configurado.
2. **Aguarde a saudação** do bot.
3. **Fale uma frase como**:
   > "Avise o João que a reunião foi adiada"

O sistema localizará o contato e fará a ligação para entregar o recado automaticamente.

---

## 🌐 Acessar o painel de contatos

Acesse o link:

[https://sunshield-bot.onrender.com/painel-contatos.html]

> No painel é possível adicionar novos contatos ou remover os existentes de forma simples e rápida.

---

## 📂 Estrutura do projeto

- `app.py` — Código principal (Flask + Twilio)
- `contacts.json` — Lista de contatos
- `recados.json` — Histórico de recados (gerado automaticamente)
- `painel-contatos.html` — Painel web para gerenciar contatos
- `.env` — Credenciais e configurações (não enviado ao GitHub)
- `requirements.txt` — Dependências do projeto

---

## 👨‍💻 Desenvolvido por

**Jordanlvs 💼**  
*Desenvolvedor do sistema BotCall - SunShield*
