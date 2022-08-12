import asyncio
import os

import dotenv
import hikari

dotenv.load_dotenv()

bot = hikari.GatewayBot(
    os.environ["BOT_TOKEN"],
    intents=hikari.Intents.ALL,
)


@bot.listen()
async def on_message_create(event: hikari.GuildMessageCreateEvent) -> None:
    if not event.is_human or not event.content:
        return

    if event.content.strip() == "+ping":
        await event.message.respond(
            f"Pong! Latency: {bot.heartbeat_latency*1000:.2f}ms"
        )


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
