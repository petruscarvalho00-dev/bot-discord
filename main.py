from flask import Flask
from threading import Thread
import os
import discord
from discord.ext import commands

app = Flask('')
@app.route('/')
def home():
    return "Bot online!"

def run():
  app.run(host='0.0.0.0',port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

keep_alive()

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"ONLINE como {bot.user}")

@bot.command()
async def ping(ctx):
    await ctx.send("Bot on!")

bot.run(os.getenv("DISCORD_TOKEN"))
