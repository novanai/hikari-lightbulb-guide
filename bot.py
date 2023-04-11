import os

import aiohttp
import dotenv
import hikari
import lightbulb
import miru
from hikari import Intents

dotenv.load_dotenv()

INTENTS = Intents.GUILD_MEMBERS | Intents.GUILDS

bot = lightbulb.BotApp(
    os.environ["BOT_TOKEN"],
    intents=INTENTS,
    banner=None,
)

miru.install(bot)  # type: ignore[arg-type]
bot.load_extensions_from("./extensions/")


@bot.listen()
async def on_starting(event: hikari.StartingEvent) -> None:
    bot.d.client_session = aiohttp.ClientSession()


@bot.listen()
async def on_stopping(event: hikari.StoppingEvent) -> None:
    await bot.d.client_session.close()


@bot.command
@lightbulb.command("ping", "The bot's ping.")
@lightbulb.implements(lightbulb.SlashCommand)
async def ping(ctx: lightbulb.SlashContext) -> None:
    await ctx.respond(f"Pong! Latency: {bot.heartbeat_latency * 1000:.2f}ms.")


@bot.command
@lightbulb.option(
    "ping", "Role to ping with announcement.", type=hikari.Role, required=False
)
@lightbulb.option(
    "image", "Announcement attachment.", type=hikari.Attachment, required=False
)
@lightbulb.option(
    "channel", "Channel to post announcement to.", type=hikari.TextableChannel
)
@lightbulb.option("message", "The message to announce.", type=str)
@lightbulb.command("announce", "Make an announcement!", pass_options=True)
@lightbulb.implements(lightbulb.SlashCommand)
async def announce(
    ctx: lightbulb.SlashContext,
    message: str,
    channel: hikari.GuildTextChannel,
    image: hikari.Attachment | None,
    ping: hikari.Role | None,
) -> None:
    embed = hikari.Embed(
        title="Announcement!",
        description=message,
    )
    embed.set_image(image)

    await ctx.app.rest.create_message(
        channel=channel.id,
        content=ping.mention if ping else hikari.UNDEFINED,
        embed=embed,
        role_mentions=True,
    )

    await ctx.respond(
        f"Announcement posted to <#{channel.id}>!", flags=hikari.MessageFlag.EPHEMERAL
    )


if __name__ == "__main__":
    bot.run()
