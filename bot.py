import os
from typing import Optional

import aiohttp
import dotenv
import hikari
import lightbulb
import miru
from hikari import Intents

dotenv.load_dotenv()

INTENTS = (
    Intents.ALL_MESSAGES
    | Intents.MESSAGE_CONTENT
    | Intents.GUILD_MEMBERS
    | Intents.GUILDS
)

bot = lightbulb.BotApp(
    os.environ["BOT_TOKEN"],
    intents=INTENTS,
    prefix="+",
    banner=None,
    help_class=None,
)

miru.load(bot)  # type: ignore[arg-type]
bot.load_extensions_from("./extensions/")


@bot.listen()
async def on_starting(_: hikari.StartingEvent) -> None:
    bot.d.client_session = aiohttp.ClientSession()


@bot.listen()
async def on_stopping(_: hikari.StoppingEvent) -> None:
    await bot.d.client_session.close()


@bot.command
@lightbulb.command("ping", description="The bot's ping.")
@lightbulb.implements(lightbulb.PrefixCommand, lightbulb.SlashCommand)
async def ping_cmd(ctx: lightbulb.Context) -> None:
    await ctx.respond(f"Pong! Latency: {bot.heartbeat_latency*1000:.2f}ms.")


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
    ctx: lightbulb.Context,
    message: str,
    channel: hikari.GuildTextChannel,
    image: Optional[hikari.Attachment] = None,
    ping: Optional[hikari.Role] = None,
) -> None:
    embed = hikari.Embed(
        title="Announcement!",
        description=message,
    )
    embed.set_image(image)

    await ctx.app.rest.create_message(
        content=ping.mention if ping else hikari.UNDEFINED,
        channel=channel.id,
        embed=embed,
        role_mentions=True,
    )

    await ctx.respond(
        f"Announcement posted to <#{channel.id}>!", flags=hikari.MessageFlag.EPHEMERAL
    )


if __name__ == "__main__":
    bot.run()
