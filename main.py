import os
from threading import Event, Thread

import discord
from discord.ext import commands
from flask import Flask


TOKEN = (os.getenv("DISCORD_TOKEN") or os.getenv("TOKEN") or "").strip()
if not TOKEN:
    raise RuntimeError("Configure DISCORD_TOKEN or TOKEN in the hosting environment.")

app = Flask(__name__)
bot_ready = Event()


@app.get("/")
def home():
    if bot_ready.is_set():
        return "BOT_ON", 200
    return "BOT_OFFLINE", 503


def run_web():
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", "10000")),
        use_reloader=False,
    )


# Do not let the HTTP thread keep the process alive if the Discord client exits.
Thread(target=run_web, daemon=True).start()


async def criar_ticket(interaction, motivo):
    guild = interaction.guild
    overwrites = {
        guild.default_role: discord.PermissionOverwrite(view_channel=False),
        interaction.user: discord.PermissionOverwrite(
            view_channel=True,
            send_messages=True,
        ),
        guild.me: discord.PermissionOverwrite(view_channel=True),
    }
    nome = f"{motivo.lower().replace(' ', '-')}-{interaction.user.name}"[:90]
    canal = await guild.create_text_channel(name=nome, overwrites=overwrites)
    await canal.send(f"{interaction.user.mention} Ticket: {motivo}")
    await interaction.response.send_message(
        f"Criado: {canal.mention}", ephemeral=True
    )


class HolandaMenu(discord.ui.Select):
    def __init__(self):
        super().__init__(
            placeholder="HOLANDA",
            custom_id="holanda",
            options=[
                discord.SelectOption(label="TRANSFERENCIA"),
                discord.SelectOption(label="DUVIDAS"),
                discord.SelectOption(label="BOOSTS"),
                discord.SelectOption(label="XFAC"),
                discord.SelectOption(label="DENUNCIA"),
                discord.SelectOption(label="ALIANCA/PARCERIA"),
                discord.SelectOption(label="OUTROS"),
            ],
        )

    async def callback(self, interaction):
        await criar_ticket(interaction, self.values[0])


class FacMenu(discord.ui.Select):
    def __init__(self):
        super().__init__(
            placeholder="OPCOES FAC",
            custom_id="fac",
            options=[
                discord.SelectOption(label="PAGAR META"),
                discord.SelectOption(label="SOLICITAR CARGO"),
                discord.SelectOption(label="SETAGEM"),
                discord.SelectOption(label="OUTROS"),
            ],
        )

    async def callback(self, interaction):
        await criar_ticket(interaction, self.values[0])


class PainelView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(HolandaMenu())
        self.add_item(FacMenu())


class HolandaBot(commands.Bot):
    async def setup_hook(self):
        # Re-register persistent menus so existing panels keep working after restarts.
        self.add_view(PainelView())


intents = discord.Intents.default()
# Prefix commands read message text, so only Message Content is additionally needed.
intents.message_content = True
bot = HolandaBot(command_prefix="!", intents=intents)


@bot.command()
async def painelhld(ctx):
    await ctx.send(
        embed=discord.Embed(
            title="HOLANDA | OPCOES FAC",
            description="Escolha no menu",
        ),
        view=PainelView(),
    )


@bot.command()
async def painel3(ctx):
    await painelhld(ctx)


@bot.event
async def on_ready():
    bot_ready.set()
    print(f"BOT ON {bot.user}")


@bot.event
async def on_disconnect():
    bot_ready.clear()


@bot.event
async def on_resumed():
    bot_ready.set()


bot.run(TOKEN)
