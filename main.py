import os
from flask import Flask
from threading import Thread
import discord
from discord.ext import commands

app = Flask('')
@app.route('/')
def home(): return "ON"
Thread(target=lambda: app.run(host='0.0.0.0', port=int(os.environ.get("PORT",10000)))).start()

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

async def criar_ticket(i, motivo):
    for c in i.guild.text_channels:
        if i.user.name.lower() in c.name.lower():
            try:
                if c.overwrites_for(i.user).view_channel:
                    return await i.response.send_message(f"Ja tem: {c.mention}", ephemeral=True)
            except: pass
    overwrites = {i.guild.default_role: discord.PermissionOverwrite(view_channel=False), i.user: discord.PermissionOverwrite(view_channel=True), i.guild.me: discord.PermissionOverwrite(view_channel=True)}
    canal = await i.guild.create_text_channel(name=f"{motivo.lower()}-{i.user.name}"[:90], overwrites=overwrites)
    await canal.send(f"{i.user.mention} Ticket {motivo}")
    await i.response.send_message(f"Criado {canal.mention}", ephemeral=True)

class Sel(discord.ui.Select):
    def __init__(self, ph, ops, cid):
        super().__init__(placeholder=ph, custom_id=cid, options=[discord.SelectOption(label=o) for o in ops])
    async def callback(self, i): await criar_ticket(i, self.values[0])

class View(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(Sel("HOLANDA", ["TRANSFERENCIA","DUVIDAS","BOOSTS","XFAC","DENUNCIA","ALIANCA/PARCERIA","OUTROS"], "h"))
        self.add_item(Sel("OPCOES FAC", ["PAGAR META","SOLICITAR CARGO","SETAGEM","OUTROS"], "f"))

@bot.command()
async def painelhld(ctx): await ctx.send(embed=discord.Embed(title="HOLANDA | OPCOES FAC", description="Escolha no menu"), view=View())
@bot.command()
async def painel3(ctx): await painelhld(ctx)

@bot.event
async def on_ready(): print(f"ON {bot.user}")

bot.run(os.getenv("TOKEN"))
       
