import os
from flask import Flask
from threading import Thread
import discord
from discord.ext import commands

# Site falso pra Render nao desligar
app = Flask('')
@app.route('/')
def home():
    return "Bot On"

def run_flask():
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))

Thread(target=run_flask).start()

# Bot
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"Bot logado como {bot.user}")

TOKEN = os.getenv("TOKEN")
if not TOKEN:
    print("ERRO: Coloca o TOKEN na Render em Environment")
else:
    bot.run(TOKEN)

       
