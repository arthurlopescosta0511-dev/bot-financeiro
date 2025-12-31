import telebot
import json
import os
from datetime import datetime

# ================= CONFIGURAÇÃO =================
TOKEN = "8248823430:AAHCr05v9lulJbf_GKYGCtXeeC-I-5L9-Zs"
bot = telebot.TeleBot(TOKEN)
ARQUIVO = "gastos.json"

# ================= FUNÇÕES BASE =================
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

# ================= COMANDOS =================
@bot.message_handler(commands=["start", "ajuda"])
def ajuda(message):
    bot.reply_to(
        message,
        "📖 *Ajuda – Bot Financeiro*\n\n"
        "💰 /saldo 2000\n"
        "Define o saldo mensal\n\n"
        "✏️ 50 mercado\n"
        "Registra um gasto\n\n"
        "📊 /resumo\n"
        "Lista os gastos do mês\n\n"
        "📊 /grafico\n"
        "Gráfico mensal em texto\n\n"
        "🗑️ /apagar\n"
        "Apaga o último gasto\n\n"
        "🗑️ /apagar 2\n"
        "Apaga um gasto específico\n\n"
        "✏️ /editar 2 120 mercado\n"
        "Edita um gasto\n\n"
        "📅 /mes 2025-01\n"
        "Mostra dados de meses anteriores",
        parse_mode="Markdown"
    )

# ================= SALDO =================
@bot.message_handler(commands=["saldo"])
def definir_saldo(message):
    dados = carregar_dados()
    chat = str(message.chat.id)
    mes = mes_atual()

    try:
        valor = float(message.text.split()[1])
    except:
        bot.reply_to(message, "❌ Use: /saldo 2000")
        return

    dados.setdefault(chat, {})
    dados[chat][mes] = {"saldo": valor, "gastos": []}
    salvar_dados(dados)

    bot.reply_to(message, f"✅ Saldo definido: R${valor:.2f}")

# ================= RESUMO =================
@bot.message_handler(commands=["resumo"])
def resumo(message):
    dados = carregar_dados()
    chat = str(message.chat.id)
    mes = mes_atual()

    if chat not in dados or mes not in dados[chat]:
        bot.reply_to(message, "❌ Defina o saldo primeiro")
        return

    gastos = dados[chat][mes]["gastos"]
    if not gastos:
        bot.reply_to(message, "❌ Nenhum gasto registrado")
        return

    texto = f"📊 Gastos do mês ({mes}):\n\n"
    for i, g in enumerate(gastos, start=1):
        texto += f"{i}️⃣ R${g['valor']:.2f} | {g['categoria']}\n"

    bot.reply_to(message, texto)

# ================= APAGAR =================
@bot.message_handler(commands=["apagar"])
def apagar(message):
    dados = carregar_dados()
    chat = str(message.chat.id)
    mes = mes_atual()

    if chat not in dados or mes not in dados[chat]:
        bot.reply_to(message, "❌ Nenhum gasto para apagar")
        return

    gastos = dados[chat][mes]["gastos"]
    partes = message.text.split()

    if not gastos:
        bot.reply_to(message, "❌ Nenhum gasto para apagar")
        return

    if len(partes) == 2:
        try:
            indice = int(partes[1]) - 1
            gasto = gastos.pop(indice)
        except:
            bot.reply_to(message, "❌ Número inválido")
            return
    else:
        gasto = gastos.pop()

    salvar_dados(dados)
    bot.reply_to(
        message,
        f"🗑️ Gasto removido:\nR${gasto['valor']:.2f} | {gasto['categoria']}"
    )

# ================= EDITAR =================
@bot.message_handler(commands=["editar"])
def editar(message):
    dados = carregar_dados()
    chat = str(message.chat.id)
    mes = mes_atual()
    partes = message.text.split()

    if chat not in dados or mes not in dados[chat]:
        bot.reply_to(message, "❌ Nenhum gasto para editar")
        return

    if len(partes) < 4:
        bot.reply_to(message, "❌ Use: /editar número valor categoria")
        return

    try:
        indice = int(partes[1]) - 1
        valor = float(partes[2])
        categoria = " ".join(partes[3:])
    except:
        bot.reply_to(message, "❌ Dados inválidos")
        return

    gastos = dados[chat][mes]["gastos"]

    if indice < 0 or indice >= len(gastos):
        bot.reply_to(message, "❌ Número inválido")
        return

    gastos[indice]["valor"] = valor
    gastos[indice]["categoria"] = categoria
    salvar_dados(dados)

    bot.reply_to(message, f"✏️ Gasto editado:\nR${valor:.2f} | {categoria}")

# ================= GRÁFICO TEXTO =================
@bot.message_handler(commands=["grafico"])
def grafico(message):
    dados = carregar_dados()
    chat = str(message.chat.id)
    mes = mes_atual()

    if chat not in dados or mes not in dados[chat]:
        bot.reply_to(message, "❌ Sem dados para o mês")
        return

    categorias = {}
    for g in dados[chat][mes]["gastos"]:
        categorias[g["categoria"]] = categorias.get(g["categoria"], 0) + g["valor"]

    if not categorias:
        bot.reply_to(message, "❌ Nenhum gasto registrado")
        return

    maior = max(categorias.values())
    texto = f"📊 Gastos por categoria ({mes})\n\n"

    for cat, valor in categorias.items():
        barras = int((valor / maior) * 10)
        texto += f"{cat:<12} {'█' * barras} R${valor:.2f}\n"

    bot.reply_to(message, texto)

# ================= MESES ANTERIORES =================
@bot.message_handler(commands=["mes"])
def ver_mes(message):
    dados = carregar_dados()
    chat = str(message.chat.id)
    partes = message.text.split()

    if len(partes) != 2:
        bot.reply_to(message, "❌ Use: /mes AAAA-MM")
        return

    mes = partes[1]

    if chat not in dados or mes not in dados[chat]:
        bot.reply_to(message, "❌ Não há dados para esse mês")
        return

    saldo = dados[chat][mes]["saldo"]
    gastos = dados[chat][mes]["gastos"]

    total = sum(g["valor"] for g in gastos)
    texto = f"📅 Resumo {mes}\n"
    texto += f"💰 Saldo: R${saldo:.2f}\n"
    texto += f"📉 Gasto: R${total:.2f}\n"
    texto += f"💵 Restante: R${saldo - total:.2f}\n\n"

    for i, g in enumerate(gastos, start=1):
        texto += f"{i}️⃣ R${g['valor']:.2f} | {g['categoria']}\n"

    bot.reply_to(message, texto)

# ================= REGISTRAR GASTO =================
@bot.message_handler(func=lambda m: True)
def registrar_gasto(message):
    dados = carregar_dados()
    chat = str(message.chat.id)
    mes = mes_atual()

    try:
        partes = message.text.split()
        valor = float(partes[0])
        categoria = " ".join(partes[1:]) if len(partes) > 1 else "Outros"
    except:
        return

    if chat not in dados or mes not in dados[chat]:
        bot.reply_to(message, "❌ Defina o saldo com /saldo primeiro")
        return

    dados[chat][mes]["gastos"].append({
        "valor": valor,
        "categoria": categoria
    })

    salvar_dados(dados)
    bot.reply_to(message, f"✅ Gasto registrado: R${valor:.2f}")

# ================= INICIAR BOT =================
print("🤖 Bot financeiro rodando...")
bot.infinity_polling()
