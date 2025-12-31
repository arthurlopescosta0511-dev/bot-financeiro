import telebot
import json
import os
from datetime import datetime

TOKEN = os.getenv("TOKEN")  # pega token do Render
bot = telebot.TeleBot(TOKEN)

ARQUIVO = "gastos.json"

# ------------------- Funções de dados -------------------
def carregar_dados():
    if os.path.exists(ARQUIVO):
        with open(ARQUIVO, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def salvar_dados(dados):
    with open(ARQUIVO, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)

def mes_atual():
    return datetime.now().strftime("%Y-%m")

# ------------------- Comandos -------------------
@bot.message_handler(commands=["start", "ajuda"])
def ajuda(message):
    texto = (
        "💰 Bot Financeiro\n\n"
        "Comandos:\n"
        "/saldo 2000 → definir saldo mensal\n"
        "50 uber → registrar gasto\n"
        "/total → total gasto\n"
        "/restante → saldo restante\n"
        "/resumo → resumo do mês\n"
        "/apagar → apagar último gasto
