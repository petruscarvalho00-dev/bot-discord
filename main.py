import os, threading, asyncio, discord
from discord.ext import commands
from flask import Flask
app = Flask(__name__)
@app.route('/')
def home(): return "ON"
def run_web(): app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
threading.Thread(target=run_web, daemon=True).start()
TOKEN = os.getenv("TOKEN") or os.getenv("DISCORD_TOKEN") or os.getenv("DISCORD")
intents = discord.Intents.default()
intents.members = True
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)
@bot.event
async def on_ready():
    try: await bot.tree.sync()
    except: pass
    print(f"### BOT ON: {bot.user} ###")
@bot.tree.command(name="painel", description="Cria painel de ticket")
async def painel(interaction: discord.Interaction):
    view = discord.ui.View(timeout=None)
    async def cb(i: discord.Interaction):
        ow = {i.guild.default_role: discord.PermissionOverwrite(view_channel=False), i.user: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_messages=True), i.guild.me: discord.PermissionOverwrite(view_channel=True)}
        ch = await i.guild.create_text_channel(f"ticket-{i.user.name}", overwrites=ow)
        await i.response.send_message(f"Criado {ch.mention}", ephemeral=True)
        await ch.send(f"{i.user.mention} explique seu problema")
    b = discord.ui.Button(label="Abrir Ticket", emoji="🎫", style=discord.ButtonStyle.blurple)
    b.callback = cb
    view.add_item(b)
    await interaction.response.send_message(embed=discord.Embed(title="Central", description="Clique abaixo", color=0x5865f2), view=view)
@bot.tree.command(name="fechar", description="Fecha")
async def fechar(interaction: discord.Interaction):
    await interaction.response.send_message("Fechando...")
    await asyncio.sleep(2)
    await interaction.channel.delete()
@bot.tree.command(name="ban", description="Bane")
async def ban(interaction: discord.Interaction, usuario: discord.Member, motivo: str = "Sem motivo"):
    await usuario.ban(reason=motivo)
    await interaction.response.send_message(f"{usuario} banido")
@bot.tree.command(name="unban", description="Desbane")
async def unban(interaction: discord.Interaction, id: str):
    u = await bot.fetch_user(int(id))
    await interaction.guild.unban(u)
    await interaction.response.send_message(f"{u} desbanido")
@bot.tree.command(name="adicionar", description="Adiciona no ticket")
async def adicionar(interaction: discord.Interaction, usuario: discord.Member):
    await interaction.channel.set_permissions(usuario, view_channel=True, send_messages=True)
    await interaction.response.send_message(f"{usuario.mention} add")
@bot.tree.command(name="remover", description="Remove do ticket")
async def remover(interaction: discord.Interaction, usuario: discord.Member):
    await interaction.channel.set_permissions(usuario, overwrite=None)
    await interaction.response.send_message(f"{usuario.mention} removido")
bot.run(TOKEN)
