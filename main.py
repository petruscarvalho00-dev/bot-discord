import discord
from discord.ext import commands
from flask import Flask
import threading, os, asyncio

app = Flask(__name__)
@app.route('/')
def home(): return "Tropa Holanda ON"
threading.Thread(target=lambda: app.run(host='0.0.0.0', port=int(os.environ.get("PORT",10000)))).start()

intents = discord.Intents.default()
intents.members = True
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# === AQUI É ONDE VOCÊ COLOCA O BANNER QUANDO QUISER ===
# Deixa vazio "" se não quiser banner agora
# Se quiser, cola o link aqui dentro das aspas depois
BANNER_URL = "" 

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
        await canal.send(content=f"{interaction.user.mention} @here", embed=discord.Embed(title=f"🇳🇱 {self.values[0].upper()}", description="Aguarde um superior. Use !fechar para fechar.", color=0xff0000))

class TicketView(discord.ui.View):
    def __init__(self): super().__init__(timeout=None); self.add_item(TicketSelect())

@bot.event
async def on_ready():
    bot.add_view(TicketView())
    print(f"ON {bot.user}")

async def criar_painel(channel):
    embed = discord.Embed(
        title="🇳🇱 ATENDIMENTO - TROPA DA HOLANDA",
        description="**O QUE ACONTECE QUANDO VOCÊ ABRE UM TICKET**\n• Canal privado só seu e da equipe\n• Atendimento rápido e sigiloso\n\n**Clique no menu abaixo e selecione o motivo**",
        color=0x000000
    )
    # Se tiver link no BANNER_URL, ele usa. Se não, manda sem banner e não dá erro
    if BANNER_URL and BANNER_URL.startswith("http"):
        embed.set_image(url=BANNER_URL)
    
    await channel.send(embed=embed, view=TicketView())

@bot.command(name="painel")
async def painel_prefix(ctx):
    await criar_painel(ctx.channel)
    try: await ctx.message.delete()
    except: pass

# Comandos extras
@bot.command(name="fechar")
async def fechar(ctx): await ctx.send("Fechando em 2s..."); await asyncio.sleep(2); await ctx.channel.delete()
@bot.command(name="assumir")
async def assumir(ctx): await ctx.channel.edit(name=f"assumido-{ctx.author.name}-{ctx.channel.name}"); await ctx.send(f"✅ Assumido por {ctx.author.mention}")

bot.run(os.getenv("TOKEN"))
