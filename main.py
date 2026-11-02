import discord
from discord.ext import commands
from discord import app_commands
from flask import Flask
import threading
import os
import asyncio
from datetime import timedelta

# Flask pro Render não derrubar
app = Flask(__name__)
@app.route('/')
def home(): return "Bot Ticket On!"
def run(): app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
threading.Thread(target=run).start()

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"Logado como {bot.user}")
    try:
        synced = await bot.tree.sync()
        print(f"Sincronizado {len(synced)} comandos /")
    except Exception as e:
        print(e)

# /painel ticket
@bot.tree.command(name="painel", description="Cria painel de ticket")
async def painel(interaction: discord.Interaction):
    embed = discord.Embed(title="🎫 Suporte", description="Clique no botão abaixo para abrir um ticket", color=0x2b2d31)
    view = TicketView()
    await interaction.response.send_message(embed=embed, view=view)

class TicketView(discord.ui.View):
    def __init__(self): super().__init__(timeout=None)
    @discord.ui.button(label="Abrir Ticket", style=discord.ButtonStyle.blurple, emoji="🎫")
    async def abrir(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild = interaction.guild
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            interaction.user: discord.PermissionOverwrite(view_channel=True, send_messages=True),
            guild.me: discord.PermissionOverwrite(view_channel=True)
        }
        canal = await guild.create_text_channel(f"ticket-{interaction.user.name}", overwrites=overwrites)
        await interaction.response.send_message(f"Ticket criado: {canal.mention}", ephemeral=True)
        await canal.send(f"{interaction.user.mention} bem-vindo! Descreva seu problema.")

# /renomear
@bot.tree.command(name="renomear", description="Renomeia o ticket atual")
@app_commands.describe(novo_nome="Novo nome do canal")
async def renomear(interaction: discord.Interaction, novo_nome: str):
    if "ticket-" not in interaction.channel.name:
        return await interaction.response.send_message("Use isso apenas em tickets!", ephemeral=True)
    await interaction.channel.edit(name=novo_nome)
    await interaction.response.send_message(f"Canal renomeado para {novo_nome}")

# /ban
@bot.tree.command(name="ban", description="Bane um usuário")
@app_commands.describe(usuario="Usuário", tempo="Tempo em minutos (0 = permanente)", motivo="Motivo")
async def ban(interaction: discord.Interaction, usuario: discord.Member, tempo: int = 0, motivo: str = "Sem motivo"):
    if not interaction.user.guild_permissions.ban_members:
        return await interaction.response.send_message("Você não tem permissão!", ephemeral=True)
    await usuario.ban(reason=motivo)
    await interaction.response.send_message(f"🔨 {usuario.mention} banido. Motivo: {motivo}")
    if tempo > 0:
        await asyncio.sleep(tempo * 60)
        try:
            await interaction.guild.unban(usuario)
            await interaction.channel.send(f"⏰ {usuario.mention} desbanido automaticamente após {tempo}min")
        except: pass

# /unban
@bot.tree.command(name="unban", description="Desbane um usuário")
@app_commands.describe(usuario_id="ID do usuário")
async def unban(interaction: discord.Interaction, usuario_id: str):
    if not interaction.user.guild_permissions.ban_members:
        return await interaction.response.send_message("Você não tem permissão!", ephemeral=True)
    try:
        user = await bot.fetch_user(int(usuario_id))
        await interaction.guild.unban(user)
        await interaction.response.send_message(f"✅ {user.name} desbanido!")
    except:
        await interaction.response.send_message("ID inválido ou usuário não banido.", ephemeral=True)

bot.run(os.getenv("TOKEN"))
