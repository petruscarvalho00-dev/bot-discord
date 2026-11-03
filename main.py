import discord
from discord.ext import commands
import io, datetime, os
from flask import Flask
from threading import Thread

# --- KEEP ALIVE PRA RENDER FICAR ON 24/7 ---
app = Flask('')

@app.route('/')
def home():
    return "BOT HOLANDA ON 24/7 🇳🇱"

def run():
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))

def keep_alive():
    t = Thread(target=run)
    t.start()

# --- BOT ---
intents = discord.Intents.default()
intents.message_content = True
intents.messages = True
bot = commands.Bot(command_prefix="!", intents=intents)

CONFIG_CATEGORIAS = {
    "TRANSFERÊNCIA": None,
    "DUVIDAS": None,
    "BOOSTS": None,
    "XFAC": None,
    "DENUNCIA": None,
    "ALIANÇA/PARCERIA": None,
    "OUTROS": None,
    "PAGAR META": None,
    "SOLICITAR CARGO": None,
    "SETAGEM": None,
}
ID_CANAL_LOGS = None

async def criar_transcript(channel):
    messages = [msg async for msg in channel.history(limit=500, oldest_first=True)]
    transcript = f"Transcript {channel.name}\n\n"
    for m in messages:
        transcript += f"[{m.created_at.strftime('%d/%m %H:%M')}] {m.author}: {m.content}\n"
    return transcript

async def criar_ticket(interaction, motivo):
    guild = interaction.guild
    for c in guild.text_channels:
        if f"-{interaction.user.name.lower()}" in c.name.lower() and c.overwrites_for(interaction.user).view_channel:
            return await interaction.response.send_message(f"❌ Já tem ticket: {c.mention}", ephemeral=True)

    cat_id = CONFIG_CATEGORIAS.get(motivo)
    categoria = guild.get_channel(cat_id) if cat_id else None
    overwrites = {
        guild.default_role: discord.PermissionOverwrite(view_channel=False),
        interaction.user: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True),
        guild.me: discord.PermissionOverwrite(view_channel=True)
    }
    nome = f"{motivo.lower().replace('/','-').replace(' ','-')}-{interaction.user.name}"[:90]
    canal = await guild.create_text_channel(name=nome.lower(), category=categoria, overwrites=overwrites, topic=str(interaction.user.id))

    class FecharView(discord.ui.View):
        def __init__(self): super().__init__(timeout=None)
        @discord.ui.button(label="Fechar Ticket", style=discord.ButtonStyle.red, emoji="🔒")
        async def fechar(self, inter, btn):
            await inter.response.defer()
            txt = await criar_transcript(inter.channel)
            file = discord.File(io.StringIO(txt), filename=f"transcript-{inter.channel.name}.txt")
            if ID_CANAL_LOGS:
                log_canal = guild.get_channel(ID_CANAL_LOGS)
                if log_canal:
                    embed = discord.Embed(title="🔒 Ticket Fechado", color=0xFF0000)
                    embed.add_field(name="Canal", value=inter.channel.name)
                    embed.add_field(name="Fechado por", value=f"{inter.user.mention}")
                    await log_canal.send(embed=embed, file=file)
            await inter.channel.delete()

    embed_ticket = discord.Embed(title=f"🇳🇱 {motivo}", description=f"{interaction.user.mention} abriu", color=0xFF5500)
    await canal.send(embed=embed_ticket, view=FecharView())
    await interaction.response.send_message(f"✅ {canal.mention}", ephemeral=True)

    if ID_CANAL_LOGS:
        log_canal = guild.get_channel(ID_CANAL_LOGS)
        if log_canal:
            await log_canal.send(embed=discord.Embed(title="📩 Ticket Aberto", description=f"{interaction.user.mention} - {motivo} - {canal.mention}", color=0x00FF00))

class MenuHolanda(discord.ui.Select):
    def __init__(self):
        super().__init__(placeholder="
       
