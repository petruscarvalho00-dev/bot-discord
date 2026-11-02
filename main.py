import discord
from discord import app_commands
from discord.ext import commands
from flask import Flask
import threading, os, asyncio

app = Flask(__name__)
@app.route('/')
def home(): return "Ticket Beco ON"
threading.Thread(target=lambda: app.run(host='0.0.0.0', port=int(os.environ.get("PORT",10000)))).start()

intents = discord.Intents.default()
intents.members = True
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

class TicketSelect(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="XFAC", emoji="🔥", value="xfac", description="Assuntos de facção"),
            discord.SelectOption(label="ALISTAMENTO", emoji="📋", value="alistamento", description="Quero me alistar"),
            discord.SelectOption(label="DÚVIDAS", emoji="❓", value="duvidas", description="Tirar dúvidas"),
            discord.SelectOption(label="FALAR COM SUPERIOR", emoji="👑", value="superior", description="Falar com a alta"),
            discord.SelectOption(label="OUTROS", emoji="📛", value="outros", description="Outros assuntos"),
        ]
        super().__init__(placeholder="📩 Selecione uma categoria...", min_values=1, max_values=1, options=options)
    async def callback(self, interaction: discord.Interaction):
        guild = interaction.guild
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            interaction.user: discord.PermissionOverwrite(view_channel=True, send_messages=True, attach_files=True),
            guild.me: discord.PermissionOverwrite(view_channel=True, send_messages=True, manage_channels=True)
        }
        canal = await guild.create_text_channel(f"🎫・{self.values[0]}-{interaction.user.name}", overwrites=overwrites)
        await interaction.response.send_message(f"✅ Ticket criado: {canal.mention}", ephemeral=True)
        embed = discord.Embed(title=f"ATENDIMENTO - {self.values[0].upper()}", description=f"{interaction.user.mention} Aguarde um superior.\n\nUse `/prioridade` pra urgência.\nUse `/assumir` pra assumir.", color=0x2b2d31)
        await canal.send(content=f"{interaction.user.mention} @here", embed=embed)

class TicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(TicketSelect())

@bot.event
async def on_ready():
    bot.add_view(TicketView())
    await bot.tree.sync()
    print(f"ON {bot.user}")

@bot.tree.command(name="painel", description="Cria painel de ticket bonito")
async def painel(interaction: discord.Interaction):
    embed = discord.Embed(title="ATENDIMENTO BECO", description="**O QUE ACONTECE QUANDO VOCÊ ABRE UM TICKET**\n• Um canal privado será criado apenas para você\n• Apenas você e nossa equipe terão acesso\n• Nossa equipe responderá o mais rápido possível\n\n**IMPORTANTE**\n• Use o sistema apenas para suporte", color=0xffd700)
    if interaction.guild.icon: embed.set_thumbnail(url=interaction.guild.icon.url)
    await interaction.response.send_message(embed=embed, view=TicketView())

@bot.tree.command(name="prioridade", description="Define prioridade")
@app_commands.choices(nivel=[app_commands.Choice(name="🔴 Alta", value="alta"), app_commands.Choice(name="🟡 Média", value="media"), app_commands.Choice(name="🟢 Baixa", value="baixa"), app_commands.Choice(name="⚫ Crítica - PCR", value="critica")])
async def prioridade(interaction: discord.Interaction, nivel: app_commands.Choice[str]):
    nome = interaction.channel.name.replace("🔴-ALTA-","").replace("🟡-MEDIA-","").replace("🟢-BAIXA-","").replace("⚫-CRITICA-","").replace("assumido-","")
    mapa = {"alta": ("🔴-ALTA-", 0xff0000), "media": ("🟡-MEDIA-", 0xffff00), "baixa": ("🟢-BAIXA-", 0x00ff00), "critica": ("⚫-CRITICA-", 0x000000)}
    pref, cor = mapa[nivel.value]
    await interaction.channel.edit(name=pref+nome)
    await interaction.response.send_message(embed=discord.Embed(title=f"Prioridade: {nivel.name}", color=cor))

@bot.tree.command(name="assumir", description="Assumir ticket")
async def assumir(interaction: discord.Interaction):
    await interaction.channel.edit(name=f"assumido-{interaction.user.name}-{interaction.channel.name}")
    await interaction.response.send_message(f"✅ Assumido por {interaction.user.mention}")

@bot.tree.command(name="fechar", description="Fechar ticket")
async def fechar(interaction: discord.Interaction):
    await interaction.response.send_message("Fechando em 3s...")
    await asyncio.sleep(3)
    await interaction.channel.delete()

@bot.tree.command(name="ban", description="Banir usuario")
async def ban(interaction: discord.Interaction, usuario: discord.Member, motivo: str="Sem motivo"):
    await usuario.ban(reason=motivo)
    await interaction.response.send_message(f"🔨 {usuario} banido")

@bot.tree.command(name="unban", description="Desbanir por ID")
async def unban(interaction: discord.Interaction, id: str):
    user = await bot.fetch_user(int(id))
    await interaction.guild.unban(user)
    await interaction.response.send_message(f"✅ {user} desbanido")

@bot.tree.command(name="limpar", description="Limpar mensagens")
async def limpar(interaction: discord.Interaction, quantidade: int):
    await interaction.response.defer(ephemeral=True)
    await interaction.channel.purge(limit=quantidade)
    await interaction.followup.send(f"🧹 {quantidade} apagadas", ephemeral=True)

bot.run(os.getenv("TOKEN"))
