import os, threading, asyncio, discord
from discord import app_commands
from discord.ext import commands
from flask import Flask

app = Flask(__name__)
@app.route('/')
def home(): return "ON"
def run_web(): app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
threading.Thread(target=run_web, daemon=True).start()

TOKEN = os.getenv("TOKEN") or os.getenv("DISCORD_TOKEN")
intents = discord.Intents.default()
intents.members = True
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

def get_cargo(guild):
    for r in guild.roles:
        if "Permissão Ticket" in r.name or "Permissão" in r.name:
            return r
    return None

async def criar_ticket(interaction, motivo):
    cargo = get_cargo(interaction.guild)
    overw = {
        interaction.guild.default_role: discord.PermissionOverwrite(view_channel=False),
        interaction.user: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_messages=True, attach_files=True),
        interaction.guild.me: discord.PermissionOverwrite(view_channel=True, send_messages=True, manage_channels=True),
    }
    if cargo:
        overw[cargo] = discord.PermissionOverwrite(view_channel=True, send_messages=True, read_messages=True)

    ch = await interaction.guild.create_text_channel(f"🎫・{motivo.lower()}-{interaction.user.name}", overwrites=overw)
    
    embed = discord.Embed(
        title=f"🎫 Ticket - {motivo}",
        description=f"Olá {interaction.user.mention}!\n\n**Motivo:** `{motivo}`\n**Atendimento:** {cargo.mention if cargo else 'Staff'}\n\nAguarde, alguém vai te atender!",
        color=0x2B2D31
    )
    
    class TicketInsideView(discord.ui.View):
        def __init__(self):
            super().__init__(timeout=None)
        
        @discord.ui.button(label="Atender", emoji="✅", style=discord.ButtonStyle.success)
        async def atender(self, i: discord.Interaction, b: discord.ui.Button):
            await i.response.send_message(f"✅ Ticket assumido por {i.user.mention}!", ephemeral=False)
            await i.channel.edit(name=f"✅・{i.user.name}")
            b.disabled = True
            await i.message.edit(view=self)

        @discord.ui.button(label="Fechar - Resolvido", emoji="🔒", style=discord.ButtonStyle.secondary)
        async def resolvido(self, i: discord.Interaction, b: discord.ui.Button):
            await i.response.send_message("🔒 Fechando como **RESOLVIDO** em 5s...")
            await asyncio.sleep(5)
            await i.channel.delete(reason="Resolvido")

        @discord.ui.button(label="Fechar - Sem Resposta", emoji="⛔", style=discord.ButtonStyle.danger)
        async def sem_resposta(self, i: discord.Interaction, b: discord.ui.Button):
            await i.response.send_message("⛔ Fechando como **SEM RESPOSTA** em 5s...")
            await asyncio.sleep(5)
            await i.channel.delete(reason="Sem resposta")

    await ch.send(content=f"{interaction.user.mention} {cargo.mention if cargo else ''}", embed=embed, view=TicketInsideView())
    return ch

class TropaView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
       
