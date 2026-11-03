import os
from flask import Flask
from threading import Thread
import discord
from discord.ext import commands

app = Flask('')
@app.route('/')
def home(): return "ON"
def run(): app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
Thread(target=run).start()

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

async def criar_ticket(interaction, motivo):
    guild = interaction.guild
    overwrites = {
        guild.default_role: discord.PermissionOverwrite(view_channel=False),
        interaction.user: discord.PermissionOverwrite(view_channel=True, send_messages=True),
        guild.me: discord.PermissionOverwrite(view_channel=True)
    }
    nome = f"{motivo.lower().replace(' ','-')}-{interaction.user.name}"[:90]
    canal = await guild.create_text_channel(name=nome, overwrites=overwrites)
    await canal.send(f"{interaction.user.mention} Ticket: {motivo}")
    await interaction.response.send_message(f"Criado: {canal.mention}", ephemeral=True)

class HolandaMenu(discord.ui.Select):
    def __init__(self):
        super().__init__(placeholder="HOLANDA - Selecione", custom_id="holanda", options=[
            discord.SelectOption(label="TRANSFERENCIA"),
            discord.SelectOption(label="DUVIDAS"),
            discord.SelectOption(label="BOOSTS"),
            discord.SelectOption(label="XFAC"),
            discord.SelectOption(label="DENUNCIA"),
            discord.SelectOption(label="ALIANCA/PARCERIA"),
            discord.SelectOption(label="OUTROS"),
        ])
    async def callback(self, interaction):
        await criar_ticket(interaction, self.values[0])

class FacMenu(discord
