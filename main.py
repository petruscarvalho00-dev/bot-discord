import os
from flask import Flask
from threading import Thread
import discord
from discord.ext import commands
app=Flask('')
@app.route('/')
def home():return "ON"
def run():app.run(host='0.0.0.0',port=int(os.environ.get("PORT",10000)))
Thread(target=run).start()
intents=discord.Intents.all()
bot=commands.Bot(command_prefix="!",intents=intents)
async def criar_ticket(i,motivo):
 g=i.guild
 ow={g.default_role:discord.PermissionOverwrite(view_channel=False),i.user:discord.PermissionOverwrite(view_channel=True,send_messages=True),g.me:discord.PermissionOverwrite(view_channel=True)}
 nome=f"{motivo.lower().replace(' ','-')}-{i.user.name}"[:90]
 c=await g.create_text_channel(name=nome,overwrites=ow)
 await c.send(f"{i.user.mention} Ticket: {motivo}")
 await i.response.send_message(f"Criado: {c.mention}",ephemeral=True)
class HolandaMenu(discord.ui.Select):
 def __init__(self):
  super().__init__(placeholder="HOLANDA",custom_id="holanda",options=[discord.SelectOption(label="TRANSFERENCIA"),discord.SelectOption(label="DUVIDAS"),discord.SelectOption(label="BOOSTS"),discord.SelectOption(label="XFAC"),discord.SelectOption(label="DENUNCIA"),discord.SelectOption(label="ALIANCA/PARCERIA"),discord.SelectOption(label="OUTROS")])
 async def callback(self,i):await criar_ticket(i,self.values[0])
class FacMenu(discord.ui.Select):
 def __init__(self):
  super().__init__(placeholder="OPCOES FAC",custom_id="fac",options=[discord.SelectOption(label="PAGAR META"),discord.SelectOption(label="SOLICITAR CARGO"),discord.SelectOption(label="SETAGEM"),discord.SelectOption(label="OUTROS")])
 async def callback(self,i):await criar_ticket(i,self.values[0])
class PainelView(discord.ui.View):
 def __init__(self):
  super().__init__(timeout=None)
  self.add_item(HolandaMenu())
  self.add_item(FacMenu())
@bot.command()
async def painelhld(ctx):
 await ctx.send(embed=discord.Embed(title="HOLANDA | OPCOES FAC",description="Escolha no menu"),view=PainelView())
@bot.command()
async def painel3(ctx):await painelhld(ctx)
@bot.event
async def on_ready():print(f"BOT ON {bot.user}")
token=os.getenv("DISCORD_TOKEN") or os.getenv("TOKEN")
if token:token=token.strip()
bot.run(token)
