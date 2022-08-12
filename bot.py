import asyncio
import os

import dotenv
import hikari
import lightbulb

dotenv.load_dotenv()

bot = lightbulb.BotApp(
    os.environ["BOT_TOKEN"],
    intents=hikari.Intents.ALL,
    default_enabled_guilds=(765236394577756171,),
    prefix="+",
    banner=None,
)


@bot.command
@lightbulb.command("ping", description="The bot's ping")
@lightbulb.implements(lightbulb.PrefixCommand, lightbulb.SlashCommand)
async def ping(ctx: lightbulb.Context) -> None:
    await ctx.respond(f"Pong! Latency: {bot.heartbeat_latency*1000:.2f}ms")


if __name__ == "__main__":
    if os.name != "nt":
        # we're not running on a Windows machine, so we can use uvloop
        import uvloop

        uvloop.install()
    else:
        # we are running on a Windows machine, and we have to add this so
        # the code doesn't error :< (it most likely will error without this)
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    bot.run()
