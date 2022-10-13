import asyncio
import os

import aiohttp
import dotenv
import hikari
import lightbulb
import miru

dotenv.load_dotenv()

bot = lightbulb.BotApp(
    os.environ["BOT_TOKEN"],
    intents=hikari.Intents.ALL,
    prefix="+",
    banner=None,
)

miru.load(bot)
bot.load_extensions_from("./extensions/")


@bot.listen()
async def on_starting(event: hikari.StartingEvent) -> None:
    bot.d.aio_session = aiohttp.ClientSession()


@bot.listen()
async def on_stopping(event: hikari.StoppingEvent) -> None:
    await bot.d.aio_session.close()


@bot.command
@lightbulb.command("ping", description="The bot's ping.")
@lightbulb.implements(lightbulb.PrefixCommand, lightbulb.SlashCommand)
async def ping(ctx: lightbulb.Context) -> None:
    await ctx.respond(f"Pong! Latency: {bot.heartbeat_latency*1000:.2f}ms.")


@bot.command
@lightbulb.option("ping", "Role to ping with announcement.", type=hikari.Role)
@lightbulb.option(
    "channel", "Channel to post announcement to.", type=hikari.TextableChannel
)
@lightbulb.option("image", "Announcement attachment.", type=hikari.Attachment)
@lightbulb.option("message", "The message to announce.", type=str)
@lightbulb.command("announce", "Make an announcement!", pass_options=True)
@lightbulb.implements(lightbulb.PrefixCommand, lightbulb.SlashCommand)
async def announce(
    ctx: lightbulb.Context,
    message: str,
    image: hikari.Attachment,
    channel: hikari.InteractionChannel,
    ping: hikari.Role,
) -> None:
    embed = hikari.Embed(
        title="Announcement!",
        description=message,
    )
    embed.set_image(image)

    await ctx.bot.rest.create_message(
        content=ping.mention,
        channel=channel.id,
        embed=embed,
        role_mentions=True,
    )

    await ctx.respond(
        f"Announcement posted to <#{channel.id}>!", flags=hikari.MessageFlag.EPHEMERAL
    )


if __name__ == "__main__":
    if os.name == "nt":
        # we are running on a Windows machine, and we have to add this so
        # the code doesn't error :< (it most likely will error without this)
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    bot.run()
