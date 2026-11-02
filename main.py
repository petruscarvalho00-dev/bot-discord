import discord
from discord import app_commands
from discord.ext import commands
from flask import Flask
import threading, os, asyncio

app = Flask(__name__)
@app.route('/')
def home(): return "Ticket Holanda ON"
threading.Thread(target=lambda: app.run(host='0.0.0.0', port=int(os.environ.get("PORT",10000)))).start()

intents = discord.Intents.default()
intents.members = True
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# COLE O LINK DO SEU BANNER AQUI
BANNER_URL = "https://i.imgur.com/SEU_LINK_AQUI.png" # <--- TROCA ISSO

class TicketSelect(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="XFAC", emoji="🔥", value="xfac"),
            discord.SelectOption(label="ALISTAMENTO", emoji="📋", value="alistamento"),
            discord.SelectOption(label="DÚVIDAS", emoji="❓", value="duvidas"),
            discord.SelectOption(label="FALAR COM SUPERIOR", emoji="👑", value="superior"),
            discord.SelectOption(label="OUTROS", emoji="📛", value="outros"),
        ]
        super().__init__(placeholder="📩 Selecione uma categoria...", min_values=1, max_values=1, options=options)
    async def callback(self, interaction: discord.Interaction):
        guild = interaction.guild
        overwrites = {guild.default_role: discord.PermissionOverwrite(view_channel=False), interaction.user: discord.PermissionOverwrite(view_channel=True, send_messages=True, attach_files=True), guild.me: discord.PermissionOverwrite(view_channel=True, send_messages=True, manage_channels=True)}
        canal = await guild.create_text_channel(f"🎫・{self.values[0]}-{interaction.user.name}", overwrites=overwrites)
        await interaction.response.send_message(f"✅ Ticket criado: {canal.mention}", ephemeral=True)
        await canal.send(content=f"{interaction.user.mention} @here", embed=discord.Embed(title=f"🇳🇱 TROPA DA HOLANDA - {self.values[0].upper()}", description="Aguarde um superior.\nUse `/prioridade` e `/assumir`", color=0xff0000))

class TicketView(discord.ui.View):
    def __init__(self): super().__init__(timeout=None); self.add_item(TicketSelect())

@bot.event
async def on_ready():
    bot.add_view(TicketView())
    await bot.tree.sync()
    print(f"ON {bot.user}")

@bot.tree.command(name="painel", description="Cria painel da Tropa da Holanda")
async def painel(interaction: discord.Interaction):
    embed = discord.Embed(
        title="🇳🇱 ATENDIMENTO - TROPA DA HOLANDA",
        description="**O QUE ACONTECE QUANDO VOCÊ ABRE UM TICKET**\n• Canal privado só seu e da equipe\n• Atendimento rápido e sigiloso\n\n**IMPORTANTE**\n• Use apenas para assuntos da facção\n• Falso ticket = punição",
        color=0x000000
    )
    embed.set_image(url=BANNER_URL) # AQUI VAI SEU BANNER
    await interaction.response.send_message(embed=embed, view=TicketView())

@bot.tree.command(name="prioridade", description="Define prioridade")
@app_commands.choices(nivel=[app_commands.Choice(name="🔴 Alta", value="alta"), app_commands.Choice(name="🟡 Média", value="media"), app_commands.Choice(name="🟢 Baixa", value="baixa"), app_commands.Choice(name="⚫ Crítica", value="critica")])
async def prioridade(interaction: discord.Interaction, nivel: app_commands.Choice[str]):
    nome = interaction.channel.name.replace("🔴-ALTA-","").replace("🟡-MEDIA-","").replace("🟢-BAIXA-","").replace("⚫-CRITICA-","").replace("assumido-","")
    pref = {"alta":"🔴-ALTA-","media":"🟡-MEDIA-","baixa":"🟢-BAIXA-","critica":"⚫-CRITICA-"}[nivel.value]
    await interaction.channel.edit(name=pref+nome)
    await interaction.response.send_message(f"Prioridade {nivel.name} definida!")
@bot.tree.command(name="assumir", description="Assumir ticket")
async def assumir(interaction: discord.Interaction): await interaction.channel.edit(name=f"assumido-{interaction.user.name}-{interaction.channel.name}"); await interaction.response.send_message(f"✅ Assumido por {interaction.user.mention}")
@bot.tree.command(name="fechar", description="Fechar ticket")
async def fechar(interaction: discord.Interaction): await interaction.response.send_message("Fechando..."); await asyncio.sleep(2); await interaction.channel.delete()
@bot.tree.command(name="ban", description="Banir")
async def ban(interaction: discord.Interaction, usuario: discord.Member, motivo: str="Sem motivo"): await usuario.ban(reason=motivo); await interaction.response.send_message(f"🔨 {usuario} banido")
@bot.tree.command(name="unban", description="Desbanir por ID")
async def unban(interaction: discord.Interaction, id: str): user = await bot.fetch_user(int(id)); await interaction.guild.unban(user); await interaction.response.send_message(f"✅ {user} desbanido")
@bot.tree.command(name="limpar", description="Limpar msgs")
async def limpar(interaction: discord.Interaction, quantidade: int): await interaction.response.defer(ephemeral=True); await interaction.channel.purge(limit=quantidade); await interaction.followup.send(f"🧹 {quantidade} apagadas", ephemeral=True)

bot.run(os.getenv("TOKEN"))
